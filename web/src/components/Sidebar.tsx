'use client';

import { clsx } from 'clsx';
import {
  Database,
  Workflow,
  BarChart3,
  GraduationCap,
  Target,
  ChevronRight,
} from 'lucide-react';

type View =
  | 'retention-pipeline'
  | 'lead-pipeline'
  | 'retention-fe'
  | 'lead-fe'
  | 'retention-model'
  | 'lead-model';

interface SidebarProps {
  view: View;
  onViewChange: (v: View) => void;
}

const navItems: { id: View; label: string; icon: React.ReactNode }[] = [
  { id: 'retention-pipeline', label: 'Retention Data Pipeline', icon: <Database className="w-5 h-5" /> },
  { id: 'lead-pipeline', label: 'Lead Scoring Data Pipeline', icon: <Database className="w-5 h-5" /> },
  { id: 'retention-fe', label: 'Retention Feature Engineering', icon: <Workflow className="w-5 h-5" /> },
  { id: 'lead-fe', label: 'Lead Feature Engineering', icon: <Workflow className="w-5 h-5" /> },
  { id: 'retention-model', label: 'Retention Models', icon: <GraduationCap className="w-5 h-5" /> },
  { id: 'lead-model', label: 'Lead Scoring Model', icon: <Target className="w-5 h-5" /> },
];

export default function Sidebar({ view, onViewChange }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-slate-950/95 border-r border-white/5 flex flex-col">
      <div className="p-6 border-b border-white/5">
        <h1 className="font-bold text-lg tracking-tight text-cyan-400 flex items-center gap-2">
          <BarChart3 className="w-6 h-6" />
          Student Prediction
        </h1>
        <p className="text-xs text-gray-500 mt-1">Analytics Platform</p>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-auto">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onViewChange(item.id)}
            className={clsx(
              'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left text-sm transition-all',
              view === item.id
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
            )}
          >
            {item.icon}
            <span className="flex-1">{item.label}</span>
            <ChevronRight
              className={clsx('w-4 h-4 transition', view === item.id && 'opacity-100')}
            />
          </button>
        ))}
      </nav>
    </aside>
  );
}
