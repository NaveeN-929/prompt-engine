import React from 'react';
import { Sun, Moon, Activity } from 'lucide-react';

const Header = ({ darkMode, toggleDarkMode, healthSummary }) => {
  return (
    <header className="bg-white dark:bg-gray-800 shadow-md border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-processing bg-opacity-10 rounded-lg">
              <Activity size={32} className="text-processing" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                Pipeline Visualizer
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Self-Learning Prompt Engine System
              </p>
            </div>
          </div>

          {/* Health Summary and Controls */}
          <div className="flex items-center gap-4">
            {healthSummary && (
              <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  healthSummary.percentage === 100 ? 'bg-success' :
                  healthSummary.percentage >= 50 ? 'bg-warning' : 'bg-error'
                } animate-pulse`} />
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {healthSummary.healthy}/{healthSummary.total} Services
                </span>
              </div>
            )}
            
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {darkMode ? (
                <Sun size={20} className="text-yellow-500" />
              ) : (
                <Moon size={20} className="text-gray-600" />
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

