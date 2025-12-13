/**
 * Main detection page - Clean, modern, friendly design
 */
import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Shield, BarChart3, Zap, CheckCircle, AlertTriangle } from 'lucide-react';
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
        <title>Prompt Injection Detector | Protect Your LLM Applications</title>
        <meta name="description" content="Multi-layer prompt injection detection system" />
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
                <Link href="/analytics" className="text-sm font-medium hover:opacity-70 transition-opacity" style={{ color: '#2D5016' }}>
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
                href="/analytics"
                className="px-5 py-2 rounded-full text-sm font-semibold transition-all playful-hover"
                style={{ backgroundColor: '#87CEEB', color: '#2D5016' }}
              >
                View Analytics
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <main className="max-w-7xl mx-auto px-6 py-16">
          <div className="text-center mb-16 fade-in-up">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight" style={{ color: '#2D5016' }}>
              Unlock{' '}
              <span className="hand-drawn-circle" style={{ color: '#2D5016' }}>
                effortless
              </span>{' '}
              prompt injection protection with world-class detection
            </h1>
            
            {/* Progress bar */}
            <div className="max-w-4xl mx-auto mb-8">
              <div className="progress-bar" style={{ backgroundColor: '#2D5016', height: '4px' }}></div>
            </div>

            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed mb-12">
              Our multi-layer defense system combines rule-based patterns, machine learning models, 
              and behavioral analysis to identify prompt injection attacks with{' '}
              <span className="font-semibold" style={{ color: '#2D5016' }}>84.44% accuracy</span>.
            </p>
          </div>

          {/* Detection Input */}
          <div className="mb-12 fade-in-up">
            <DetectionInput onSubmit={handleDetection} isLoading={loading} />
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-8 max-w-4xl mx-auto p-6 bg-red-50 border-2 border-red-200 rounded-2xl fade-in-up">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="text-red-600" size={24} />
                <p className="text-red-600 font-medium">{error}</p>
              </div>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <div className="fade-in-up">
              <ResultsDisplay result={result} />
            </div>
          )}

          {/* Features Section */}
          {!result && (
            <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
              <div className="clean-card p-8 text-center playful-hover">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ backgroundColor: '#87CEEB' }}>
                  <Shield className="text-white" size={32} />
                </div>
                <h3 className="text-xl font-bold mb-3" style={{ color: '#2D5016' }}>4-Tier Defense</h3>
                <p className="text-gray-600">
                  Multi-layer protection combining validation, detection, intent analysis, and behavioral monitoring
                </p>
              </div>

              <div className="clean-card p-8 text-center playful-hover">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ backgroundColor: '#FFD700' }}>
                  <Zap className="text-white" size={32} />
                </div>
                <h3 className="text-xl font-bold mb-3" style={{ color: '#2D5016' }}>Real-Time Analysis</h3>
                <p className="text-gray-600">
                  Instant detection with sub-second response times and comprehensive threat analysis
                </p>
              </div>

              <div className="clean-card p-8 text-center playful-hover">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ backgroundColor: '#2D5016' }}>
                  <CheckCircle className="text-white" size={32} />
                </div>
                <h3 className="text-xl font-bold mb-3" style={{ color: '#2D5016' }}>High Accuracy</h3>
                <p className="text-gray-600">
                  84.44% overall accuracy with 0% false positive rate on legitimate inputs
                </p>
              </div>
            </div>
          )}

          {/* CTA Section */}
          {!result && (
            <div className="mt-16 flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              <button className="btn-secondary">
                Get Started with Detection
              </button>
              <button className="btn-tertiary">
                View Analytics Dashboard
              </button>
              <button className="btn-primary">
                Try It Now!
              </button>
            </div>
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

