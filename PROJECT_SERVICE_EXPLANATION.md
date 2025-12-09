# Prompt-Engine Project Service Explanation

## Overview

Business-ready financial analysis traverses a data-first pipeline that protects sensitive data, boosts prompts with context, augments them via vectors/LLMs, validates output, and exposes telemetry. Data enters through the UI (or API) and flows through a linked chain of services that each own a slice of the intelligence, staging, or observability work.

The core pipeline is:

1. **PII safety** → `pseudonymization-service`
2. **Prompt generation** → `prompt-engine` (optionally enriched via PAM + Qdrant)
3. **Autonomous analysis** → `autonomous-agent` (RAG + Ollama + validation)
4. **Blocking validation** → `validation-llm`
5. **Learning + persistence** → vector database + feedback hooks
6. **Optional re-identification** → `repersonalization-service`
7. **Visualization** → `pipeline-visualizer`

Each service uses purpose-built Python or JavaScript stacks listed below.

---

## Services and Responsibilities

### 1. Pseudonymization Service (`pseudonymization-service`)

- **Purpose:** Sanitizes incoming transactional/customer data so downstream components never process raw PII. It obfuscates identifiers with HMAC-SHA256, adds deterministic noise to amounts (`±10%`), shifts dates (`±30 days`), and maps free-text descriptions to category tokens before handing the payload along.
- **Tech stack:** FastAPI app (auto docs), `cryptography` for HMAC, `flask-cors`/`requests` for internal calls, optionally `redis` for pseudonym cache. Keys live in the `keys/` directory and are rotated via `/key/rotate` (per README warnings).
- **Internal flow when data arrives:** The FastAPI endpoint verifies JSON, runs `core.pseudonymizer` to transform each field, stores a `pseudonym_id`, and streams the sanitized copy plus metadata back. Bulk endpoints iterate the same logic, allowing large batches to reuse deterministic transformations.
- **Links:** Downstream services (prompt engine, PAM, autonomous agent) take the pseudonymized payload to generate prompts/analysis. When original data is needed later, the `pseudonym_id` is sent to the Repersonalization Service.

### 2. Repersonalization Service (`repersonalization-service`)

- **Purpose:** Restores original data for auditing or final delivery when the system needs to show true values (e.g., after validation or reports). It validates integrity and maintains audit logs of each restoration.
- **Tech stack:** FastAPI + shared `cryptography` keys + optional `redis`. Aligns with pseudonym service through shared `keys/` volume or explicit copy.
- **Internal flow:** `/repersonalize` accepts a `pseudonym_id`, fetches the stored mapping (via shared key material), verifies the fields, and responds with the original payload plus verification metadata. Bulk and cleanup endpoints allow batch restores or GDPR-friendly deletion.
- **Links:** Receives identifiers emitted by the pseudonym service; the UI or reporting layer can call this service once analysis is complete and it’s safe to reveal original values.

### 3. Prompt Engine (`app/` + `server.py`)

- **Purpose:** Takes sanitized transactional data, infers context, and builds structured prompts that guide the autonomous agent and RAG pipeline.
- **Tech stack:** Flask + `flask-cors` serving `/generate`, `/learn`, `/health`, `/system/*` endpoints. Dependencies include `requests`, `sentence-transformers`, `torch`, `qdrant-client`, `numpy`, `scikit-learn`, `pandas`, `jsonschema`, `aiohttp`, `asyncio-throttle`, and `pydantic` for structured metadata.
- **Internal flow when `/generate` receives `input_data`:**
  1. Parses JSON and hands the data to `AgenticPromptGenerator`.
  2. The generator infers context/data type, optionally calls the PAM service for company/market intelligence, checks the quality-improvement manager, and consults the vector service (via `VectorService`).
  3. `VectorService` uses `sentence-transformers` (falling back to hash embeddings if unavailable) and Qdrant collections (`agentic_prompts`, `successful_patterns`, `data_insights`) to find cached prompts or store new ones.
  4. The generator renders templates from `app.templates`, applies agentic enhancements (analysis, reasoning steps, structured output requirements), then returns the prompt + metadata (vector/quality indicators).
  5. `/generate` reports processing time, vector usage, and status; `/learn` later accepts interactions for quality-aware self-learning and vector persistence.
