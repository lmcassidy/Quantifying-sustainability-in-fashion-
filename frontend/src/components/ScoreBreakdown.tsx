import { useState } from 'react';
import type { ScoreBreakdown as ScoreBreakdownType } from '../types';

interface ScoreBreakdownProps {
  breakdown: ScoreBreakdownType;
  environmentalScore: number;
  certificationBonus: number;
}

interface ImpactBarProps {
  label: string;
  value: number;
}

function ImpactBar({ label, value }: ImpactBarProps) {
  // Monochrome: darker = higher impact (worse)
  const getBarColor = (v: number) => {
    if (v <= 20) return 'bg-gray-300';
    if (v <= 40) return 'bg-gray-400';
    if (v <= 60) return 'bg-gray-500';
    if (v <= 80) return 'bg-gray-600';
    return 'bg-gray-800';
  };

  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{value.toFixed(1)}%</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${getBarColor(value)}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
}

interface AccordionSectionProps {
  title: string;
  isOpen: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

function AccordionSection({ title, isOpen, onToggle, children }: AccordionSectionProps) {
  return (
    <div className="border-b border-gray-100">
      <button
        onClick={onToggle}
        className="w-full py-3 px-4 flex justify-between items-center hover:bg-gray-50 transition-colors"
      >
        <span className="font-medium text-gray-900">{title}</span>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  );
}

export function ScoreBreakdown({ breakdown, environmentalScore, certificationBonus }: ScoreBreakdownProps) {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(['material']));

  const toggleSection = (section: string) => {
    const newSections = new Set(openSections);
    if (newSections.has(section)) {
      newSections.delete(section);
    } else {
      newSections.add(section);
    }
    setOpenSections(newSections);
  };

  // Calculate component averages for the formula display
  const materialAvg = (
    breakdown.material_impact.co2 +
    breakdown.material_impact.water +
    breakdown.material_impact.energy +
    breakdown.material_impact.chemical
  ) / 4;

  const careAvg = (
    breakdown.care_impact.co2 +
    breakdown.care_impact.water +
    breakdown.care_impact.energy
  ) / 3;

  const originAvg = (
    breakdown.origin_impact.grid +
    breakdown.origin_impact.transport +
    breakdown.origin_impact.manufacturing
  ) / 3;

