# PAM (Prompt Augmentation Model) Service

The PAM Service enriches prompts with real-time company and market intelligence by scraping web data and using LLM-based research.

## Features

- 🏢 **Company Extraction**: Automatically identifies companies from transaction data
- 🌐 **Web Scraping**: Gathers company information from web sources
- 🤖 **LLM Research**: Uses Ollama to synthesize insights
- 💾 **Vector Caching**: Stores augmented data in Qdrant for fast retrieval
- ⚡ **High Performance**: Caching reduces latency by up to 87%

## Architecture

PAM integrates into the prompt generation pipeline:

```
Input Data → Pseudonymization → PAM Augmentation → Generate Embeddings → Vector Search
```

## Installation

### Local Setup

1. Create virtual environment:
```bash
cd pam-service
python3 -m venv pam
source pam/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure dependencies are running:
   - Qdrant (port 6333)
   - Ollama (port 11434)

4. Start the service:
```bash
python3 run_service.py
```

The service will be available at `http://localhost:5005`

### Docker Setup

```bash
cd pam-service
docker-compose up -d
```

## Configuration

Environment variables (see `app/config.py`):

- `PAM_HOST`: Host to bind to (default: 0.0.0.0)
- `PAM_PORT`: Port to run on (default: 5005)
- `QDRANT_HOST`: Qdrant server host (default: localhost)
- `QDRANT_PORT`: Qdrant server port (default: 6333)
- `OLLAMA_HOST`: Ollama server host (default: localhost)
- `OLLAMA_PORT`: Ollama server port (default: 11434)
- `OLLAMA_MODEL`: LLM model to use (default: llama3)
- `PAM_ENABLE_SCRAPING`: Enable web scraping (default: true)
- `PAM_ENABLE_LLM`: Enable LLM research (default: true)
- `PAM_ENABLE_CACHING`: Enable Qdrant caching (default: true)
- `PAM_CACHE_TTL_HOURS`: Cache TTL in hours (default: 24)

## API Endpoints

### POST /augment

Augment a prompt with company and market intelligence.

**Request:**
```json
{
  "input_data": {
    "transactions": [...],
    "customer_id": "BIZ_0001"
  },
  "prompt_text": "Analyze transaction patterns...",
  "companies": ["TechCorp Inc"],  // Optional override
  "context": "core_banking"       // Optional context
}
```

**Response:**
```json
{
  "augmented_prompt": "...[original]...\n\n## Company Context\n...",
  "companies_analyzed": ["TechCorp Inc", "Global Logistics"],
  "augmentation_summary": {
    "company_count": 2,
    "companies": [...]
  },
  "cache_hit": false,
  "processing_time_ms": 1250
}
```

### POST /augment/bulk

Batch augmentation for multiple requests.

### GET /health

Health check endpoint.

### GET /stats

Service statistics including cache hit rate.

### POST /cleanup

Clean up expired cache entries.

## Integration with Prompt Engine

The PAM service is automatically called by the Prompt Engine when enabled.

In `config.py`:
```python
PAM_HOST = 'localhost'
PAM_PORT = 5005
ENABLE_PAM_AUGMENTATION = True
```

The `AgenticPromptGenerator` will:
1. Extract companies from input data
2. Call PAM service to augment
3. Use augmented prompt for generation

## Testing

Run tests:
```bash
python3 test_pam_service.py
```

Tests include:
- Company extraction
- Web scraping
- API health check
- Full augmentation request

## Performance

- **Cache Hit**: ~50ms (87% faster)
- **Cache Miss**: ~1.5s (web scraping + LLM)
- **Cache TTL**: 24 hours (configurable)

## Troubleshooting

### Service won't start

- Check Qdrant is running: `docker ps | grep qdrant`
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Check port 5005 is free: `lsof -ti :5005`

### Web scraping fails

- Check internet connectivity
- Some sites may block automated requests
- Rate limiting is enforced (1 req/sec)

### Cache not working

- Verify Qdrant connection in health check
- Check Qdrant collection exists: `curl http://localhost:6333/collections`

## Development

Project structure:
```
pam-service/
├── app/
│   ├── core/
│   │   ├── company_extractor.py    # Extract companies from data
│   │   ├── web_scraper.py          # Web scraping logic
│   │   ├── llm_researcher.py       # LLM-based research
│   │   ├── qdrant_cache.py         # Vector caching
│   │   └── augmentation_engine.py  # Main orchestrator
│   ├── config.py                   # Configuration
│   └── main.py                     # Flask API
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## License

Part of the Prompt Engine project.

