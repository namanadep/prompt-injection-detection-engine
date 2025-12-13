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

      <div className="min-h-screen terminal-bg relative" style={{ backgroundColor: '#000000' }}>
        {/* Scanline effect */}
        <div className="scanlines"></div>

        {/* Sidebar Navigation */}
        <aside className="fixed left-0 top-0 h-full w-64 border-r-2 border-yellow-400/30 bg-black/90 backdrop-blur-sm z-40">
          <div className="p-6">
            {/* Logo */}
            <div className="mb-12">
              <h1 className="text-yellow-400 pixelated neon-glow text-2xl font-bold mb-2">
                INJECTION
              </h1>
              <h2 className="text-yellow-400 pixelated neon-glow text-xl font-bold mb-1">
                DETECTOR
              </h2>
              <p className="text-green-400 text-xs mt-2 opacity-70">
                MULTI-LAYER DEFENSE SYSTEM
              </p>
            </div>

            {/* Navigation */}
            <nav className="space-y-2">
              <Link
                href="/"
                className="flex items-center space-x-3 px-4 py-3 hover:bg-yellow-400/10 hover:border-l-2 hover:border-yellow-400/50 text-yellow-400/70 hover:text-yellow-400 transition-all"
              >
                <Home size={18} />
                <span className="text-sm font-mono">DETECTION</span>
              </Link>
              <Link
                href="/analytics"
                className="flex items-center space-x-3 px-4 py-3 bg-yellow-400/10 border-l-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400/20 transition-all glitch"
              >
                <Shield size={18} />
                <span className="text-sm font-mono">ANALYTICS</span>
              </Link>
            </nav>

            {/* Status Indicators */}
            <div className="mt-12 space-y-3">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full neon-glow" style={{ color: '#00FF41' }}></div>
                <span className="text-green-400 text-xs font-mono">SYSTEM ONLINE</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full neon-glow"></div>
                <span className="text-yellow-400 text-xs font-mono">4 TIER DEFENSE</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="ml-64 min-h-screen p-8">
          {/* Top Bar */}
          <div className="flex items-center justify-between mb-8 pb-4 border-b-2 border-yellow-400/20">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full neon-glow"></div>
                <span className="text-yellow-400 text-xs font-mono">ANALYTICS DASHBOARD</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full neon-glow" style={{ color: '#00FF41' }}></div>
                <span className="text-green-400 text-xs font-mono">REAL-TIME DATA</span>
              </div>
            </div>
            <div className="text-yellow-400/50 text-xs font-mono">
              v1.0.0 | TERMINAL MODE
            </div>
          </div>

          {/* Hero Section */}
          <div className="mb-12">
            <h1 className="text-yellow-400 pixelated neon-glow text-5xl font-bold mb-4 leading-tight">
              ANALYTICS
            </h1>
            <h2 className="text-yellow-400 pixelated neon-glow text-4xl font-bold mb-6">
              DASHBOARD
            </h2>
            <p className="text-green-400 text-lg font-mono max-w-3xl leading-relaxed">
              REAL-TIME DETECTION STATISTICS AND INSIGHTS FROM THE MULTI-LAYER DEFENSE SYSTEM.
            </p>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64 border-2 border-yellow-400/30 bg-black/60">
              <div className="text-yellow-400 font-mono text-sm neon-glow">LOADING STATISTICS...</div>
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <ThreatStats stats={stats} />

              {/* Analytics Charts */}
              <AnalyticsDashboard />
            </>
          )}

          {/* Footer */}
          <footer className="mt-16 pt-8 border-t-2 border-yellow-400/20">
            <p className="text-yellow-400/50 text-xs font-mono text-center">
              PROMPT INJECTION DETECTION ENGINE v1.0.0 | BUILT FOR PROTECTING LLM APPLICATIONS
            </p>
          </footer>
        </main>
      </div>
    </>
  );
}

