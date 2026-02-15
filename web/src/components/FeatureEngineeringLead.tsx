'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { ArrowRight, Merge, Database } from 'lucide-react';

interface LeadFEData {
  pipeline_steps: Array<{
    step: number;
    name: string;
    features: string | number;
    description: string;
  }>;
  merge_strategy: string;
  missing_data_handling: Array<{
    source: string;
    method: string;
    indicator: string;
  }>;
}

export default function FeatureEngineeringLead() {
  const [data, setData] = useState<LeadFEData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<LeadFEData>('/api/feature-engineering/lead-scoring')
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-pulse text-cyan-400">Loading feature engineering...</div>
      </div>
    );
  }
  if (!data) return <div className="text-amber-500">Failed to load.</div>;

  return (
    <div className="space-y-8 animate-fade-in">
      <header>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Lead Scoring Feature Engineering
        </h1>
        <p className="text-gray-500 mt-1">
          Multi-source merge, missing data handling, cross-source features
        </p>
      </header>

      {/* Pipeline steps */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <Database className="w-5 h-5 text-cyan-400" />
          Pipeline Steps
        </h2>
        <div className="flex flex-wrap items-center gap-4">
          {data.pipeline_steps.map((s, i) => (
            <div key={s.step} className="flex items-center gap-4">
              <div className="w-40 p-4 rounded-xl bg-slate-800/50 border border-cyan-500/20">
                <p className="text-xs text-cyan-400 font-mono">Step {s.step}</p>
                <p className="font-bold text-white mt-1">{s.name}</p>
                <p className="text-sm text-gray-500 mt-1">{s.features}</p>
                <p className="text-xs text-gray-600 mt-2">{s.description}</p>
              </div>
              {i < data.pipeline_steps.length - 1 && (
                <ArrowRight className="w-6 h-6 text-gray-600 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Merge strategy */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Merge className="w-5 h-5 text-emerald-400" />
          Merge Strategy
        </h2>
        <p className="text-gray-400">{data.merge_strategy}</p>
      </section>

      {/* Missing data handling */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Missing Data Handling</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {data.missing_data_handling.map((m) => (
            <div
              key={m.source}
              className="p-4 rounded-lg bg-slate-800/50 border border-amber-500/20"
            >
              <p className="font-medium text-amber-400">{m.source}</p>
              <p className="text-sm text-gray-500 mt-1">Method: {m.method}</p>
              <p className="text-xs text-cyan-400 font-mono mt-2">Indicator: {m.indicator}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
