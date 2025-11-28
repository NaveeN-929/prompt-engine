# PAM Service Integration Guide

## Overview

The PAM (Prompt Augmentation Model) service has been successfully integrated into the prompt-engine pipeline. This guide explains how to use and verify the integration.

## Architecture Flow

```
┌─────────────┐
│ Input Data  │
│ (Trans.)    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Pseudonymization│
└──────┬──────────┘
       │
       ▼
┌─────────────────┐    ┌──────────────────┐
│ PAM Augmentation│◄───│ PAM Service      │
│ (NEW)           │    │ (Port 5005)      │
└──────┬──────────┘    └──────────────────┘
       │                       │
       │                   ┌───┴───┐
       │                   │       │
       │              ┌────▼─┐  ┌──▼───┐
       │              │ Web  │  │ LLM  │
       │              │ Scr. │  │ Res. │
       │              └────┬─┘  └──┬───┘
       │                   │       │
       │              ┌────▼───────▼──┐
       │              │ Qdrant Cache  │
       │              └───────────────┘
       ▼
┌─────────────────┐
│ Create Signature│
│ (tx_count=5)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Generate Vector │
│ Embedding       │
│ (384-dim)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Search Vector DB│
│ Similarity≥0.75 │
└──────┬──────────┘
       │
   ┌───┴────┐
   │        │
 FOUND   NOT FOUND
   │        │
   ▼        ▼
 REUSE   GENERATE
```

## Quick Start

### 1. Start Services

```bash
# Start all services (includes PAM)
./start_all_services.sh
```

This will start:
1. Qdrant (Docker) - Vector database
2. PAM Service (Port 5005) - Prompt augmentation
3. Prompt Engine (Port 5000) - Prompt generation
4. Validation Service (Port 5002) - Quality gates
5. Autonomous Agent (Port 5001) - RAG analysis

### 2. Verify PAM Service

```bash
# Check health
curl http://localhost:5005/health

# Check statistics
curl http://localhost:5005/stats
```

### 3. Test PAM Augmentation

```bash
cd pam-service
source pam/bin/activate
python3 test_pam_service.py
```

### 4. Test End-to-End Pipeline

```python
import requests

# Sample transaction data
data = {
    "input_data": {
        "customer_id": "BIZ_0001",
        "transactions": [
            {
                "date": "2025-11-01",
                "amount": 5000.00,
                "description": "Payment from Microsoft for services"
            }
        ]
    },
    "generation_type": "standard"
}

# Call prompt engine (PAM is automatically used)
response = requests.post(
    "http://localhost:5000/generate",
    json=data
)

result = response.json()
print(f"PAM Companies: {result['metadata'].get('companies_analyzed', [])}")
print(f"PAM Cache Hit: {result['metadata'].get('pam_cache_hit', False)}")
```

## Configuration

### Enable/Disable PAM

In `config.py`:
```python
# Enable PAM augmentation
ENABLE_PAM_AUGMENTATION = True

# PAM service location
PAM_HOST = 'localhost'
PAM_PORT = 5005
```

### PAM Service Configuration

In `pam-service/app/config.py`:
```python
# Feature flags
ENABLE_WEB_SCRAPING = True    # Web scraping for company info
ENABLE_LLM_RESEARCH = True    # LLM-based synthesis
ENABLE_CACHING = True         # Qdrant vector caching

# Caching
CACHE_TTL_HOURS = 24          # Cache expiry
SIMILARITY_THRESHOLD = 0.85   # Cache similarity threshold
```

## Integration Points

### 1. Prompt Engine Integration

File: `app/generators/agentic_prompt_generator.py`

The `AgenticPromptGenerator` class now includes:
- `enable_pam` parameter in `__init__()`
- `_augment_with_pam()` method for augmentation
- PAM augmentation called at the start of `generate_agentic_prompt()`

### 2. Metadata Enhancement

All generated prompts now include PAM metadata:
```json
{
  "pam_enabled": true,
  "companies_analyzed": ["Microsoft", "Google"],
  "pam_cache_hit": false,
  "pam_processing_time_ms": 1250,
  "augmentation_summary": {
    "company_count": 2,
    "companies": [...]
  }
}
```

