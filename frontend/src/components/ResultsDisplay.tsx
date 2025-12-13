/**
 * Results display component - Clean, modern design
 */
import React from 'react';
import { AlertTriangle, CheckCircle, Shield, AlertCircle, Clock, Zap } from 'lucide-react';
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
        return { bg: '#FEF2F2', border: '#EF4444', text: '#DC2626', icon: '#EF4444' };
      case 'medium':
        return { bg: '#FFF7ED', border: '#F97316', text: '#EA580C', icon: '#F97316' };
      case 'low':
        return { bg: '#FEFCE8', border: '#EAB308', text: '#CA8A04', icon: '#EAB308' };
      default:
        return { bg: '#F0FDF4', border: '#22C55E', text: '#16A34A', icon: '#22C55E' };
    }
  };

  const getThreatIcon = (level: string) => {
    switch (level) {
      case 'high':
        return <AlertTriangle size={32} />;
      case 'medium':
        return <AlertCircle size={32} />;
      case 'low':
        return <Shield size={32} />;
      default:
        return <CheckCircle size={32} />;
    }
  };

  const threatColors = getThreatColor(result.threat_level);

  return (
    <div className="w-full max-w-5xl mx-auto mt-8 space-y-6">
      {/* Main Result Card */}
      <div 
        className="clean-card p-8 border-2 fade-in-up"
        style={{ 
          backgroundColor: threatColors.bg,
          borderColor: threatColors.border
        }}
      >
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-start space-x-4 flex-1">
            <div 
              className="w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: threatColors.icon, color: 'white' }}
            >
              {getThreatIcon(result.threat_level)}
            </div>
            <div className="flex-1">
              <h3 className="text-2xl font-bold mb-3" style={{ color: threatColors.text }}>
                {result.is_threat ? 'Threat Detected' : 'No Threat Detected'}
              </h3>
              <p className="text-gray-700 leading-relaxed">{result.explanation}</p>
            </div>
          </div>
          <div className="text-right ml-6">
            <div className="text-4xl font-bold mb-1" style={{ color: threatColors.text }}>
              {(result.confidence * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-600 font-medium">Confidence</div>
          </div>
        </div>

        {result.processing_time_ms && (
          <div className="mt-6 pt-6 border-t border-gray-200 flex items-center space-x-2 text-sm text-gray-600">
            <Clock size={16} />
            <span>Processed in {result.processing_time_ms.toFixed(1)}ms</span>
          </div>
        )}
      </div>

      {/* Layer-by-Layer Results */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Rule-Based Detection */}
        <div className="clean-card p-6 playful-hover">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#2D5016' }}>
              <Shield className="text-white" size={20} />
            </div>
            <h4 className="font-bold text-lg" style={{ color: '#2D5016' }}>Rule-Based</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <span className={`text-sm font-semibold ${result.rule_result.detected ? 'text-red-600' : 'text-green-600'}`}>
                {result.rule_result.detected ? 'Detected' : 'Clean'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Confidence:</span>
              <span className="text-sm font-bold" style={{ color: '#2D5016' }}>
                {(result.rule_result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            {result.rule_result.matched_patterns.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Matched Patterns:</p>
                <ul className="space-y-1">
                  {result.rule_result.matched_patterns.slice(0, 3).map((pattern, idx) => (
                    <li key={idx} className="text-xs text-gray-600 flex items-center">
                      <span className="mr-2" style={{ color: '#2D5016' }}>•</span>
                      {pattern.pattern_name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* ML Detection */}
        <div className="clean-card p-6 playful-hover">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#87CEEB' }}>
              <Zap className="text-white" size={20} />
            </div>
            <h4 className="font-bold text-lg" style={{ color: '#2D5016' }}>ML Model</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <span className={`text-sm font-semibold ${result.ml_result.detected ? 'text-red-600' : 'text-green-600'}`}>
                {result.ml_result.detected ? 'Detected' : 'Clean'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Confidence:</span>
              <span className="text-sm font-bold" style={{ color: '#87CEEB' }}>
                {(result.ml_result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-600">
                Model: <span className="font-mono">{result.ml_result.model_version}</span>
              </p>
            </div>
          </div>
        </div>

        {/* Vector Similarity Detection */}
        <div className="clean-card p-6 playful-hover">
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#FFD700' }}>
              <Shield className="text-white" size={20} />
            </div>
            <h4 className="font-bold text-lg" style={{ color: '#2D5016' }}>Vector DB</h4>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status:</span>
              <span className={`text-sm font-semibold ${result.vector_result.detected ? 'text-red-600' : 'text-green-600'}`}>
                {result.vector_result.detected ? 'Detected' : 'Clean'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Confidence:</span>
              <span className="text-sm font-bold" style={{ color: '#FFD700' }}>
                {(result.vector_result.confidence * 100).toFixed(1)}%
              </span>
            </div>
            {result.vector_result.similar_attacks.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">Similar Attacks:</p>
                <ul className="space-y-1">
                  {result.vector_result.similar_attacks.slice(0, 2).map((attack, idx) => (
                    <li key={idx} className="text-xs text-gray-600 flex items-center">
                      <span className="mr-2" style={{ color: '#FFD700' }}>•</span>
                      {attack.category} ({(attack.similarity_score * 100).toFixed(0)}%)
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
