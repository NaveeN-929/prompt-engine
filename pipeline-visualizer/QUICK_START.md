# Quick Start Guide

## Prerequisites

1. **Node.js 18+** installed
2. **All backend services running:**
   - Pseudonymization Service (Port 5003)
   - Repersonalization Service (Port 5004)
   - Prompt Engine (Port 5000)
   - Validation Service (Port 5002)
   - Qdrant Vector DB (Port 6333)
   - Ollama LLM (Port 11434)

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

### Development Mode

```bash
npm run dev
```

The app will open at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## First Steps

1. **Check Service Health**
   - Navigate to Dashboard view (top menu)
   - Verify all services show "healthy" status
   - If services are down, start them from the backend

2. **Explore Flow Diagram**
   - Click on "Flow Diagram" in the top menu
   - Click any node to see detailed information
   - Pan and zoom to explore the pipeline

3. **Run a Pipeline**
   - Click on "Execution" in the top menu
   - Review the sample input data (or edit it)
   - Click "Execute Pipeline"
   - Watch the real-time progress in the timeline

4. **View Timeline**
   - Click on "Timeline" in the top menu
   - Expand any step to see details
   - View metrics and data for each step

## Troubleshooting

### Services Not Connecting

If you see "unhealthy" status for services:

1. **Start backend services:**
   ```bash
   cd ../
   ./start_all_services.sh
   ```

2. **Check individual services:**
   ```bash
   curl http://localhost:5003/health  # Pseudonymization
   curl http://localhost:5004/health  # Repersonalization
   curl http://localhost:5000/health  # Prompt Engine
   curl http://localhost:5002/health  # Validation
   curl http://localhost:6333/collections # Qdrant
   curl http://localhost:11434/api/tags # Ollama
   ```

### Port Already in Use

If port 5173 is busy:

```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or edit vite.config.js to use a different port
```

### CORS Errors

If you see CORS errors in the browser console:

1. Make sure backend services allow CORS from `http://localhost:5173`
2. Check that services are actually running
3. Try accessing the API directly in your browser

## Features Overview

### 🔄 Flow Diagram
- Interactive node-based visualization
- Click nodes to drill down
- Animated data flow
- Color-coded status

### ⏱️ Timeline View
- Step-by-step progression
- Expandable details
- Real-time updates
- Metric display

### 📊 Dashboard View
- Service health monitoring
- Performance charts
- Real-time metrics
- Statistical overview

### ▶️ Execution View
- Run complete pipeline
- Edit input data
- Live progress tracking
- Download results

## Tips

1. **Dark Mode**: Click the sun/moon icon in the header
2. **Sample Data**: Pre-loaded in Execution view
3. **Export**: Download results after pipeline execution
4. **Health Check**: Services auto-refresh every 5 seconds
5. **Zoom**: Use mouse wheel in Flow Diagram

## Next Steps

- Explore all 4 visualization modes
- Run pipeline with custom data
- Monitor service health in Dashboard
- Export and analyze results

## Support

For issues:
1. Check browser console (F12)
2. Verify all backend services are running
3. Review the main README.md
4. Check API endpoints directly

---

**Happy Visualizing! 🚀**