  // Backend averages all 10 metrics equally (not category averages)
  const allMetricsSum = (
    breakdown.material_impact.co2 +
    breakdown.material_impact.water +
    breakdown.material_impact.energy +
    breakdown.material_impact.chemical +
    breakdown.care_impact.co2 +
    breakdown.care_impact.water +
    breakdown.care_impact.energy +
    breakdown.origin_impact.grid +
    breakdown.origin_impact.transport +
    breakdown.origin_impact.manufacturing
  );
  const overallImpact = allMetricsSum / 10;
  const finalScore = Math.min(100, environmentalScore + certificationBonus);

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Summary */}
      <div className="p-4 bg-gray-50 border-b border-gray-100">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-600">Environmental Score</span>
          <span className="font-semibold text-gray-900">{environmentalScore.toFixed(1)}%</span>
        </div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-600">Certification Bonus</span>
          <span className="font-semibold text-gray-900">+{certificationBonus.toFixed(1)}%</span>
        </div>
        <div className="flex justify-between items-center pt-2 border-t border-gray-200">
          <span className="font-medium text-gray-900">Final Score</span>
          <span className="font-bold text-gray-900">{finalScore.toFixed(0)}%</span>
        </div>
      </div>

      {/* Material Impact */}
      <AccordionSection
        title="Material Impact"
        isOpen={openSections.has('material')}
        onToggle={() => toggleSection('material')}
      >
        <p className="text-sm text-gray-500 mb-3">
          Impact from raw material production (lower is better)
        </p>
        <ImpactBar label="Carbon Emissions" value={breakdown.material_impact.co2} />
        <ImpactBar label="Water Usage" value={breakdown.material_impact.water} />
        <ImpactBar label="Energy Consumption" value={breakdown.material_impact.energy} />
        <ImpactBar label="Chemical Impact" value={breakdown.material_impact.chemical} />
      </AccordionSection>

      {/* Care Impact */}
      <AccordionSection
        title="Care Phase Impact"
        isOpen={openSections.has('care')}
        onToggle={() => toggleSection('care')}
      >
        <p className="text-sm text-gray-500 mb-3">
          Impact from garment care during use phase (lower is better)
        </p>
        <ImpactBar label="Carbon Emissions" value={breakdown.care_impact.co2} />
        <ImpactBar label="Water Usage" value={breakdown.care_impact.water} />
        <ImpactBar label="Energy Consumption" value={breakdown.care_impact.energy} />
      </AccordionSection>

      {/* Origin Impact */}
      <AccordionSection
        title="Manufacturing Origin"
        isOpen={openSections.has('origin')}
        onToggle={() => toggleSection('origin')}
      >
        <p className="text-sm text-gray-500 mb-3">
          Impact from manufacturing location (lower is better)
        </p>
        <ImpactBar label="Grid Energy Intensity" value={breakdown.origin_impact.grid} />
        <ImpactBar label="Transport Impact" value={breakdown.origin_impact.transport} />
        <ImpactBar label="Manufacturing Process" value={breakdown.origin_impact.manufacturing} />
      </AccordionSection>

      {/* How is this calculated? */}
      <AccordionSection
        title="How is this calculated?"
        isOpen={openSections.has('formula')}
        onToggle={() => toggleSection('formula')}
      >
        <div className="space-y-4 text-sm">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 mb-2 text-xs font-medium">FORMULA</p>
            <p className="text-gray-900 mb-1">
              <span className="font-medium">Environmental Score</span> = 100 - Average of all 10 impact metrics
            </p>
            <p className="text-gray-600 text-xs mb-2">
              (4 material + 3 care + 3 origin metrics, equally weighted)
            </p>
            <p className="text-gray-900">
              <span className="font-medium">Final Score</span> = Environmental Score + Certification Bonus
            </p>
          </div>

          <div>
            <p className="font-medium text-gray-900 mb-2">Impact by Category:</p>
            <div className="space-y-2 text-gray-600">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="font-medium text-gray-700">Material (4 metrics)</span>
                  <span className="font-mono">{materialAvg.toFixed(1)}%</span>
                </div>
                <p className="text-xs text-gray-500 ml-2">CO2, Water, Energy, Chemical from raw materials</p>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="font-medium text-gray-700">Care Phase (3 metrics)</span>
                  <span className="font-mono">{careAvg.toFixed(1)}%</span>
                </div>
                <p className="text-xs text-gray-500 ml-2">CO2, Water, Energy from washing/drying</p>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="font-medium text-gray-700">Manufacturing Origin (3 metrics)</span>
                  <span className="font-mono">{originAvg.toFixed(1)}%</span>
                </div>
                <p className="text-xs text-gray-500 ml-2">Grid intensity, Transport, Manufacturing process</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-100 rounded-lg p-3 space-y-1">
            <p className="text-xs text-gray-500 mb-2">CALCULATION</p>
            <p className="text-gray-700">
              Average Impact: <span className="font-mono">(sum of 10 metrics) / 10</span> = <span className="font-medium">{overallImpact.toFixed(1)}%</span>
            </p>
            <p className="text-gray-700">
              Environmental: <span className="font-mono">100 - {overallImpact.toFixed(1)}</span> = <span className="font-medium">{(100 - overallImpact).toFixed(1)}%</span>
            </p>
            <p className="text-gray-700">
              Final: <span className="font-mono">{(100 - overallImpact).toFixed(1)} + {certificationBonus.toFixed(1)}</span> = <span className="font-bold">{finalScore.toFixed(0)}%</span>
            </p>
          </div>

          <p className="text-gray-500 text-xs">
            Each metric is normalized 0-100% against reference data. Lower impact = higher sustainability score.
          </p>
        </div>
      </AccordionSection>
    </div>
  );
}
