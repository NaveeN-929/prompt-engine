import React from 'react';
import { Workflow, BarChart3, Play } from 'lucide-react';

const views = [
  { id: 'flow', label: 'Flow Diagram', icon: Workflow },
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
  { id: 'execution', label: 'Execution', icon: Play },
];

const ViewSelector = ({ currentView, onViewChange }) => {
  return (
    <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-8" aria-label="Views">
          {views.map((view) => {
            const Icon = view.icon;
            const isActive = currentView === view.id;
            
            return (
              <button
                key={view.id}
                onClick={() => onViewChange(view.id)}
                className={`
                  flex items-center gap-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors
                  ${isActive
                    ? 'border-processing text-processing'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <Icon size={18} />
                <span>{view.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
};

export default ViewSelector;
