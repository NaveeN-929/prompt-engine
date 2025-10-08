# 🧪 Testing Guide

## Quick Start

### Run Comprehensive System Test
```bash
python test_system_comprehensive.py
```

This will test all services and generate a detailed report.

## What Gets Tested

### ✅ Service Connectivity
- Prompt Engine (Port 5000)
- Autonomous Agent (Port 5001)
- Validation System (Port 5002)
- Ollama LLM (Port 11434)
- Qdrant Vector DB (Port 6333)

### ✅ Functionality Tests
- **Prompt Generation**: Test prompt creation with sample data
- **Analysis Processing**: Full autonomous analysis workflow with integrated validation
- **Validation System**: Health check (full validation tested in autonomous agent)
- **Ollama Models**: Verify models are loaded (response tested in other components)
- **Vector Operations**: Qdrant database connectivity

### ✅ End-to-End Workflow
- Complete analysis pipeline from input to validated output
- Performance metrics and timing
- Validation score assessment

## Expected Results

### 🎯 Success Criteria
- All services respond within timeout limits
- Validation scores > 0% (not stuck at 0.0%)
- End-to-end processing < 60 seconds
- No connection errors

### 📊 Performance Benchmarks
- **Prompt Generation**: 1-3 seconds
- **Analysis Processing**: 10-30 seconds  
- **Validation**: 2-5 seconds
- **Total Workflow**: 15-40 seconds

## Troubleshooting

### Common Issues

**❌ Service Connection Refused**
```bash
# Check if services are running
curl http://localhost:5000/health
curl http://localhost:5001/agent/status
curl http://localhost:5002/health
```

**❌ Validation Timeout**
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Verify models are available: `ollama list`
- Check system resources

**❌ Low Validation Scores**
- Review validation configuration
- Check LLM model responses
- Verify input data quality

### Manual Service Checks

```bash
# Start services if needed
cd autonomous-agent && python server_final.py &
cd validation-llm && python validation_server.py &
python server.py &
```

## Test Report

The test generates `system_test_report.md` with:
- Service status summary
- Performance metrics
- Validation results
- Recommendations for improvements

## Integration Testing

For development and CI/CD:
```bash
# Run tests in CI environment
python test_system_comprehensive.py --ci-mode

# Generate JSON report
python test_system_comprehensive.py --json-report
```

---

**Last Updated**: 2024-01-15  
**Test Coverage**: All major system components ✅
