# PAM Service - Pipeline Visualizer Integration

## Overview

The PAM (Prompt Augmentation Model) service has been successfully integrated into the pipeline visualizer. The service now appears in the pipeline flow and can be monitored through the web UI.

## Changes Made

### 1. Pipeline Configuration (`src/utils/pipelineConfig.js`)

#### Added PAM Step

```javascript
{
  id: 'pam-service',
  name: 'PAM (Prompt Augmentation)',
  description: 'Company intelligence & market research',
  icon: 'Search',
  type: 'process',
  color: '#14B8A6',
  position: { x: 100, y: 225 },
  port: 5005,
  endpoint: 'http://localhost:5005',
  healthCheck: '/health',
  apiPath: '/augment',
  features: [
    'Company Extraction',
    'Web Scraping',
    'LLM Research',
    'Vector Caching (Qdrant)'
  ],
  metrics: ['companies_analyzed', 'pam_cache_hit', 'pam_processing_time_ms'],
  dependencies: {
    qdrant: { ... },
    ollama: { ... }
  }
}
```

#### Added PAM Service Configuration

```javascript
PAM: {
  name: 'PAM Service',
  port: 5005,
  url: 'http://localhost:5005',
  healthEndpoint: '/health',
  description: 'Prompt Augmentation Model - Company Intelligence & Market Research',
  critical: false // Optional service for enhancement
}
```

#### Updated Pipeline Flow

```
Input Data
    ↓
Pseudonymization
    ↓
PAM Augmentation  ← NEW STEP
    ↓
    ├─→ Autonomous Agent ┐
    │                     ├─→ Validation System
    └─→ Prompt Engine    ┘
           ↓
      Repersonalization
           ↓
      Output Data
```

### 2. API Service (`src/services/apiService.js`)

#### Added PAM API Methods

```javascript
export const pamService = {
  async augment(inputData, options = {}) { ... },
  async augmentBulk(requests) { ... },
  async getStats() { ... },
  async cleanup() { ... }
};
```

#### Updated Pipeline Execution

The pipeline execution now includes PAM as step 2.5:

1. Input Data
2. Pseudonymization
3. **PAM Augmentation** (NEW - optional)
4. Parallel: Autonomous Agent + Prompt Engine
5. Validation System
6. Self-Learning (feedback loop)
7. Repersonalization
8. Output Data

**Key Features:**
- PAM is **optional** - pipeline continues if PAM is unavailable
- PAM-augmented data is passed to both Agent and Prompt Engine
- Failures are logged as warnings, not errors

### 3. Updated Prompt Engine Metadata

The Prompt Engine step now shows:
- PAM Integration enabled
- `pam_enabled` in metrics
- `usesPAM: true` flag

## Visualizer Features

### Service Health Monitoring

The health check system now monitors:
- ✅ PAM Service status (port 5005)
- ✅ PAM dependencies (Qdrant, Ollama)
- ✅ Cache hit rates
- ⚠️  Graceful degradation if unavailable

### Pipeline Flow Visualization

