'use client';

import { useEffect, useState } from 'react';
import { apiFetchWithCache } from '@/lib/api';
import { DataPipelineLoading, DataPipelineError } from '@/components/DataPipelineShell';
import { ChartEmptyState } from '@/components/ChartEmptyState';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface RetentionPipelineData {
  stats: {
    total_records: number;
    n_students: number;
    withdrawal_rate: number;
    missing_exit_date_rate: number;
    withdrawn_count: number;
    missing_by_column: Record<string, number>;
  };
  distributions: Array<{
    feature: string;
    bins: number[];
    counts: number[];
    mean: number;
    std: number;
    missing_pct: number;
  }>;
  correlation_matrix: { features: string[]; values: number[][] };
  real_world_issues: Array<{ issue: string; rate: number; impact: string }>;
}

export default function DataPipelineRetention() {
  const [data, setData] = useState<RetentionPipelineData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetchWithCache<RetentionPipelineData>('/api/data-pipeline/retention')
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <DataPipelineLoading pipeline="retention" />;
  if (error || !data) return <DataPipelineError error={error || 'Failed to load data.'} />;

  const { stats, distributions, real_world_issues } = data;

  return (
    <div className="space-y-8 animate-fade-in">
      <header>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          Student Retention Data Pipeline
        </h1>
        <p className="text-gray-500 mt-1">
          Synthetic data mirroring real-world quality issues: missing exit dates, sparse early
          engagement, class imbalance
        </p>
      </header>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Records', value: stats.total_records.toLocaleString(), color: 'text-cyan-400' },
          { label: 'Students', value: stats.n_students.toLocaleString(), color: 'text-emerald-400' },
          { label: 'Withdrawal Rate', value: `${stats.withdrawal_rate}%`, color: 'text-amber-400' },
          {
            label: 'Missing Exit Dates',
            value: `${stats.missing_exit_date_rate}%`,
            color: 'text-amber-400',
          },
        ].map((s) => (
          <div
            key={s.label}
            className="bg-slate-900/50 border border-white/5 rounded-xl p-5 backdrop-blur"
          >
            <p className="text-gray-500 text-sm">{s.label}</p>
            <p className={`text-xl font-bold mt-1 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Real-world issues */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Real-World Data Quality Issues</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {real_world_issues.map((issue) => (
            <div
              key={issue.issue}
              className="p-4 rounded-lg bg-slate-800/50 border border-amber-500/20"
            >
              <p className="font-medium text-amber-400">{issue.issue}</p>
              <p className="text-sm text-gray-500 mt-1">{issue.impact}</p>
              <p className="text-2xl font-mono text-amber-300 mt-2">{issue.rate}%</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature distributions */}
      <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Feature Distributions</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {distributions.slice(0, 6).map((d) => {
            const chartData = (d.bins || [])
              .slice(0, -1)
              .map((b, i) => ({ bin: Number(b).toFixed(1), count: d.counts?.[i] || 0 }));
            const hasData = chartData.length > 0 && chartData.some((r) => r.count > 0);
            return (
              <div key={d.feature} className="bg-slate-800/30 rounded-lg p-4">
                <p className="font-mono text-sm text-cyan-400 mb-2">{d.feature}</p>
                <div className="h-32">
                  {!hasData ? (
                    <ChartEmptyState message="No distribution" className="min-h-[80px]" />
                  ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <XAxis dataKey="bin" tick={{ fontSize: 10 }} stroke="#6b7280" />
                      <YAxis hide />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1a2332', border: '1px solid rgba(255,255,255,0.1)' }}
                        formatter={(v: number) => [v, 'Count']}
                      />
                      <Bar dataKey="count" fill="#22d3ee" radius={[2, 2, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  μ={d.mean.toFixed(2)} σ={d.std.toFixed(2)} • {d.missing_pct}% missing
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Correlation matrix */}
      {data.correlation_matrix && data.correlation_matrix.features?.length > 0 && (
        <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Feature Correlations</h2>
          <div className="overflow-x-auto">
            <table className="border-collapse">
              <thead>
                <tr>
                  <th className="p-2 text-left text-xs text-gray-500 font-normal" />
                  {data.correlation_matrix.features.slice(0, 10).map((f) => (
                    <th key={f} className="p-1 text-[10px] text-gray-500 w-8" title={f}>
                      {f.replace(/_/g, ' ').slice(0, 6)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.correlation_matrix.values.slice(0, 10).map((row, i) => (
                  <tr key={i}>
                    <td className="p-1 text-[10px] text-gray-500 w-24 truncate" title={data.correlation_matrix.features[i]}>
                      {data.correlation_matrix.features[i].replace(/_/g, ' ').slice(0, 10)}
                    </td>
                    {row.slice(0, 10).map((v, j) => (
                      <td
                        key={j}
                        className="w-8 h-8 rounded text-center text-[10px]"
                        style={{
                          backgroundColor: `rgba(34, 211, 238, ${Math.max(0, (v + 1) / 2)})`,
                          color: Math.abs(v) > 0.5 ? '#0a0f1a' : 'transparent',
                        }}
                        title={`${data.correlation_matrix.features[i]} vs ${data.correlation_matrix.features[j]}: ${v.toFixed(2)}`}
                      >
                        {i === j ? '1' : Math.abs(v) > 0.4 ? v.toFixed(1) : ''}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-500 mt-4">Sampled features • Cyan intensity = correlation strength</p>
        </section>
      )}

      {/* Missing by column */}
      {Object.keys(stats.missing_by_column).length > 0 && (
        <section className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Missing Values by Column</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={Object.entries(stats.missing_by_column).map(([k, v]) => ({
                  name: k,
                  missing: v,
                }))}
                layout="vertical"
                margin={{ left: 120 }}
              >
                <XAxis type="number" domain={[0, 5]} tick={{ fontSize: 11 }} stroke="#6b7280" />
                <YAxis dataKey="name" type="category" width={110} tick={{ fontSize: 11 }} stroke="#6b7280" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a2332', border: '1px solid rgba(255,255,255,0.1)' }}
                  formatter={(v: number) => [`${v}%`, 'Missing']}
                />
                <Bar dataKey="missing" fill="#f59e0b" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}
    </div>
  );
}
