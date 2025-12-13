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

      <div className="min-h-screen" style={{ backgroundColor: '#FAFAFA' }}>
        {/* Header */}
        <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: '#2D5016' }}>
                  <Shield className="text-white" size={24} />
                </div>
                <div>
                  <h1 className="text-xl font-bold" style={{ color: '#2D5016' }}>
                    Prompt Injection Detector
                  </h1>
                </div>
              </div>
              <nav className="hidden md:flex items-center space-x-8">
                <Link href="/" className="text-sm font-medium hover:opacity-70 transition-opacity" style={{ color: '#2D5016' }}>
                  Detection
                </Link>
                <Link href="/analytics" className="text-sm font-medium hover:opacity-70 transition-opacity font-semibold" style={{ color: '#2D5016' }}>
                  Analytics
                </Link>
                <Link href="/analytics" className="text-sm font-medium hover:opacity-70 transition-opacity" style={{ color: '#2D5016' }}>
                  How it Works
                </Link>
                <Link href="/analytics" className="text-sm font-medium hover:opacity-70 transition-opacity" style={{ color: '#2D5016' }}>
                  FAQ
                </Link>
              </nav>
              <Link
                href="/"
                className="px-5 py-2 rounded-full text-sm font-semibold transition-all playful-hover"
                style={{ backgroundColor: '#87CEEB', color: '#2D5016' }}
              >
                Back to Detection
              </Link>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-16">
          {/* Hero Section */}
          <div className="text-center mb-16 fade-in-up">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight" style={{ color: '#2D5016' }}>
              Analytics{' '}
              <span className="hand-drawn-circle" style={{ color: '#2D5016' }}>
                Dashboard
              </span>
            </h1>
            
            {/* Progress bar */}
            <div className="max-w-4xl mx-auto mb-8">
              <div className="progress-bar" style={{ backgroundColor: '#2D5016', height: '4px' }}></div>
            </div>

            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Real-time detection statistics and insights from the multi-layer defense system.
            </p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64 clean-card">
              <div className="text-gray-600 font-medium">Loading statistics...</div>
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
        <footer className="bg-white border-t border-gray-100 py-12 mt-24">
          <div className="max-w-7xl mx-auto px-6 text-center">
            <p className="text-gray-600 text-sm">
              Prompt Injection Detection Engine v1.0.0 | Built for protecting LLM applications
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}

