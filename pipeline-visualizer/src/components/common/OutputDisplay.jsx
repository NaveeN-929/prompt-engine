import React, { useState } from 'react';
import { CheckCircle, Lightbulb, TrendingUp, AlertCircle, Copy, Download, Maximize2, Minimize2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { parseOutput, getQualityLevel } from '../../utils/textParser';

const OutputDisplay = ({ outputData, validationResult }) => {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  if (!outputData && !validationResult) {
    return (
      <div className="card">
        <div className="text-center py-12">
          <Lightbulb size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600 dark:text-gray-400">
            No output yet. Execute the pipeline to see insights and recommendations.
          </p>
        </div>
      </div>
    );
  }

  const insights = outputData?.insights || '';
  const recommendations = outputData?.recommendations || '';
  const qualityScore = validationResult?.overall_score || outputData?.quality_score;
  const qualityLevelRaw = validationResult?.quality_level || outputData?.quality_level;

  // Parse the output into structured bullet points
  const parsedOutput = parseOutput(insights || recommendations);

  // Get quality level info
  const qualityInfo = qualityScore ? getQualityLevel(qualityScore) : { label: 'N/A', color: 'gray' };

  const handleCopy = () => {
    const insightsText = parsedOutput.insights.map((item, i) => `${i + 1}. ${item}`).join('\n');
    const recommendationsText = parsedOutput.recommendations.map((item, i) => `${i + 1}. ${item}`).join('\n');
    const fullText = `INSIGHTS:\n${insightsText}\n\nRECOMMENDATIONS:\n${recommendationsText}`;
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const insightsText = parsedOutput.insights.map((item, i) => `${i + 1}. ${item}`).join('\n');
    const recommendationsText = parsedOutput.recommendations.map((item, i) => `${i + 1}. ${item}`).join('\n');
    const fullText = `PIPELINE OUTPUT\n${'='.repeat(50)}\n\nINSIGHTS:\n${insightsText}\n\nRECOMMENDATIONS:\n${recommendationsText}\n\nQuality Score: ${qualityScore ? (qualityScore * 100).toFixed(1) + '%' : 'N/A'}`;
    const blob = new Blob([fullText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pipeline-output-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`card ${expanded ? 'fixed inset-4 z-50 overflow-auto' : ''}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-success bg-opacity-10 rounded-lg">
            <CheckCircle size={24} className="text-success" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Pipeline Output
            </h3>
            {qualityScore && (
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Quality Score:
                </span>
                <span className={`text-xs font-semibold text-${qualityInfo.color}`}>
                  {(qualityScore * 100).toFixed(1)}%
                </span>
                <span className={`text-xs px-2 py-0.5 rounded bg-${qualityInfo.color} bg-opacity-10 text-${qualityInfo.color}`}>
                  {qualityInfo.label}
                </span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Copy to clipboard"
          >
            {copied ? (
              <CheckCircle size={18} className="text-success" />
            ) : (
              <Copy size={18} className="text-gray-600 dark:text-gray-400" />
            )}
          </button>
          <button
            onClick={handleDownload}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Download output"
          >
            <Download size={18} className="text-gray-600 dark:text-gray-400" />
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title={expanded ? "Minimize" : "Maximize"}
          >
            {expanded ? (
              <Minimize2 size={18} className="text-gray-600 dark:text-gray-400" />
            ) : (
              <Maximize2 size={18} className="text-gray-600 dark:text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Insights Section */}
      {parsedOutput.insights && parsedOutput.insights.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb size={20} className="text-processing" />
            <h4 className="text-md font-semibold text-gray-900 dark:text-gray-100">
              Insights
            </h4>
          </div>
          <div className="bg-processing bg-opacity-5 dark:bg-processing dark:bg-opacity-10 rounded-lg p-4 border-l-4 border-processing">
            <ul className="space-y-3">
              {parsedOutput.insights.map((insight, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-processing text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                    {index + 1}
                  </span>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                    {insight}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Recommendations Section */}
      {parsedOutput.recommendations && parsedOutput.recommendations.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp size={20} className="text-success" />
            <h4 className="text-md font-semibold text-gray-900 dark:text-gray-100">
              Recommendations
            </h4>
          </div>
          <div className="bg-success bg-opacity-5 dark:bg-success dark:bg-opacity-10 rounded-lg p-4 border-l-4 border-success">
            <ul className="space-y-3">
              {parsedOutput.recommendations.map((recommendation, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-success text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5">
                    {index + 1}
                  </span>
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed flex-1">
                    {recommendation}
                  </p>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Validation Details */}
      {validationResult?.criteria_scores && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <AlertCircle size={20} className="text-warning" />
            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              Validation Criteria
            </h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(validationResult.criteria_scores).map(([criterion, score]) => (
              <div key={criterion} className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3">
                <div className="text-xs text-gray-600 dark:text-gray-400 capitalize mb-1">
                  {criterion.replace(/_/g, ' ')}
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {(score * 100).toFixed(0)}%
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5 mt-1">
                  <div 
                    className={`h-1.5 rounded-full ${
                      score >= 0.8 ? 'bg-success' : 
                      score >= 0.65 ? 'bg-warning' : 'bg-error'
                    }`}
                    style={{ width: `${score * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default OutputDisplay;
