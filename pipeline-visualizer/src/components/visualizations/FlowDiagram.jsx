import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { PIPELINE_STEPS, PIPELINE_EDGES } from '../../utils/pipelineConfig';
import PipelineStepDetail from '../pipeline/PipelineStepDetail';
import { 
  Database, Shield, FileText, Brain, Sparkles, 
  CheckCircle, GitBranch, Unlock 
} from 'lucide-react';

const iconMap = {
  Database, Shield, FileText, Brain, Sparkles,
  CheckCircle, GitBranch, Unlock
};

// Custom Node Component
const CustomNode = ({ data }) => {
  const Icon = iconMap[data.icon] || Database;
  const statusColors = {
    success: 'border-success bg-success bg-opacity-10',
    processing: 'border-processing bg-processing bg-opacity-10 animate-pulse',
    error: 'border-error bg-error bg-opacity-10',
    warning: 'border-warning bg-warning bg-opacity-10',
    idle: 'border-idle bg-gray-50 dark:bg-gray-800',
  };

  return (
    <div
      className={`px-6 py-4 shadow-lg rounded-lg border-2 cursor-pointer transition-all hover:shadow-xl min-w-[200px] ${
        statusColors[data.status] || statusColors.idle
      } bg-white dark:bg-gray-800`}
      onClick={data.onClick}
    >
      <div className="flex items-center gap-3 mb-2">
        <div 
          className="p-2 rounded-lg"
          style={{ backgroundColor: `${data.color}20` }}
        >
          <Icon size={24} style={{ color: data.color }} />
        </div>
        <div className="flex-1">
          <div className="font-bold text-gray-900 dark:text-gray-100 text-sm">
            {data.label}
          </div>
          {data.port && (
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Port: {data.port}
            </div>
          )}
          {data.parallel && (
            <div className="text-xs text-processing font-medium">
              Parallel
            </div>
          )}
        </div>
      </div>
      {data.description && (
        <div className="text-xs text-gray-600 dark:text-gray-400 mt-2">
          {data.description}
        </div>
      )}
      {data.status && data.status !== 'idle' && (
        <div className="mt-2">
          <div className={`text-xs font-medium capitalize ${
            data.status === 'success' ? 'text-success' :
            data.status === 'processing' ? 'text-processing' :
            data.status === 'error' ? 'text-error' :
            data.status === 'warning' ? 'text-warning' : 'text-idle'
          }`}>
            {data.status}
          </div>
        </div>
      )}
    </div>
  );
};

const nodeTypes = {
  custom: CustomNode,
};

const FlowDiagram = ({ pipelineState, stepStatuses }) => {
  const [selectedStep, setSelectedStep] = useState(null);

  // Convert pipeline steps to React Flow nodes - PIPELINE_STEPS is an array
  const initialNodes = PIPELINE_STEPS.map((step) => ({
    id: step.id,
    type: 'custom',
    position: step.position,
    data: {
      label: step.name,
      description: step.description,
      icon: step.icon,
      color: step.color,
      port: step.port,
      parallel: step.parallel || false,
      status: stepStatuses?.[step.id] || 'idle',
      onClick: () => setSelectedStep(step),
    },
  }));

  // Convert pipeline edges to React Flow edges
  const initialEdges = PIPELINE_EDGES.map((edge) => ({
    ...edge,
    type: edge.type || 'smoothstep',
    animated: pipelineState?.currentStep === edge.source || false,
    style: { 
      stroke: '#3B82F6',
      strokeWidth: 2,
      ...edge.style
    },
    label: edge.label || undefined,
    labelStyle: edge.label ? { fill: '#6B7280', fontSize: 12 } : undefined,
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when status changes
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: {
          ...node.data,
          status: stepStatuses?.[node.id] || 'idle',
        },
      }))
    );
  }, [stepStatuses, setNodes]);

  // Update edges when current step changes or parallel steps are running
  useEffect(() => {
    setEdges((eds) =>
      eds.map((edge) => {
        const isActive = pipelineState?.currentStep === edge.source ||
                        pipelineState?.parallelSteps?.includes(edge.source) || false;
        return {
          ...edge,
          animated: isActive,
          style: {
            ...edge.style,
            stroke: isActive ? '#3B82F6' : '#94A3B8',
            strokeWidth: isActive ? 3 : 2,
          },
        };
      })
    );
  }, [pipelineState?.currentStep, pipelineState?.parallelSteps, setEdges]);

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-gray-50 dark:bg-gray-900"
      >
        <Background color="#aaa" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const status = node.data?.status || 'idle';
            if (status === 'success') return '#10B981';
            if (status === 'processing') return '#3B82F6';
            if (status === 'error') return '#EF4444';
            if (status === 'warning') return '#F59E0B';
            return '#6B7280';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>

      {/* Step Detail Modal */}
      {selectedStep && (
        <PipelineStepDetail
          step={selectedStep}
          stepData={pipelineState?.steps?.[selectedStep.id]}
          status={stepStatuses?.[selectedStep.id] || 'idle'}
          onClose={() => setSelectedStep(null)}
        />
      )}
    </div>
  );
};

export default FlowDiagram;
