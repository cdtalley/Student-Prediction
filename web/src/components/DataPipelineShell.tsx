'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, Database, Loader2 } from 'lucide-react';
import { BACKEND_HELP } from '@/lib/api';

const LOADING_MESSAGES = [
  'Crunching numbers…',
  'Merging data sources…',
  'Building pipelines…',
  'Almost there…',
];

export function DataPipelineLoading({ pipeline = 'data' }: { pipeline?: 'retention' | 'lead' | 'data' }) {
  const [msgIndex, setMsgIndex] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setMsgIndex((i) => (i + 1) % LOADING_MESSAGES.length), 2000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      <header>
        <div className="h-8 w-64 bg-slate-700/50 rounded-lg animate-pulse" />
        <div className="h-4 w-96 mt-2 bg-slate-800/50 rounded animate-pulse" />
      </header>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-24 bg-slate-800/50 border border-white/5 rounded-xl animate-pulse"
          />
        ))}
      </div>
      <div className="flex flex-col items-center justify-center py-12 gap-6">
        <div className="flex items-center gap-3 text-cyan-400">
          <Loader2 className="w-8 h-8 animate-spin" />
          <Database className="w-8 h-8 opacity-70" />
        </div>
        <div className="w-full max-w-sm h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full animate-pulse"
            style={{ width: '50%' }}
          />
        </div>
        <p className="text-cyan-400 font-medium">{LOADING_MESSAGES[msgIndex]}</p>
        <p className="text-sm text-gray-500">
          {pipeline === 'retention' && 'Loading retention pipeline…'}
          {pipeline === 'lead' && 'Loading lead scoring pipeline…'}
          {pipeline === 'data' && 'Loading pipeline data…'}
        </p>
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-32 bg-slate-800/30 rounded-xl border border-white/5 animate-pulse" />
        ))}
      </div>
    </div>
  );
}

export function DataPipelineError({ error }: { error: string }) {
  const isBackendDown = error.includes('Cannot reach') || error.includes('fetch') || error.includes('Network');
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <AlertTriangle className="w-16 h-16 text-amber-500 mb-4" />
      <h2 className="text-xl font-bold text-white mb-2">Couldn’t load pipeline data</h2>
      <p className="text-gray-400 max-w-lg">{error || BACKEND_HELP}</p>
      <div className="mt-6 text-left space-y-2 rounded-xl bg-slate-800/60 border border-white/10 p-4 max-w-md">
        <p className="text-cyan-400 font-medium text-sm">From project root:</p>
        <code className="block text-sm text-gray-300 bg-slate-900 px-3 py-2 rounded">
          python -m uvicorn api.main:app --port 8000
        </code>
        <p className="text-amber-400/90 text-sm">Then generate data (if needed):</p>
        <code className="block text-sm text-gray-300 bg-slate-900 px-3 py-2 rounded">
          python src/train.py
        </code>
      </div>
      {!isBackendDown && (
        <p className="text-sm text-gray-500 mt-4">
          Or run <code className="bg-slate-800 px-2 py-1 rounded">.\run.ps1</code>
        </p>
      )}
    </div>
  );
}
