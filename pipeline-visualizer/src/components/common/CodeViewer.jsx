import React, { useState } from 'react';
import { Copy, Check, Download } from 'lucide-react';
import { formatJSON } from '../../utils/dataFormatter';

const CodeViewer = ({ data, title, language = 'json', maxHeight = '400px' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    const text = typeof data === 'string' ? data : formatJSON(data);
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const text = typeof data === 'string' ? data : formatJSON(data);
    const blob = new Blob([text], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'data'}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formattedData = typeof data === 'string' ? data : formatJSON(data);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        {title && (
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {title}
          </h3>
        )}
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Copy to clipboard"
          >
            {copied ? (
              <Check size={16} className="text-success" />
            ) : (
              <Copy size={16} className="text-gray-600 dark:text-gray-400" />
            )}
          </button>
          <button
            onClick={handleDownload}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Download JSON"
          >
            <Download size={16} className="text-gray-600 dark:text-gray-400" />
          </button>
        </div>
      </div>
      <div 
        className="bg-gray-900 dark:bg-black rounded-lg p-4 overflow-auto"
        style={{ maxHeight }}
      >
        <pre className="text-sm text-gray-100 font-mono whitespace-pre-wrap break-all">
          {formattedData}
        </pre>
      </div>
    </div>
  );
};

export default CodeViewer;

