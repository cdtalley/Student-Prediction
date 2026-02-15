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
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface LeadPipelineData {
  stats: {
    ga4: { records: number; coverage_pct: number };
    crm: { records: number; coverage_pct: number };
    sis: { records: number; coverage_pct: number };
    enrollment_rate: number;
  };
  join_coverage: Array<{
    source: string;
    records: number;
    coverage: number;
    description: string;
  }>;
  ga4_distributions: Array<{ feature: string; bins: number[]; counts: number[]; mean: number }>;
  source_breakdown: Record<string, number>;
  real_world_issues: Array<{ issue: string; coverage: number; impact: string }>;
}

const SOURCE_COLORS: Record<string, string> = {
  GA4: '#22d3ee',
  CRM: '#34d399',
  SIS: '#fbbf24',
};

export default function DataPipelineLead() {
  const [data, setData] = useState<LeadPipelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<LeadPipelineData>('/api/data-pipeline/lead-scoring')
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-pulse text-cyan-400">Loading pipeline data...</div>
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="text-amber-500">
        {error || 'Failed to load data.'} Ensure the FastAPI backend is running on port 8000.
      </div>
    );
  }

  const { join_coverage, source_breakdown, ga4_distributions, real_world_issues } = data;

  const sourcePieData = Object.entries(source_breakdown).map(([name, value]) => ({
    name,
    value,
    fill: ['#22d3ee', '#34d399', '#fbbf24', '#a78bfa', '#f472b6'][
      Object.keys(source_breakdown).indexOf(name) % 5
    ],
  }));

  return (
    <div className="space-y-8 animate-fade-in">
      <header>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Lead Scoring Data Pipeline
        </h1>
        <p className="text-gray-500 mt-1">
          Multi-source integration: GA4 (web), CRM (marketing), SIS (academic) — mirroring
          incomplete joins and sparse coverage
        </p>
      </header>

      {/* Join coverage flowchart */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-6">Data Source Join Coverage</h2>
        <div className="flex flex-col md:flex-row items-center justify-center gap-4 md:gap-8">
          {join_coverage.map((s, i) => (
            <div key={s.source} className="flex items-center gap-4">
              <div
                className="w-40 p-4 rounded-xl border-2 text-center"
                style={{
                  borderColor: SOURCE_COLORS[s.source] || '#6b7280',
                  backgroundColor: `${SOURCE_COLORS[s.source] || '#6b7280'}15`,
                }}
              >
                <p className="font-bold text-lg" style={{ color: SOURCE_COLORS[s.source] }}>
                  {s.source}
                </p>
                <p className="text-2xl font-mono mt-1">{s.records.toLocaleString()}</p>
                <p className="text-sm text-gray-500 mt-1">{s.coverage}% coverage</p>
                <p className="text-xs text-gray-600 mt-2">{s.description}</p>
              </div>
              {i < join_coverage.length - 1 && (
                <div className="hidden md:block text-gray-600">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Real-world issues */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Real-World Data Challenges</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {real_world_issues.map((issue) => (
            <div
              key={issue.issue}
              className="p-4 rounded-lg bg-slate-800/50 border border-amber-500/20"
            >
              <p className="font-medium text-amber-400">{issue.issue}</p>
              <p className="text-sm text-gray-500 mt-1">{issue.impact}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Traffic source breakdown */}
      <section className="grid md:grid-cols-2 gap-6">
        <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">GA4 Traffic Sources</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sourcePieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {sourcePieData.map((_, i) => (
                    <Cell key={i} fill={sourcePieData[i].fill} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a2332', border: '1px solid rgba(255,255,255,0.1)' }}
                  formatter={(v: number) => [v.toLocaleString(), 'Leads']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* GA4 distributions */}
        <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">GA4 Feature Distributions</h2>
          <div className="space-y-4">
            {ga4_distributions?.slice(0, 4).map((d) => {
              const chartData = d.bins
                ?.slice(0, -1)
                .map((b, i) => ({ bin: b.toFixed(0), count: d.counts[i] || 0 }));
              return (
                <div key={d.feature}>
                  <p className="text-sm text-cyan-400 font-mono mb-1">{d.feature}</p>
                  <div className="h-16">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData || []}>
                        <XAxis dataKey="bin" tick={{ fontSize: 9 }} stroke="#6b7280" />
                        <YAxis hide />
                        <Bar dataKey="count" fill="#22d3ee" radius={[2, 2, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
