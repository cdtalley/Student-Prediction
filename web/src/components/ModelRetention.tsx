'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, Award, Phone } from 'lucide-react';
import { ChartEmptyState } from '@/components/ChartEmptyState';

interface RetentionBand {
  band: string;
  label: string;
  min: number;
  max: number;
  color: string;
  intervention: string;
  actions: string[];
  count?: number;
  pct?: number;
}

interface RetentionModelData {
  early_semester: {
    auc: number;
    features: number;
    feature_importance: [string, number][];
  };
  mid_semester: {
    auc: number;
    features: number;
    feature_importance: [string, number][];
  };
  score_bands?: RetentionBand[];
}

interface ScoreBandsResponse {
  bands: (RetentionBand & { count: number; pct: number })[];
  total: number;
}

export default function ModelRetention() {
  const [data, setData] = useState<RetentionModelData | null>(null);
  const [bandsData, setBandsData] = useState<ScoreBandsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiFetch<RetentionModelData>('/api/models/retention'),
      apiFetch<ScoreBandsResponse>('/api/score-bands/retention'),
    ])
      .then(([modelData, bands]) => {
        setData(modelData);
        setBandsData(bands);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-pulse text-cyan-400">Loading model metrics...</div>
      </div>
    );
  }
  if (!data) return <div className="text-amber-500">Failed to load.</div>;

  const midImp = data.mid_semester.feature_importance.slice(0, 12).map(([n, v]) => ({
    name: n.replace(/_/g, ' '),
    value: v * 100,
  }));

  return (
    <div className="space-y-8 animate-fade-in">
      <header>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Retention Models
        </h1>
        <p className="text-gray-500 mt-1">
          Early vs mid-semester prediction with XGBoost
        </p>
      </header>

      {/* Model cards */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Early Semester</h2>
            <span className="px-3 py-1 rounded-full bg-cyan-500/20 text-cyan-400 text-sm">
              {data.early_semester.features} features
            </span>
          </div>
          <div className="mt-4 flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Award className="w-8 h-8 text-cyan-400" />
              <div>
                <p className="text-3xl font-bold text-cyan-400">
                  {(data.early_semester.auc * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500">AUC-ROC</p>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Mid-Semester</h2>
            <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-sm">
              {data.mid_semester.features} features
            </span>
          </div>
          <div className="mt-4 flex items-center gap-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-emerald-400" />
              <div>
                <p className="text-3xl font-bold text-emerald-400">
                  {(data.mid_semester.auc * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500">AUC-ROC</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Score bands & interventions */}
      {bandsData && (
        <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">
            Risk Score Bands & Interventions
          </h2>
          <p className="text-sm text-gray-500 mb-6">
            Students segmented by dropout risk. Each band maps to a specific intervention.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {bandsData.bands.map((b) => (
              <div
                key={b.band}
                className="rounded-xl border overflow-hidden"
                style={{ borderColor: `${b.color}40`, backgroundColor: `${b.color}10` }}
              >
                <div
                  className="px-4 py-3 font-bold text-lg"
                  style={{ color: b.color, backgroundColor: `${b.color}20` }}
                >
                  Band {b.band} — {b.label}
                </div>
                <div className="p-4 space-y-3">
                  <p className="text-xs text-gray-500 font-mono">
                    Score: {(b.min * 100).toFixed(0)}%–{(b.max * 100).toFixed(0)}%
                  </p>
                  <p className="text-sm text-white font-medium">{b.intervention}</p>
                  <div className="flex items-center gap-2 text-cyan-400 text-sm">
                    <Phone className="w-4 h-4 flex-shrink-0" />
                    <span>Actions:</span>
                  </div>
                  <ul className="text-xs text-gray-400 space-y-1 ml-6">
                    {b.actions.map((a) => (
                      <li key={a}>• {a}</li>
                    ))}
                  </ul>
                  {(b.count !== undefined || b.pct !== undefined) && (
                    <p className="text-sm font-mono pt-2 border-t border-white/10">
                      {b.count?.toLocaleString()} students ({b.pct}%)
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Feature importance */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">
          Mid-Semester Model — Feature Importance
        </h2>
        <div className="h-80">
          {!midImp.length ? (
            <ChartEmptyState message="No feature importance data" className="min-h-[200px]" />
          ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={midImp} layout="vertical" margin={{ left: 140 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} stroke="#6b7280" />
              <YAxis
                dataKey="name"
                type="category"
                width={130}
                tick={{ fontSize: 11 }}
                stroke="#6b7280"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a2332',
                  border: '1px solid rgba(255,255,255,0.1)',
                }}
                formatter={(v: number) => [v.toFixed(2) + '%', 'Importance']}
              />
              <Bar dataKey="value" fill="#22d3ee" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
          )}
        </div>
      </section>
    </div>
  );
}
