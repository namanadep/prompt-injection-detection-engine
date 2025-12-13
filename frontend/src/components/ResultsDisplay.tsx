/**
 * Results display component - Terminal style
 */
import React from 'react';
import { AlertTriangle, CheckCircle, Shield, AlertCircle, Clock, Terminal, Zap } from 'lucide-react';
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
        return { border: '#FF0000', bg: 'rgba(255, 0, 0, 0.1)', text: '#FF0000' };
      case 'medium':
        return { border: '#FF8C00', bg: 'rgba(255, 140, 0, 0.1)', text: '#FF8C00' };
      case 'low':
        return { border: '#FFD700', bg: 'rgba(255, 215, 0, 0.1)', text: '#FFD700' };
      default:
        return { border: '#00FF41', bg: 'rgba(0, 255, 65, 0.1)', text: '#00FF41' };
    }
  };

  const getThreatIcon = (level: string) => {
    switch (level) {
      case 'high':
        return <AlertTriangle size={20} className="text-red-400" style={{ color: '#FF0000' }} />;
      case 'medium':
        return <AlertCircle size={20} className="text-orange-400" style={{ color: '#FF8C00' }} />;
      case 'low':
        return <Shield size={20} className="text-yellow-400" />;
      default:
        return <CheckCircle size={20} className="text-green-400" style={{ color: '#00FF41' }} />;
    }
  };

  const threatColors = getThreatColor(result.threat_level);

  return (
    <div className="w-full max-w-5xl mt-8 space-y-6">
      {/* Main Result Terminal */}
      <div 
        className="border-2 bg-black/80 neon-border"
        style={{ 
          borderColor: threatColors.border,
          backgroundColor: threatColors.bg
        }}
      >
        {/* Terminal Header */}
        <div className="border-b-2 px-4 py-2 flex items-center justify-between" style={{ borderColor: threatColors.border }}>
          <div className="flex items-center space-x-2">
            <Terminal size={16} style={{ color: threatColors.text }} />
            <span className="text-xs font-mono uppercase tracking-wider neon-glow" style={{ color: threatColors.text }}>
              DETECTION_RESULT
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-2xl font-mono font-bold neon-glow" style={{ color: threatColors.text }}>
                {(result.confidence * 100).toFixed(1)}%
              </div>
              <div className="text-xs font-mono opacity-70" style={{ color: threatColors.text }}>
                CONFIDENCE
              </div>
            </div>
          </div>
        </div>

        {/* Terminal Body */}
        <div className="p-6">
          <div className="flex items-start space-x-4 mb-4">
            {getThreatIcon(result.threat_level)}
            <div className="flex-1">
              <h3 className="text-xl font-mono font-bold mb-3 neon-glow uppercase" style={{ color: threatColors.text }}>
                {result.is_threat ? '⚠ THREAT DETECTED' : '✓ NO THREAT DETECTED'}
              </h3>
              <p className="text-sm font-mono leading-relaxed" style={{ color: threatColors.text, opacity: 0.9 }}>
                {result.explanation}
              </p>
            </div>
          </div>

          {result.processing_time_ms && (
            <div className="mt-4 pt-4 border-t-2 flex items-center space-x-2 text-xs font-mono" style={{ borderColor: threatColors.border, color: threatColors.text, opacity: 0.7 }}>
              <Clock size={14} />
              <span>PROCESSED IN {result.processing_time_ms.toFixed(1)}MS</span>
            </div>
          )}
        </div>
      </div>

      {/* Layer-by-Layer Results */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Rule-Based Detection */}
        <div className="border-2 border-yellow-400/30 bg-black/60 neon-border" style={{ borderColor: 'rgba(255, 215, 0, 0.3)' }}>
          <div className="border-b-2 border-yellow-400/30 px-4 py-2" style={{ borderColor: 'rgba(255, 215, 0, 0.3)' }}>
            <h4 className="font-mono text-xs uppercase tracking-wider text-yellow-400 neon-glow">TIER 1: RULE-BASED</h4>
          </div>
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-yellow-400/70">STATUS:</span>
              <span className={`text-xs font-mono font-bold ${result.rule_result.detected ? 'text-red-400' : 'text-green-400'}`} style={{ color: result.rule_result.detected ? '#FF0000' : '#00FF41' }}>
                {result.rule_result.detected ? 'DETECTED' : 'CLEAN'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-yellow-400/70">CONFIDENCE:</span>
              <span className="text-xs font-mono font-bold text-yellow-400">{(result.rule_result.confidence * 100).toFixed(1)}%</span>
            </div>
            {result.rule_result.matched_patterns.length > 0 && (
              <div className="mt-3 pt-3 border-t-2 border-yellow-400/20" style={{ borderColor: 'rgba(255, 215, 0, 0.2)' }}>
                <p className="text-xs font-mono font-bold text-yellow-400 mb-2 uppercase">PATTERNS:</p>
                <ul className="space-y-1">
                  {result.rule_result.matched_patterns.slice(0, 3).map((pattern, idx) => (
                    <li key={idx} className="text-xs font-mono text-yellow-400/70">
                      &gt; {pattern.pattern_name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* ML Detection */}
        <div className="border-2 border-cyan-400/30 bg-black/60 neon-border" style={{ borderColor: 'rgba(0, 255, 255, 0.3)' }}>
          <div className="border-b-2 border-cyan-400/30 px-4 py-2" style={{ borderColor: 'rgba(0, 255, 255, 0.3)' }}>
            <h4 className="font-mono text-xs uppercase tracking-wider text-cyan-400 neon-glow" style={{ color: '#00FFFF' }}>TIER 2: ML MODEL</h4>
          </div>
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-cyan-400/70" style={{ color: 'rgba(0, 255, 255, 0.7)' }}>STATUS:</span>
              <span className={`text-xs font-mono font-bold ${result.ml_result.detected ? 'text-red-400' : 'text-green-400'}`} style={{ color: result.ml_result.detected ? '#FF0000' : '#00FF41' }}>
                {result.ml_result.detected ? 'DETECTED' : 'CLEAN'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-cyan-400/70" style={{ color: 'rgba(0, 255, 255, 0.7)' }}>CONFIDENCE:</span>
              <span className="text-xs font-mono font-bold text-cyan-400 neon-glow" style={{ color: '#00FFFF' }}>{(result.ml_result.confidence * 100).toFixed(1)}%</span>
            </div>
            <div className="mt-3 pt-3 border-t-2 border-cyan-400/20" style={{ borderColor: 'rgba(0, 255, 255, 0.2)' }}>
              <p className="text-xs font-mono text-cyan-400/70" style={{ color: 'rgba(0, 255, 255, 0.7)' }}>
                MODEL: {result.ml_result.model_version}
              </p>
            </div>
          </div>
        </div>

        {/* Vector Similarity Detection */}
        <div className="border-2 border-green-400/30 bg-black/60 neon-border" style={{ borderColor: 'rgba(0, 255, 65, 0.3)' }}>
          <div className="border-b-2 border-green-400/30 px-4 py-2" style={{ borderColor: 'rgba(0, 255, 65, 0.3)' }}>
            <h4 className="font-mono text-xs uppercase tracking-wider text-green-400 neon-glow" style={{ color: '#00FF41' }}>TIER 3: VECTOR DB</h4>
          </div>
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-green-400/70" style={{ color: 'rgba(0, 255, 65, 0.7)' }}>STATUS:</span>
              <span className={`text-xs font-mono font-bold ${result.vector_result.detected ? 'text-red-400' : 'text-green-400'}`} style={{ color: result.vector_result.detected ? '#FF0000' : '#00FF41' }}>
                {result.vector_result.detected ? 'DETECTED' : 'CLEAN'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-green-400/70" style={{ color: 'rgba(0, 255, 65, 0.7)' }}>CONFIDENCE:</span>
              <span className="text-xs font-mono font-bold text-green-400 neon-glow" style={{ color: '#00FF41' }}>{(result.vector_result.confidence * 100).toFixed(1)}%</span>
            </div>
            {result.vector_result.similar_attacks.length > 0 && (
              <div className="mt-3 pt-3 border-t-2 border-green-400/20" style={{ borderColor: 'rgba(0, 255, 65, 0.2)' }}>
                <p className="text-xs font-mono font-bold text-green-400 mb-2 uppercase" style={{ color: '#00FF41' }}>SIMILAR:</p>
                <ul className="space-y-1">
                  {result.vector_result.similar_attacks.slice(0, 2).map((attack, idx) => (
                    <li key={idx} className="text-xs font-mono text-green-400/70" style={{ color: 'rgba(0, 255, 65, 0.7)' }}>
                      &gt; {attack.category} ({(attack.similarity_score * 100).toFixed(0)}%)
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

