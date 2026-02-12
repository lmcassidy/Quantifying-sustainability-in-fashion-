import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ScoreGauge } from '../components/ScoreGauge';
import { ScoreBreakdown } from '../components/ScoreBreakdown';
import { getRandomProduct } from '../api/client';
import type { ScoreResponse } from '../types';

export function Home() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePreloaded = async () => {
    setLoading(true);
    setError(null);
    try {
      const product = await getRandomProduct();
      setResult(product);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load product');
    } finally {
      setLoading(false);
    }
  };

  const handleInputOwn = () => {
    navigate('/score');
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  // If we have a result, show the score view
  if (result) {
    return (
      <div className="min-h-screen bg-white">
        {/* Header with back arrow */}
        <div className="border-b border-gray-100">
          <div className="max-w-2xl mx-auto px-4 py-4">
            <button
              onClick={handleReset}
              className="text-gray-600 hover:text-gray-900 font-medium flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back
            </button>
          </div>
        </div>

        <div className="max-w-2xl mx-auto px-4 py-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              {result.product_name}
            </h2>
            <p className="text-gray-500">{result.brand}</p>
          </div>

          <div className="flex justify-center mb-8">
            <ScoreGauge score={result.final_score} size="lg" />
          </div>

          <div className="mb-8">
            <ScoreBreakdown
              breakdown={result.breakdown}
              environmentalScore={result.environmental_score}
              certificationBonus={result.certification_bonus}
            />
          </div>

          <div className="flex justify-center">
            <button
              onClick={handlePreloaded}
              className="px-6 py-3 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition-colors"
            >
              Try Another Product
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="max-w-2xl mx-auto px-4 pt-24 pb-16 text-center">
        <h1 className="text-4xl md:text-5xl font-semibold text-gray-900 mb-6 leading-tight">
          Calculate Fashion
          <br />
          Sustainability Score
        </h1>
        <p className="text-lg text-gray-500 mb-12 max-w-lg mx-auto">
          Quantify environmental impact using lifecycle assessment data
        </p>

        {error && (
          <div className="mb-8 p-4 bg-gray-100 text-gray-700 rounded-lg text-sm">
            {error}
            <p className="mt-2 text-gray-500">
              Make sure the API is running: <code className="bg-gray-200 px-1 rounded">make dev-backend</code>
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handlePreloaded}
            disabled={loading}
            className="px-8 py-4 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : 'Use Pre-loaded Product'}
          </button>
          <button
            onClick={handleInputOwn}
            className="px-8 py-4 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors"
          >
            Input Your Own Product
          </button>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="text-center pb-8">
        <div className="inline-flex flex-col items-center text-gray-400">
          <span className="text-sm mb-2">Learn more</span>
          <svg className="w-5 h-5 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="border-t border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-24">
          <h2 className="text-2xl font-semibold text-gray-900 text-center mb-16">
            How It Works
          </h2>

          <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-4">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center max-w-xs">
              <div className="w-16 h-16 rounded-full border-2 border-gray-200 flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 mb-2">Enter Details</h3>
              <p className="text-sm text-gray-500">
                Specify materials, manufacturing origin, care instructions, and certifications
              </p>
            </div>

            {/* Arrow 1 */}
            <div className="hidden md:block text-gray-300">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
            <div className="md:hidden text-gray-300">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center text-center max-w-xs">
              <div className="w-16 h-16 rounded-full border-2 border-gray-200 flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 mb-2">LCA Analysis</h3>
              <p className="text-sm text-gray-500">
                Our algorithm calculates environmental impact using lifecycle assessment data
              </p>
            </div>

            {/* Arrow 2 */}
            <div className="hidden md:block text-gray-300">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </div>
            <div className="md:hidden text-gray-300">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col items-center text-center max-w-xs">
              <div className="w-16 h-16 rounded-full border-2 border-gray-200 flex items-center justify-center mb-4">
                <svg className="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="font-medium text-gray-900 mb-2">Get Your Score</h3>
              <p className="text-sm text-gray-500">
                Receive a 0-100 sustainability score with detailed breakdown by category
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-400">
            Sustainability Scoring System
          </p>
        </div>
      </footer>
    </div>
  );
}