The flow diagram shows:
- PAM as a distinct step after Pseudonymization
- Connections to both downstream services
- Color-coded status (teal: #14B8A6)
- Dependencies visualization

### Metrics Display

PAM metrics shown in the dashboard:
- `companies_analyzed` - Number of companies extracted
- `pam_cache_hit` - Whether cache was used
- `pam_processing_time_ms` - Processing time
- Company intelligence summary

### Step Details

Clicking on the PAM step shows:
- Feature list
- Real-time status
- Dependencies (Qdrant, Ollama)
- Processing metrics
- Error information (if any)

## How to Use

### 1. Start the Visualizer

```bash
cd pipeline-visualizer
npm install  # If first time
npm run dev
```

The visualizer will be available at `http://localhost:5173`

### 2. Verify PAM Integration

1. Open the visualizer
2. Check the **Services** tab - PAM should show port 5005
3. View **Flow Diagram** - PAM should appear between Pseudonymization and downstream services
4. Check **Health Status** - All services should be green

### 3. Execute Pipeline

1. Click "Execute Pipeline" or use the test data
2. Watch the step-by-step execution
3. PAM step should show:
   - Processing status
   - Companies analyzed
   - Cache hit/miss
   - Processing time

### 4. View PAM Metrics

In the Metrics Dashboard:
- PAM processing time graph
- Cache hit rate percentage
- Companies analyzed per request
- PAM availability status

## Error Handling

### PAM Service Unavailable

If PAM service is not running:
- ⚠️  Step shows "warning" status
- Message: "PAM service unavailable, continuing without augmentation"
- Pipeline continues normally
- No critical failure

### PAM Timeout

If PAM takes too long (>30s):
- Request times out gracefully
- Warning logged
- Pipeline continues with unaugmented data

### Partial Failures

If web scraping fails but LLM works:
- PAM returns partial augmentation
- Metrics show what succeeded
- Pipeline continues

## Testing

### Test PAM Integration

```javascript
// In browser console on visualizer page
const testData = {
  customer_id: "BIZ_0001",
  transactions: [
    {
      description: "Payment from Microsoft"
    }
  ]
};

// Execute pipeline
await pipelineExecutionService.executeFullPipeline(testData);
```

### Check PAM Health

```javascript
// Check PAM service health
await healthCheckService.checkService('PAM');
```

### View PAM Stats

```javascript
// Get PAM statistics
await pamService.getStats();
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Pipeline Visualizer                    │
│                   (React + Vite)                         │
│                   Port: 5173                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTP Requests
                     │
    ┌────────────────┼────────────────┬────────────────┐
    │                │                │                │
    ▼                ▼                ▼                ▼
┌────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│Pseudo  │────▶│   PAM   │────▶│ Prompt  │────▶│Validate │
│Port    │     │  Port   │     │ Engine  │     │ Port    │
│5003    │     │  5005   │     │  5000   │     │  5002   │
└────────┘     └────┬────┘     └─────────┘     └─────────┘
                    │
              ┌─────┴─────┐
              │           │
           ┌──▼──┐    ┌───▼───┐
           │Qdrant│    │Ollama │
           │6333  │    │11434  │
           └──────┘    └───────┘
```

## Next Steps

1. **Run the Visualizer**
   ```bash
   cd pipeline-visualizer
   npm run dev
   ```

2. **Start All Services**
   ```bash
   cd ..
   ./start_all_services.sh
   ```

3. **Open Browser**
   - Navigate to `http://localhost:5173`
   - View the pipeline with PAM integrated
   - Execute test pipeline
   - Monitor PAM metrics

4. **Customize Views**
   - The visualizer supports multiple views (Flow, Timeline, Metrics)
   - PAM appears in all views
   - Real-time updates as pipeline executes

## Configuration

### Enable/Disable PAM in Pipeline

Edit `src/utils/pipelineConfig.js`:

```javascript
// To disable PAM visualization (service still runs independently)
// Remove or comment out the PAM step from PIPELINE_STEPS

// To mark PAM as critical (fail pipeline if unavailable)
PAM: {
  // ... other config
  critical: true  // Change from false to true
}
```

### Adjust PAM Position

In `PIPELINE_STEPS`, modify the PAM step:

```javascript
{
  id: 'pam-service',
  // ...
  position: { x: 100, y: 225 }, // Adjust x,y coordinates
  // ...
}
```

## Troubleshooting

### PAM Not Showing in Visualizer

1. Check `pipelineConfig.js` - PAM step should be present
2. Rebuild the app: `npm run build`
3. Clear browser cache
4. Check browser console for errors

### Health Check Failing

1. Verify PAM service is running: `curl http://localhost:5005/health`
2. Check service logs
3. Ensure Qdrant and Ollama are running

### Pipeline Execution Hangs

1. Check timeout settings in `apiService.js`
2. Verify all services are responsive
3. Check network tab in browser dev tools

## Files Modified

- ✅ `src/utils/pipelineConfig.js` - Added PAM configuration
- ✅ `src/services/apiService.js` - Added PAM API methods
- ✅ `PAM_INTEGRATION.md` - This document

## Success Criteria

- [x] PAM appears in pipeline flow diagram
- [x] PAM health check works
- [x] PAM API methods implemented
- [x] Pipeline execution includes PAM
- [x] Graceful degradation on PAM failure
- [x] Metrics displayed correctly
- [x] Documentation complete

## Conclusion

The PAM service is now fully integrated into the pipeline visualizer. The service appears in the flow diagram, is monitored for health, and participates in pipeline execution. The integration is non-breaking and degrades gracefully if PAM is unavailable.

**Status**: ✅ Integration Complete  
**Version**: 1.0  
**Date**: November 24, 2025

