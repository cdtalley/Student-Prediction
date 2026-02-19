'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
} from 'recharts';
import {
  GraduationCap,
  Users,
  TrendingDown,
  Target,
  AlertTriangle,
  Zap,
  BarChart3,
} from 'lucide-react';

interface StakeholderData {
  retention: {
    stats: {
      total_records: number;
      n_students: number;
      withdrawal_rate: number;
      missing_exit_date_rate: number;
      withdrawn_count: number;
    };
    by_semester: Array<{
      semester: number;
      students: number;
      withdrawn: number;
      withdrawal_rate: number;
    }>;
    risk_distribution: Array<{ range: string; count: number }>;
    gpa_vs_withdrawal: Array<{ gpa_range: string; withdrawal_rate: number }>;
    bands: Array<{
      band: string;
      label: string;
      color: string;
      count: number;
      pct: number;
    }>;
    top_features: Array<{ name: string; importance: number }>;
  };
  lead_scoring: {
    stats: {
      ga4: { records: number; coverage_pct: number };
      crm: { records: number; coverage_pct: number };
      sis: { records: number; coverage_pct: number };
      enrollment_rate: number;
    };
    traffic_sources: Array<{ source: string; leads: number }>;
    enrollment_by_program: Array<{ program: string; enrolled: number }>;
    data_coverage: Array<{ source: string; records: number; coverage: number }>;
    bands: Array<{
      band: string;
      label: string;
      color: string;
      count: number;
      pct: number;
    }>;
    top_features: Array<{ name: string; importance: number }>;
    engagement_summary: Array<{ metric: string; value: number }>;
    lead_scores_sample?: Array<{
      lead_id: number;
      score_1_100: number;
      band: string;
      band_label: string;
      reasons: string[];
      enrolled: number;
    }>;
  };
  coach_list_summary?: Array<{
    school_id: number;
    school_name: string;
    at_risk_count: number;
  }>;
  model_performance: Array<{
    model: string;
    auc: number;
    features: number;
  }>;
}

const COLORS = ['#22d3ee', '#34d399', '#fbbf24', '#a78bfa', '#f472b6', '#38bdf8'];