- **Links:** Prompt output is fetched by `autonomous-agent` via `/analyze` (returns call to Prompt Engine’s `/generate`/`agentic`). The metadata helps the agent decide between fast cached responses or newly structured prompts.

### 4. PAM (Prompt Augmentation Model) Service (`pam-service`)

- **Purpose:** Enriches prompts with company/market signals (scraped data + distilled LLM intelligence) before the agent runs the multi-step reasoning pipeline.
- **Tech stack:** Flask + `flask-cors` + `beautifulsoup4`/`lxml` for scraping, `requests` for upstream/downstream calls, `sentence-transformers`/`qdrant-client` for caching, `numpy` for numeric summaries, `python-dotenv`.
- **Internal flow:** `/augment` accepts `input_data`+optional companies/context → extracts companies (via `core.company_extractor`), triggers the web scraper, optionally runs Ollama research (client in `core.llm_researcher`), caches augmented prompts/payloads in Qdrant (`qdrant_cache`) for `cache_hit` acceleration, and returns augmented prompt + stats.
- **Links:** The Prompt Engine conditionally calls PAM during prompt creation (`AgenticPromptGenerator._augment_with_pam`). The augmented prompt (with historical context) flows into the autonomous agent for RAG enrichment.

### 5. Vector Database (Qdrant)

- **Purpose:** Stores embeddings for prompts/patterns to accelerate prompt generation, retrieve successful templates, and persist self-learning artifacts.
- **Usage:** Both `VectorService` and PAM service rely on Qdrant on port 6333. Collections include `agentic_prompts`, `successful_patterns`, `data_insights`, plus metadata-driven collections (e.g., `financial_knowledge_base` from README).
- **Flow:** When a prompt is generated or a validation-approved response arrives, `VectorService.store_successful_prompt` creates embedding (`SentenceTransformer('all-MiniLM-L6-v2')` or hash fallback) and upserts the point into Qdrant. Later queries (`find_similar_prompts`, `get_optimization_cache`) use cosine similarity to seed new prompts.

### 6. Autonomous Agent (`autonomous-agent/server_final.py`)

- **Purpose:** Orchestrates the complete RAG-enhanced financial analysis, combining prompt generation, vector retrieval, multi-step reasoning, LLM inference, and blocking validation before delivering results.
- **Tech stack:** Flask + `flask-cors`, `requests`, `numpy`, `scipy`, `scikit-learn`, `sentence-transformers`, `torch`, `qdrant-client`, plus asynchronous support (`aiohttp`, `asyncio-throttle`). Core logic lives under `autonomous-agent/core/` (RAG service, prompt consumer, validation integration, response formatter).

- **Internal flow (triggered via `/analyze` or `/pipeline/*`):**
  1. Receive sanitized `input_data`.
  2. Call Prompt Engine (via `PromptConsumerService`) to get a structured prompt (standard or agentic).
  3. Pass prompt and data to `RAGService`, which consults Qdrant and Ollama. Qdrant returns relevant context, Ollama produces the natural language `analysis`.
  4. Format the response (two-section insights/recommendations) using `ResponseFormatter`.
  5. Send the candidate response to the validation service (`ValidationIntegrationService.validate_and_gate_response`), which enforces blocking quality gates (criteria, scoring thresholds) before the response can leave this service.
  6. Record stats/interaction history,  send validation feedback back to this service or stored vector database for learning.


### 7. Validation System (`validation-llm`)

