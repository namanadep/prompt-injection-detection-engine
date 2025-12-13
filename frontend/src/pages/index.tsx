/**
 * Main detection page - Retro-futuristic hacker aesthetic
 */
import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Shield, BarChart3, Terminal, Zap } from 'lucide-react';
import { DetectionInput } from '../components/DetectionInput';
import { ResultsDisplay } from '../components/ResultsDisplay';
import { DetectionResult, apiClient } from '../services/api';

export default function Home() {
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDetection = async (text: string) => {
    try {
      setLoading(true);
      setError(null);
      const detectionResult = await apiClient.detectInjection(text);
      setResult(detectionResult);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze text');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>PROMPT INJECTION DETECTOR</title>
        <meta name="description" content="Multi-layer prompt injection detection system" />
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
                className="flex items-center space-x-3 px-4 py-3 bg-yellow-400/10 border-l-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400/20 transition-all glitch"
              >
                <Terminal size={18} />
                <span className="text-sm font-mono">DETECTION</span>
              </Link>
              <Link
                href="/analytics"
                className="flex items-center space-x-3 px-4 py-3 hover:bg-yellow-400/10 hover:border-l-2 hover:border-yellow-400/50 text-yellow-400/70 hover:text-yellow-400 transition-all"
              >
                <BarChart3 size={18} />
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
                <span className="text-yellow-400 text-xs font-mono">OWASP LLM#1 PROTECTION</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full neon-glow" style={{ color: '#00FF41' }}></div>
                <span className="text-green-400 text-xs font-mono">84.44% ACCURACY</span>
              </div>
            </div>
            <div className="text-yellow-400/50 text-xs font-mono">
              v1.0.0 | TERMINAL MODE
            </div>
          </div>

          {/* Hero Section */}
          <div className="mb-12">
            <h1 className="text-yellow-400 pixelated neon-glow text-5xl font-bold mb-4 leading-tight">
              PROMPT INJECTION
            </h1>
            <h2 className="text-yellow-400 pixelated neon-glow text-4xl font-bold mb-6">
              DETECTION ENGINE
            </h2>
            <p className="text-green-400 text-lg font-mono max-w-3xl leading-relaxed">
              MULTI-LAYER DEFENSE SYSTEM COMBINING RULE-BASED PATTERNS,
              MACHINE LEARNING MODELS, AND BEHAVIORAL ANALYSIS TO IDENTIFY
              PROMPT INJECTION ATTACKS WITH HIGH ACCURACY.
            </p>
          </div>

          {/* Detection Input */}
          <div className="mb-8">
            <DetectionInput onSubmit={handleDetection} isLoading={loading} />
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 border-2 border-red-400 bg-red-400/10 neon-border" style={{ borderColor: '#FF0000', color: '#FF0000' }}>
              <p className="text-red-400 font-mono text-sm neon-glow">ERROR: {error}</p>
            </div>
          )}

          {/* Results Display */}
          <ResultsDisplay result={result} />

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

