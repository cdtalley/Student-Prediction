'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import StakeholderDashboard from '@/components/StakeholderDashboard';
import DataPipelineRetention from '@/components/DataPipelineRetention';
import DataPipelineLead from '@/components/DataPipelineLead';
import FeatureEngineeringRetention from '@/components/FeatureEngineeringRetention';
import FeatureEngineeringLead from '@/components/FeatureEngineeringLead';
import ModelRetention from '@/components/ModelRetention';
import ModelLead from '@/components/ModelLead';

type View =
  | 'stakeholder'
  | 'retention-pipeline'
  | 'lead-pipeline'
  | 'retention-fe'
  | 'lead-fe'
  | 'retention-model'
  | 'lead-model';

export default function Home() {
  const [view, setView] = useState<View>('stakeholder');

  return (
    <div className="flex min-h-screen">
      <Sidebar view={view} onViewChange={setView} />
      <main className="flex-1 ml-64 p-8 overflow-auto">
        {view === 'stakeholder' && <StakeholderDashboard />}
        {view === 'retention-pipeline' && <DataPipelineRetention />}
        {view === 'lead-pipeline' && <DataPipelineLead />}
        {view === 'retention-fe' && <FeatureEngineeringRetention />}
        {view === 'lead-fe' && <FeatureEngineeringLead />}
        {view === 'retention-model' && <ModelRetention />}
        {view === 'lead-model' && <ModelLead />}
      </main>
    </div>
  );
}