export default function StakeholderDashboard() {
  const [data, setData] = useState<StakeholderData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<StakeholderData>('/api/stakeholder')
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-cyan-500/30 border-t-cyan-400 rounded-full animate-spin" />
          <p className="text-cyan-400 font-medium">Loading stakeholder dashboard...</p>
        </div>
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] text-center">
        <AlertTriangle className="w-16 h-16 text-amber-500 mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">Unable to load dashboard</h2>
        <p className="text-gray-500 max-w-md">
          {error || 'Ensure the FastAPI backend is running on port 8000 and data has been generated.'}
        </p>
        <p className="text-sm text-gray-600 mt-4">Run: <code className="bg-slate-800 px-2 py-1 rounded">.\run.ps1</code></p>
      </div>
    );
  }

  const { retention, lead_scoring, model_performance } = data;
  const retentionBandsPie = retention.bands.map((b) => ({
    name: `Band ${b.band}`,
    value: b.pct,
    fill: b.color,
  }));
  const leadBandsPie = lead_scoring.bands.map((b) => ({
    name: `Band ${b.band}`,
    value: b.pct,
    fill: b.color,
  }));

  return (
    <div className="space-y-10 animate-fade-in">
      {/* Hero header */}
      <header className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500/10 via-slate-900/80 to-emerald-500/10 border border-white/5 p-8">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(34,211,238,0.15),transparent)]" />
        <div className="relative">
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <BarChart3 className="w-9 h-9 text-cyan-400" />
            Student Prediction Analytics
          </h1>
          <p className="text-gray-500 mt-2 text-lg">
            Executive overview — Retention risk & lead enrollment prediction
          </p>
          <div className="flex flex-wrap gap-6 mt-6">
            <div className="flex items-center gap-2 text-cyan-400">
              <Users className="w-5 h-5" />
              <span>{retention.stats.n_students.toLocaleString()} students</span>
            </div>
            <div className="flex items-center gap-2 text-emerald-400">
              <Target className="w-5 h-5" />
              <span>{lead_scoring.stats.ga4.records.toLocaleString()} leads</span>
            </div>
            <div className="flex items-center gap-2 text-amber-400">
              <Zap className="w-5 h-5" />
              <span>3 ML models • 83%+ AUC</span>
            </div>
          </div>
        </div>
      </header>

      {/* Top KPI cards */}
      <section>
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-cyan-400" />
          Key Performance Indicators
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[
            {
              label: 'Students',
              value: retention.stats.n_students.toLocaleString(),
              icon: Users,
              color: 'from-cyan-500/20 to-cyan-500/5',
              border: 'border-cyan-500/30',
            },
            {
              label: 'Withdrawal Rate',
              value: `${retention.stats.withdrawal_rate}%`,
              icon: TrendingDown,
              color: 'from-amber-500/20 to-amber-500/5',
              border: 'border-amber-500/30',
            },
            {
              label: 'Leads (GA4)',
              value: lead_scoring.stats.ga4.records.toLocaleString(),
              icon: Target,
              color: 'from-emerald-500/20 to-emerald-500/5',
              border: 'border-emerald-500/30',
            },
            {
              label: 'Enrollment Rate',
              value: `${lead_scoring.stats.enrollment_rate}%`,
              icon: Zap,
              color: 'from-violet-500/20 to-violet-500/5',
              border: 'border-violet-500/30',
            },
            {
              label: 'CRM Coverage',
              value: `${lead_scoring.stats.crm.coverage_pct}%`,
              icon: BarChart3,
              color: 'from-pink-500/20 to-pink-500/5',
              border: 'border-pink-500/30',
            },
            {
              label: 'Missing Exit Dates',
              value: `${retention.stats.missing_exit_date_rate}%`,
              icon: AlertTriangle,
              color: 'from-rose-500/20 to-rose-500/5',
              border: 'border-rose-500/30',
            },
          ].map((k) => (
            <div
              key={k.label}
              className={`rounded-xl border ${k.border} bg-gradient-to-br ${k.color} p-5 backdrop-blur`}
            >
              <k.icon className="w-6 h-6 text-gray-500 mb-2" />
              <p className="text-2xl font-bold text-white">{k.value}</p>
              <p className="text-xs text-gray-500 mt-1">{k.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Row 1: Withdrawal by semester + Risk distribution */}
      <section className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Withdrawal Rate by Semester</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={retention.by_semester}>
                <defs>
                  <linearGradient id="withdrawalGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.4} />
                    <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="semester" stroke="#6b7280" tick={{ fontSize: 12 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} unit="%" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                  formatter={(v: number) => [`${v}%`, 'Withdrawal Rate']}
                  labelFormatter={(l) => `Semester ${l}`}
                />
                <Area
                  type="monotone"
                  dataKey="withdrawal_rate"
                  stroke="#22d3ee"
                  strokeWidth={2}
                  fill="url(#withdrawalGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Score Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={retention.risk_distribution} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="range" stroke="#6b7280" tick={{ fontSize: 10 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="count" fill="#34d399" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Row 2: GPA vs Withdrawal + Model Performance */}
      <section className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Withdrawal Rate by GPA Range</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={retention.gpa_vs_withdrawal}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="gpa_range" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} unit="%" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                  formatter={(v: number) => [`${v}%`, 'Withdrawal']}
                />
                <Bar dataKey="withdrawal_rate" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Model Performance (AUC-ROC)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={model_performance} layout="vertical" margin={{ left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} stroke="#6b7280" />
                <YAxis dataKey="model" type="category" width={95} stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                  formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, 'AUC-ROC']}
                />
                <Bar dataKey="auc" fill="#22d3ee" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Row 3: Retention bands donut + Lead bands donut */}
      <section className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Retention Risk Bands</h3>
          <p className="text-sm text-gray-500 mb-4">Student distribution by dropout risk (A=Critical → D=Low)</p>
          <div className="flex items-center gap-6">
            <div className="h-56 w-56 flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={retentionBandsPie}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {retentionBandsPie.map((_, i) => (
                      <Cell key={i} fill={retentionBandsPie[i].fill} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a2332',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                    }}
                    formatter={(v: number) => [`${v}%`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-2">
              {retention.bands.map((b) => (
                <div key={b.band} className="flex items-center justify-between gap-4">
                  <span className="flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: b.color }}
                    />
                    Band {b.band} — {b.label}
                  </span>
                  <span className="font-mono text-sm text-gray-400">
                    {b.count.toLocaleString()} ({b.pct}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Lead Score Bands</h3>
          <p className="text-sm text-gray-500 mb-4">Lead distribution by enrollment likelihood (A=Hot → D=Cold)</p>
          <div className="flex items-center gap-6">
            <div className="h-56 w-56 flex-shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={leadBandsPie}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {leadBandsPie.map((_, i) => (
                      <Cell key={i} fill={leadBandsPie[i].fill} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1a2332',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: '8px',
                    }}
                    formatter={(v: number) => [`${v}%`, '']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-2">
              {lead_scoring.bands.map((b) => (
                <div key={b.band} className="flex items-center justify-between gap-4">
                  <span className="flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: b.color }}
                    />
                    Band {b.band} — {b.label}
                  </span>
                  <span className="font-mono text-sm text-gray-400">
                    {b.count.toLocaleString()} ({b.pct}%)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Row 4: Traffic sources + Enrollment by program */}
      <section className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Traffic Sources (GA4)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={lead_scoring.traffic_sources}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  dataKey="leads"
                  nameKey="source"
                >
                  {lead_scoring.traffic_sources.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                  formatter={(v: number) => [v.toLocaleString(), 'Leads']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Enrollment by Program Interest</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lead_scoring.enrollment_by_program} layout="vertical" margin={{ left: 70 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis dataKey="program" type="category" width={65} stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="enrolled" fill="#34d399" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Row 5: Data coverage + Engagement summary */}
      <section className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Data Source Coverage</h3>
          <p className="text-sm text-gray-500 mb-4">Records and join coverage across GA4, CRM, SIS</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lead_scoring.data_coverage} margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="source" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="records" fill="#22d3ee" radius={[4, 4, 0, 0]} name="Records" />
                <Bar dataKey="coverage" fill="#34d399" radius={[4, 4, 0, 0]} name="Coverage %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">GA4 Engagement Summary</h3>
          <div className="grid grid-cols-2 gap-4">
            {lead_scoring.engagement_summary.map((e) => (
              <div
                key={e.metric}
                className="rounded-lg bg-slate-800/50 border border-white/5 p-4"
              >
                <p className="text-2xl font-bold text-cyan-400">{e.value}</p>
                <p className="text-xs text-gray-500 mt-1">{e.metric}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Coach list: actionable at-risk students per school */}
      {data.coach_list_summary && data.coach_list_summary.length > 0 && (
        <section className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Coach List — At-Risk Students by School
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Top 50 highest-risk students per school for early intervention. Use API /api/coach-list with school_id and top_n for full list and reasons.
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            {data.coach_list_summary.map((s) => (
              <div
                key={s.school_id}
                className="rounded-lg bg-slate-800/50 border border-amber-500/20 p-4"
              >
                <p className="text-xs text-gray-500 truncate" title={s.school_name}>
                  {s.school_name}
                </p>
                <p className="text-2xl font-bold text-amber-400 mt-1">{s.at_risk_count}</p>
                <p className="text-xs text-gray-500">at-risk students</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Lead score 1–100 with reasons */}
      {data.lead_scoring.lead_scores_sample && data.lead_scoring.lead_scores_sample.length > 0 && (
        <section className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
            <Target className="w-5 h-5 text-emerald-400" />
            Lead Score 1–100 (Sample) — With Reasons
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Score from 1 (cold) to 100 (hot) based on engagement, form submits, and CRM/SIS indicators. Use /api/lead-scores?limit= for full list.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-white/10">
                  <th className="pb-2 pr-4">Lead ID</th>
                  <th className="pb-2 pr-4">Score</th>
                  <th className="pb-2 pr-4">Band</th>
                  <th className="pb-2">Reasons</th>
                </tr>
              </thead>
              <tbody>
                {data.lead_scoring.lead_scores_sample.slice(0, 15).map((lead) => (
                  <tr key={lead.lead_id} className="border-b border-white/5">
                    <td className="py-2 pr-4 font-mono text-cyan-400">{lead.lead_id}</td>
                    <td className="py-2 pr-4">
                      <span className="font-bold text-white">{lead.score_1_100}</span>
                      <span className="text-gray-500">/100</span>
                    </td>
                    <td className="py-2 pr-4">
                      <span className="text-gray-400">{lead.band_label}</span>
                    </td>
                    <td className="py-2 text-gray-400">
                      {lead.reasons.length ? lead.reasons.slice(0, 4).join(' • ') : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Row 6: Feature importance side by side */}
      <section className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Retention Model — Top Predictors</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={retention.top_features} layout="vertical" margin={{ left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" width={95} stroke="#6b7280" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                  formatter={(v: number) => [v.toFixed(2) + '%', 'Importance']}
                />
                <Bar dataKey="importance" fill="#22d3ee" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900/40 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Lead Scoring Model — Top Predictors</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lead_scoring.top_features} layout="vertical" margin={{ left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis dataKey="name" type="category" width={95} stroke="#6b7280" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a2332',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px',
                  }}
                  formatter={(v: number) => [v.toFixed(2) + '%', 'Importance']}
                />
                <Bar dataKey="importance" fill="#34d399" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}