- **Purpose:** Acts as blocking quality gate for every analysis response. It evaluates `analysis` text against the original `input_data` using secondary LLMs and multi-criteria heuristics and either approves or rejects before it reaches the user.
- **Tech stack:** Flask[async] + `flask-cors`, `requests`, `qdrant-client`, `numpy`, `pandas`, `python-dateutil`, optional `pytest` for testing. Although PyTorch is excluded for Python 3.13 compatibility, the service can still work with Ollama responses.
- **Internal flow:** Receives candidate responses via `/validate/response`, runs accuracy/completeness/relevance/clarity checks (possibly via Ollama), calculates a score (0–100), applies configurable thresholds (`autonomous-agent/core/validation_integration.py` defines gates), and returns a `validation` object. Approved responses include a `quality_level`; failed ones return metadata explaining the rejection. When validation results are acceptable, they are fed back via `/feedback/validation`.
- **Links:** Autonomous agent always calls this service before replying to the user (blocking validation). High-quality outputs may also be written back into the vector database for future prompt generation.

### 8. LLM Service (Ollama)

- **Purpose:** Hosts local LLM inference for both analysis and validation. Recommended models include `mistral:latest`, `llama3.1:8b`, `phi3:3.8b`, depending on workload (validation vs. analysis vs. prompting).
- **Integration:** Every service (Prompt Engine, Autonomous Agent, PAM, Validation) constructs HTTP requests against `http://localhost:11434` to list models, generate completions, and verify health.
- **Links:** This container is the ultimate text generator; Qdrant and prompt metadata guide it, but Ollama is where the language comes from.

### 9. Pipeline Visualizer (`pipeline-visualizer`)

- **Purpose:** React/Vite front end that displays the health and execution status of all pipeline steps.
- **Tech stack:** React 18, Vite, React Flow (flow diagrams), Recharts (metrics), Framer Motion (animations), Axios (API calls), Tailwind CSS, Lucide icons.
- **Internal flow:** Pulls `VITE_*` endpoints from `.env`, polls each backend (pseudonymization, prompt engine, autonomous agent, validation, PAM, Qdrant, Ollama), and renders status cards, diagrams, and execution timelines. Execution view lets users edit JSON input and sequentially call the backend APIs (pseudonymize → prompt → RAG → validation).
- **Links:** Relies on all backend URLs being reachable; the `.env` template points to production proxies (Caddy) but can be overridden for local dev (`start_all_services.sh` to spin everything up).

### 10. Supporting Data Tools (`data/`)

- **Purpose:** Scripts such as `data/data-script.py` and generated datasets under `data/generated_data/`/`data/dump/` produce synthetic transactions with embedded context. They seed tests, demonstrations, and pipelines.
- **Flow:** Data scripts feed the pseudonymization service or prompt engine with structured sample input, ensuring repeatable scenarios for QA/testing.

---

## End-to-End Data Journey

1. **Input acquisition:** User submits transaction list or JSON via the UI (`server.py` in root or the visualizer execution view). Before anything else, data can be routed through `pseudonymization-service` to mask PII; the returned data + `pseudonym_id` flows to the prompt engine.
2. **Prompt generation:** The Prompt Engine infers context, optionally enriches the base prompt with PAM, consults Qdrant (via `VectorService`) for cached prompts, and emits a structured prompt.
3. **Autonomous analysis:** The Autonomous Agent consumes that prompt, augments it with RAG context (Qdrant + Ollama), generates the analysis, formats it, and hands the candidate response to the validation system.
4. **Blocking validation:** The Validation service scores the response; if it passes (`quality_level` ≥ configured gate), it returns approved metadata. If not, the agent either retries or reports the failure while still respecting blocking semantics.
5. **Learning loop:** Approved prompt/response pairs are stored in Qdrant (`VectorService.store_successful_prompt`) and fed into the self-learning manager so future prompts automatically capture quality signals.
6. **Repersonalization (if needed):** If the final output or audit requires original data, the `pseudonym_id` is sent to `repersonalization-service`, which reverses the obfuscation and responds with the original dataset.
7. **Visualization + monitoring:** Throughout, `pipeline-visualizer` polls each service, displays health/status, and lets operators rerun the pipeline with any data sample.

This explanation should help operators understand what each service contributes, which libraries it relies on, and how sanitized data travels end-to-end from capture to validated, learnable insights.

