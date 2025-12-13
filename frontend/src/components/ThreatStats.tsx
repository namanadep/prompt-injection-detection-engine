/**
 * Threat statistics component - Terminal style
 */
import React from 'react';
import { Activity, Shield, TrendingUp, AlertTriangle, Terminal } from 'lucide-react';
import { DetectionStats } from '../services/api';

interface ThreatStatsProps {
  stats: DetectionStats | null;
}

export const ThreatStats: React.FC<ThreatStatsProps> = ({ stats }) => {
  if (!stats) {
    return null;
  }

  const statCards = [
    {
      title: 'TOTAL REQUESTS',
      value: stats.total_requests.toLocaleString(),
      icon: <Activity size={20} />,
      borderColor: '#00FFFF',
      textColor: '#00FFFF',
    },
    {
      title: 'THREATS DETECTED',
      value: stats.threats_detected.toLocaleString(),
      icon: <AlertTriangle size={20} />,
      borderColor: '#FF0000',
      textColor: '#FF0000',
    },
    {
      title: 'THREAT RATE',
      value: `${stats.threat_percentage.toFixed(1)}%`,
      icon: <TrendingUp size={20} />,
      borderColor: '#FF8C00',
      textColor: '#FF8C00',
    },
    {
      title: 'AVG CONFIDENCE',
      value: `${(stats.avg_confidence * 100).toFixed(1)}%`,
      icon: <Shield size={20} />,
      borderColor: '#00FF41',
      textColor: '#00FF41',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {statCards.map((card, index) => (
        <div
          key={index}
          className="border-2 bg-black/60 neon-border relative group hover:scale-105 transition-transform"
          style={{ borderColor: card.borderColor }}
        >
          {/* Terminal Header */}
          <div className="border-b-2 px-3 py-2 flex items-center justify-between" style={{ borderColor: card.borderColor }}>
            <Terminal size={14} style={{ color: card.textColor, opacity: 0.7 }} />
            <span className="text-xs font-mono uppercase tracking-wider" style={{ color: card.textColor, opacity: 0.7 }}>
              STAT
            </span>
          </div>
          
          {/* Content */}
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider" style={{ color: card.textColor, opacity: 0.7 }}>
                {card.title}
              </span>
              <div style={{ color: card.textColor, opacity: 0.5 }}>
                {card.icon}
              </div>
            </div>
            <div className="text-3xl font-mono font-bold neon-glow" style={{ color: card.textColor }}>
              {card.value}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

