/**
 * Main detection page.
 */
import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { Shield, BarChart3 } from 'lucide-react';
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
        <title>Prompt Injection Detection Engine</title>
        <meta name="description" content="Multi-layer prompt injection detection system" />
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
                    Prompt Injection Detection Engine
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    OWASP LLM#1 Threat Protection
                  </p>
                </div>
              </div>
              <Link
                href="/analytics"
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors"
              >
                <BarChart3 size={18} />
                <span>Analytics</span>
              </Link>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Description */}
          <div className="mb-8 text-center">
            <p className="text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              This system uses a multi-layer detection approach combining rule-based patterns,
              machine learning models, and vector similarity matching to identify prompt injection attacks
              with high accuracy.
            </p>
          </div>

          {/* Detection Input */}
          <DetectionInput onSubmit={handleDetection} isLoading={loading} />

          {/* Error Display */}
          {error && (
            <div className="mt-6 max-w-4xl mx-auto p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Results Display */}
          <ResultsDisplay result={result} />
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

