import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ScoreForm } from '../components/ScoreForm';
import { ScoreGauge } from '../components/ScoreGauge';
import { ScoreBreakdown } from '../components/ScoreBreakdown';
import { scoreProduct } from '../api/client';
import type { ProductInput, ScoreResponse } from '../types';

export function ScoreProduct() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ScoreResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastInput, setLastInput] = useState<ProductInput | null>(null);

  const handleSubmit = async (product: ProductInput) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setLastInput(product);

    try {
      const scoreResult = await scoreProduct(product);
      setResult(scoreResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to calculate score');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setLastInput(null);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back
          </Link>
          <h1 className="text-lg font-semibold text-gray-900">Score a Product</h1>
          <div className="w-16"></div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {!result ? (
          <>
            {error && (
              <div className="bg-gray-100 text-gray-700 p-4 rounded-lg mb-6">
                <p className="font-medium">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            )}
            <ScoreForm onSubmit={handleSubmit} isLoading={isLoading} />
          </>
        ) : (
          <div className="space-y-8">
            {/* Score Result */}
            <div className="bg-white rounded-lg border border-gray-200 p-8">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  {result.product_name}
                </h2>
                <p className="text-gray-500">{result.brand}</p>
              </div>

              <div className="flex justify-center mb-8">
                <ScoreGauge score={result.final_score} size="lg" />
              </div>

              {/* Quick Summary */}
              {lastInput && (
                <div className="border-t border-gray-100 pt-6 mt-6">
                  <h3 className="font-medium text-gray-900 mb-3">Product Summary</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Materials:</span>
                      <p className="font-medium text-gray-900">
                        {lastInput.materials.map(m => `${m.name} (${m.percentage}%)`).join(', ')}
                      </p>
                    </div>
                    <div>
                      <span className="text-gray-500">Origin:</span>
                      <p className="font-medium text-gray-900">{lastInput.origin}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Care:</span>
                      <p className="font-medium text-gray-900">{lastInput.care_instruction}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Certifications:</span>
                      <p className="font-medium text-gray-900">
                        {[lastInput.certification1, lastInput.certification2]
                          .filter(c => c && c !== 'No Certification')
                          .join(', ') || 'None'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Detailed Breakdown */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Score Breakdown
              </h3>
              <ScoreBreakdown
                breakdown={result.breakdown}
                environmentalScore={result.environmental_score}
                certificationBonus={result.certification_bonus}
              />
            </div>

            {/* Actions */}
            <div className="flex justify-center">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition-colors"
              >
                Score Another Product
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
