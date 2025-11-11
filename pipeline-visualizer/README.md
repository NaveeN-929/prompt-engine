# Pipeline Visualizer

A comprehensive React application for visualizing the complete end-to-end pipeline of the Self-Learning Prompt Engine System.

## Features

### 🎨 Multiple Visualization Modes

1. **Flow Diagram** - Interactive React Flow diagram with drag-and-drop nodes
2. **Timeline View** - Step-by-step progression with collapsible details
3. **Dashboard View** - Real-time metrics, charts, and service health monitoring
4. **Execution View** - Run complete pipeline and watch step-by-step progress

### 🔄 Complete Pipeline Coverage

Visualizes all 8 pipeline steps:
1. **Data Generation** - Business banking transactions with PII
2. **Pseudonymization** - PII detection & masking (Port 5003)
3. **Prompt Generation** - Intelligent prompt creation (Port 5000)
4. **RAG Enhancement** - Vector database context (Qdrant 6333)
5. **LLM Analysis** - Ollama text generation (Port 11434)
6. **Validation** - Quality assessment (Port 5002)
7. **Self-Learning** - Pattern storage & knowledge graph
8. **Repersonalization** - Restore original data (Port 5004)

### ⚡ Real-time Features

- **Service Health Monitoring** - Auto-refresh every 5 seconds
- **Live Pipeline Execution** - Watch data flow through steps
- **Performance Metrics** - Response times, success rates, request volumes
- **Interactive Charts** - Line charts, bar charts, pie charts

### 🎯 Key Capabilities

- **Dark/Light Mode** - Automatic theme switching with persistence
- **Responsive Design** - Works on mobile, tablet, and desktop
- **Interactive Nodes** - Click to drill down into step details
- **Code Viewer** - View and export JSON data
- **Export Results** - Download pipeline execution results
- **Sample Data** - Pre-loaded example data for testing

## Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend services running (ports 5000, 5002, 5003, 5004, 6333, 11434)

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Usage

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Connecting to Backend Services

The visualizer connects to the following services:

- **Pseudonymization Service** - http://localhost:5003
- **Repersonalization Service** - http://localhost:5004
- **Prompt Engine** - http://localhost:5000
- **Validation Service** - http://localhost:5002
- **Qdrant Vector DB** - http://localhost:6333
- **Ollama LLM** - http://localhost:11434

Make sure all services are running before starting the visualizer.

### Quick Start

1. **Start all backend services**
   ```bash
   # From the prompt-engine root directory
   ./start_all_services.sh
   ```

2. **Start the visualizer**
   ```bash
   cd pipeline-visualizer
   npm run dev
   ```

3. **Open in browser**
   Navigate to `http://localhost:5173`

4. **Check service health**
   Switch to Dashboard view to see all service statuses

5. **Execute pipeline**
   Switch to Execution view, edit input data, and click "Execute Pipeline"

## Features by View

### Flow Diagram
- Interactive node-based visualization
- Animated data flow between steps
- Click nodes to view details
- Color-coded status (success, processing, error, idle)
- Pan and zoom controls
- Mini-map overview

### Timeline View
- Vertical step-by-step progression
- Expandable step details
- Real-time status updates
- Processing time per step
- Success/error indicators
- Collapsible data viewers

### Dashboard View
- Service health cards (8 services)
- Response time trend chart
- Success rate bar chart
- Request volume line chart
- Service health pie chart
- Real-time metric updates

### Execution View
- JSON input data editor
- Execute pipeline button
- Real-time progress tracking
- Step-by-step execution timeline
- Download results
- Error handling and validation

## Configuration

### API Endpoints

Edit `src/utils/pipelineConfig.js` to configure service endpoints:

```javascript
export const SERVICES = {
  PSEUDONYMIZATION: {
    name: 'Pseudonymization Service',
    port: 5003,
    url: 'http://localhost:5003',
    healthEndpoint: '/health'
  },
  // ... more services
};
```

### Theme Colors

Edit `tailwind.config.js` to customize colors:

```javascript
colors: {
  success: '#10B981',
  processing: '#3B82F6',
  error: '#EF4444',
  idle: '#6B7280',
  warning: '#F59E0B',
}
```

### Polling Interval

Change health check polling interval in `App.jsx`:

```javascript
useServiceHealth(5000); // Poll every 5 seconds
```

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool
- **React Flow** - Interactive diagrams
- **Recharts** - Charts and graphs
- **Framer Motion** - Animations
- **Axios** - API communication
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## Project Structure

```
pipeline-visualizer/
├── src/
│   ├── components/
│   │   ├── visualizations/      # Main visualization components
│   │   ├── pipeline/             # Pipeline step details
│   │   ├── common/               # Reusable components
│   │   └── layout/               # Layout components
│   ├── services/                 # API service layer
│   ├── hooks/                    # Custom React hooks
│   ├── utils/                    # Utility functions
│   ├── App.jsx                   # Main app component
│   └── main.jsx                  # Entry point
├── public/                       # Static assets
├── index.html                    # HTML template
├── tailwind.config.js            # Tailwind configuration
├── vite.config.js                # Vite configuration
└── package.json                  # Dependencies
```

## Development

### Adding New Visualizations

1. Create component in `src/components/visualizations/`
2. Add view to `src/components/layout/ViewSelector.jsx`
3. Integrate in `App.jsx`

### Adding New Pipeline Steps

1. Update `src/utils/pipelineConfig.js` with step metadata
2. Add service endpoints
3. Update visualization components to handle new step

### Styling Guidelines

- Use Tailwind utility classes
- Follow dark mode pattern: `class="bg-white dark:bg-gray-800"`
- Use status colors: `success`, `processing`, `error`, `idle`, `warning`
- Maintain responsive design with breakpoints

## Troubleshooting

### Services Not Connecting

1. Verify all backend services are running
2. Check service ports match configuration
3. Look for CORS errors in browser console
4. Test endpoints directly: `curl http://localhost:5003/health`

### Dark Mode Not Working

1. Clear localStorage: `localStorage.clear()`
2. Check browser console for errors
3. Verify Tailwind dark mode is configured

### Charts Not Displaying

1. Check Recharts is installed: `npm list recharts`
2. Verify data format matches chart requirements
3. Check browser console for errors

## Performance

- Health checks run every 5 seconds (configurable)
- Service requests timeout after 30 seconds
- Charts update data every minute
- React Flow optimized for 8 nodes

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

Proprietary - All rights reserved

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend service logs
3. Test API endpoints directly
4. Check browser developer console

## Version

Current version: 1.0.0

## Contributors

Built for the Self-Learning Prompt Engine System