### 3. Docker Integration

The `docker-compose.yml` now includes:
- PAM service container
- Dependencies on Qdrant and Ollama
- Environment variable configuration

### 4. Service Management

- `start_all_services.sh` - Starts PAM as step 0
- `stop_all_services.sh` - Stops PAM service

## Performance Metrics

### With Caching

- **Cache Hit**: ~50-100ms
- **Cache Miss (first request)**: ~1-2s
- **Cache Hit Rate**: Typically 40-60% after warmup

### Without Caching

- **Web Scraping**: ~500-800ms per company
- **LLM Research**: ~300-500ms per synthesis
- **Total**: ~1.5-2.5s for 2-3 companies

## Monitoring

### Health Checks

```bash
# PAM Service
curl http://localhost:5005/health

# Prompt Engine (includes PAM status)
curl http://localhost:5000/status
```

### Statistics

```bash
# PAM statistics
curl http://localhost:5005/stats

# Response includes:
# - cache_hits, cache_misses
# - companies_analyzed
# - web_scrapes, llm_calls
```

### Logs

PAM service logs include:
- ✨ PAM augmentation success
- ⚠️ PAM service timeout/error
- 🔍 Company extraction
- 💾 Cache hits/misses

## Troubleshooting

### PAM Service Won't Start

```bash
# Check dependencies
docker ps | grep qdrant    # Should show qdrant running
curl http://localhost:11434/api/tags  # Should return Ollama models

# Check port
lsof -ti :5005  # Should be empty if port is free

# Check logs
cd pam-service
python3 run_service.py  # See detailed logs
```

### Prompt Engine Can't Reach PAM

```bash
# Verify PAM is running
curl http://localhost:5005/health

# Check config
grep PAM config.py

# Test connectivity
curl -X POST http://localhost:5005/augment \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"transactions": []}}'
```

### PAM Augmentation Fails

The system gracefully degrades:
- If PAM is unavailable, prompts are generated without augmentation
- Timeout is 10 seconds
- Errors are logged but don't block prompt generation

## Best Practices

1. **Cache Warmup**: Run common queries after startup to populate cache
2. **Monitor Stats**: Check cache hit rate regularly
3. **Cleanup**: Run periodic cache cleanup for expired entries
4. **Rate Limiting**: Web scraping respects rate limits (1 req/sec)
5. **Graceful Degradation**: PAM failures don't break the pipeline

## API Examples

### Direct PAM Call

```bash
curl -X POST http://localhost:5005/augment \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "customer_id": "BIZ_0001",
      "transactions": [
        {
          "description": "Payment from Microsoft"
        }
      ]
    },
    "prompt_text": "Analyze transactions",
    "context": "core_banking"
  }'
```

### Bulk Augmentation

```bash
curl -X POST http://localhost:5005/augment/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"input_data": {...}},
      {"input_data": {...}}
    ]
  }'
```

### Cache Cleanup

```bash
curl -X POST http://localhost:5005/cleanup
```

## What's Next

- **Monitoring Dashboard**: Add metrics visualization
- **Advanced Scraping**: Support more data sources
- **LLM Optimization**: Fine-tune prompts for better insights
- **Caching Strategy**: Implement smart pre-fetching

## Support

For issues or questions:
1. Check logs in the PAM service terminal
2. Verify all dependencies are running
3. Review this integration guide
4. Check the main README.md

## Files Modified

- `config.py` - Added PAM configuration
- `app/generators/agentic_prompt_generator.py` - PAM integration
- `docker-compose.yml` - PAM service container
- `start_all_services.sh` - PAM startup
- `stop_all_services.sh` - PAM shutdown

## Files Created

- `pam-service/` - Complete PAM service implementation
- `pam-service/app/core/` - Core modules
- `pam-service/Dockerfile` - Container definition
- `pam-service/README.md` - Service documentation
- `pam-service/test_pam_service.py` - Unit tests

