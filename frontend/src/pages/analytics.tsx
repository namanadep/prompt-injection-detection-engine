/**
 * Analytics page.
 */
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Shield, Home } from 'lucide-react';
import { ThreatStats } from '../components/ThreatStats';
import { AnalyticsDashboard } from '../components/AnalyticsDashboard';
import { DetectionStats, apiClient } from '../services/api';

export default function Analytics() {
  const [stats, setStats] = useState<DetectionStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await apiClient.getStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Analytics - Prompt Injection Detection Engine</title>
        <meta name="description" content="Analytics dashboard for prompt injection detection" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Shield className="text-blue-600" size={32} />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                    Analytics Dashboard
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Real-time detection statistics and insights
                  </p>
                </div>
              </div>
              <Link
                href="/"
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
              >
                <Home size={18} />
                <span>Detection</span>
              </Link>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-gray-600 dark:text-gray-400">Loading statistics...</div>
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <ThreatStats stats={stats} />

              {/* Analytics Charts */}
              <AnalyticsDashboard />
            </>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 py-8 border-t border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-gray-600 dark:text-gray-400">
            <p>Prompt Injection Detection Engine v1.0.0 | Built for protecting LLM applications</p>
          </div>
        </footer>
      </div>
    </>
  );
}

