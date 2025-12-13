/**
 * Threat statistics component.
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
      color: 'text-blue-600 bg-blue-50 dark:bg-blue-900/20',
    },
    {
      title: 'Threats Detected',
      value: stats.threats_detected.toLocaleString(),
      icon: <AlertTriangle size={24} />,
      color: 'text-red-600 bg-red-50 dark:bg-red-900/20',
    },
    {
      title: 'Threat Rate',
      value: `${stats.threat_percentage.toFixed(1)}%`,
      icon: <TrendingUp size={24} />,
      color: 'text-orange-600 bg-orange-50 dark:bg-orange-900/20',
    },
    {
      title: 'Avg Confidence',
      value: `${(stats.avg_confidence * 100).toFixed(1)}%`,
      icon: <Shield size={24} />,
      color: 'text-green-600 bg-green-50 dark:bg-green-900/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {statCards.map((card, index) => (
        <div
          key={index}
          className="p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">{card.title}</span>
            <div className={`p-2 rounded-lg ${card.color}`}>{card.icon}</div>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{card.value}</div>
        </div>
      ))}
    </div>
  );
};

