/**
 * Threat statistics component - Clean, modern design
 */
import React from 'react';
import { Activity, Shield, TrendingUp, AlertTriangle } from 'lucide-react';
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
      title: 'Total Requests',
      value: stats.total_requests.toLocaleString(),
      icon: <Activity size={24} />,
      bgColor: '#87CEEB',
      textColor: '#2D5016',
    },
    {
      title: 'Threats Detected',
      value: stats.threats_detected.toLocaleString(),
      icon: <AlertTriangle size={24} />,
      bgColor: '#FFD700',
      textColor: '#2D5016',
    },
    {
      title: 'Threat Rate',
      value: `${stats.threat_percentage.toFixed(1)}%`,
      icon: <TrendingUp size={24} />,
      bgColor: '#2D5016',
      textColor: 'white',
    },
    {
      title: 'Avg Confidence',
      value: `${(stats.avg_confidence * 100).toFixed(1)}%`,
      icon: <Shield size={24} />,
      bgColor: '#87CEEB',
      textColor: '#2D5016',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
      {statCards.map((card, index) => (
        <div
          key={index}
          className="clean-card p-6 text-center playful-hover"
        >
          <div 
            className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center"
            style={{ backgroundColor: card.bgColor, color: card.textColor }}
          >
            {card.icon}
          </div>
          <h3 className="text-sm font-semibold text-gray-600 mb-2">{card.title}</h3>
          <div className="text-3xl font-bold" style={{ color: '#2D5016' }}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
};

