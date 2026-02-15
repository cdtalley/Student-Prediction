'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { ArrowRight, Cpu, Layers } from 'lucide-react';

interface FEData {
  pipeline_steps: Array<{
    step: number;
    name: string;
    features: number;
    description: string;
  }>;
  early_features: Array<{ name: string; type: string }>;
  mid_additions: string[];
  transformations: Array<{ input: string; output: string; method: string }>;
}

export default function FeatureEngineeringRetention() {
  const [data, setData] = useState<FEData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch<FEData>('/api/feature-engineering/retention')
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
          Retention Feature Engineering
        </h1>
        <p className="text-gray-500 mt-1">
          From raw demographics to early/mid-semester predictive features
        </p>
      </header>

      {/* Pipeline flow */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          Pipeline Steps
        </h2>
        <div className="flex flex-wrap items-center gap-4">
          {data.pipeline_steps.map((s, i) => (
            <div key={s.step} className="flex items-center gap-4">
              <div className="w-48 p-4 rounded-xl bg-slate-800/50 border border-cyan-500/20">
                <p className="text-xs text-cyan-400 font-mono">Step {s.step}</p>
                <p className="font-bold text-white mt-1">{s.name}</p>
                <p className="text-sm text-gray-500 mt-1">{s.features} features</p>
                <p className="text-xs text-gray-600 mt-2">{s.description}</p>
              </div>
              {i < data.pipeline_steps.length - 1 && (
                <ArrowRight className="w-6 h-6 text-gray-600 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Transformations */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-emerald-400" />
          Key Transformations
        </h2>
        <div className="space-y-4">
          {data.transformations.map((t) => (
            <div
              key={t.output}
              className="flex flex-col md:flex-row md:items-center gap-2 p-4 rounded-lg bg-slate-800/30 border border-white/5"
            >
              <span className="font-mono text-sm text-gray-500">{t.input}</span>
              <ArrowRight className="w-4 h-4 text-gray-600 hidden md:block" />
              <span className="font-mono text-cyan-400">{t.output}</span>
              <span className="text-sm text-gray-500 md:ml-auto">→ {t.method}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Early vs Mid features */}
      <section className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Early Semester Features (15)</h2>
          <div className="flex flex-wrap gap-2">
            {data.early_features.map((f) => (
              <span
                key={f.name}
                className={`px-2 py-1 rounded text-xs font-mono ${
                  f.type === 'demographic'
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : f.type === 'academic'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : f.type === 'engagement'
                    ? 'bg-amber-500/20 text-amber-400'
                    : 'bg-purple-500/20 text-purple-400'
                }`}
              >
                {f.name}
              </span>
            ))}
          </div>
        </div>
        <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Mid-Semester Additions (9)</h2>
          <div className="flex flex-wrap gap-2">
            {data.mid_additions.map((f) => (
              <span
                key={f}
                className="px-2 py-1 rounded text-xs font-mono bg-amber-500/20 text-amber-400"
              >
                {f}
              </span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
