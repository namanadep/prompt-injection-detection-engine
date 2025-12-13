/**
 * Results display component showing detection analysis.
 */
import React from 'react';
import { AlertTriangle, CheckCircle, Shield, AlertCircle, Clock } from 'lucide-react';
import { DetectionResult } from '../services/api';

interface ResultsDisplayProps {
  result: DetectionResult | null;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  if (!result) {
    return null;
  }

  const getThreatColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-red-600 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'medium':
        return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800';
      case 'low':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
      default:
        return 'text-green-600 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
    }
  };

  const getThreatIcon = (level: string) => {
    switch (level) {
      case 'high':
        return <AlertTriangle size={24} />;
      case 'medium':
        return <AlertCircle size={24} />;
      case 'low':
        return <Shield size={24} />;
      default:
        return <CheckCircle size={24} />;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-8 space-y-6">
      {/* Main Result Card */}
      <div className={`p-6 border-2 rounded-lg ${getThreatColor(result.threat_level)}`}>
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            {getThreatIcon(result.threat_level)}
            <div>
              <h3 className="text-xl font-bold mb-2">
                {result.is_threat ? 'Threat Detected' : 'No Threat Detected'}
              </h3>
              <p className="text-sm opacity-90">{result.explanation}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</div>
            <div className="text-xs opacity-75">Confidence</div>
          </div>
        </div>

        {result.processing_time_ms && (
          <div className="mt-4 flex items-center space-x-2 text-sm opacity-75">
            <Clock size={14} />
            <span>Processed in {result.processing_time_ms.toFixed(1)}ms</span>
          </div>
        )}
      </div>

      {/* Layer-by-Layer Results */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Rule-Based Detection */}
        <div className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h4 className="font-semibold text-sm mb-2 text-gray-700 dark:text-gray-300">Rule-Based Detection</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 dark:text-gray-400">Status:</span>
              <span className={`text-xs font-medium ${result.rule_result.detected ? 'text-red-600' : 'text-green-600'}`}>
                {result.rule_result.detected ? 'Detected' : 'Clean'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 dark:text-gray-400">Confidence:</span>
              <span className="text-xs font-medium">{(result.rule_result.confidence * 100).toFixed(1)}%</span>
            </div>
            {result.rule_result.matched_patterns.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Matched Patterns:</p>
                <ul className="space-y-1">
                  {result.rule_result.matched_patterns.slice(0, 3).map((pattern, idx) => (
                    <li key={idx} className="text-xs text-gray-600 dark:text-gray-400">
                      • {pattern.pattern_name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* ML Detection */}
        <div className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h4 className="font-semibold text-sm mb-2 text-gray-700 dark:text-gray-300">ML Model Detection</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 dark:text-gray-400">Status:</span>
              <span className={`text-xs font-medium ${result.ml_result.detected ? 'text-red-600' : 'text-green-600'}`}>
                {result.ml_result.detected ? 'Detected' : 'Clean'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 dark:text-gray-400">Confidence:</span>
              <span className="text-xs font-medium">{(result.ml_result.confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Model: {result.ml_result.model_version}
              </p>
            </div>
          </div>
        </div>

        {/* Vector Similarity Detection */}
        <div className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
          <h4 className="font-semibold text-sm mb-2 text-gray-700 dark:text-gray-300">Vector Similarity</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 dark:text-gray-400">Status:</span>
              <span className={`text-xs font-medium ${result.vector_result.detected ? 'text-red-600' : 'text-green-600'}`}>
                {result.vector_result.detected ? 'Detected' : 'Clean'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600 dark:text-gray-400">Confidence:</span>
              <span className="text-xs font-medium">{(result.vector_result.confidence * 100).toFixed(1)}%</span>
            </div>
            {result.vector_result.similar_attacks.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Similar Attacks:</p>
                <ul className="space-y-1">
                  {result.vector_result.similar_attacks.slice(0, 2).map((attack, idx) => (
                    <li key={idx} className="text-xs text-gray-600 dark:text-gray-400">
                      • {attack.category} ({(attack.similarity_score * 100).toFixed(0)}%)
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

