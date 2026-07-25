import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { Organizations } from './pages/Organizations';
import { Projects } from './pages/Projects';
import { Workflows } from './pages/Workflows';
import { Agents } from './pages/Agents';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { Plugins } from './pages/Plugins';
import { FeatureFlags } from './pages/FeatureFlags';
import { Settings } from './pages/Settings';
import { Layout } from './components/Layout';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/organizations" element={<Organizations />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/workflows" element={<Workflows />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/knowledge-base" element={<KnowledgeBase />} />
        <Route path="/plugins" element={<Plugins />} />
        <Route path="/feature-flags" element={<FeatureFlags />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;