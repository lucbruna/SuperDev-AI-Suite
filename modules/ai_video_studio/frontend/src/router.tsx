import { Suspense, lazy } from 'react';
import { Route, Routes } from 'react-router-dom';
import { Spinner } from '@/ui';
import GuestLayout from '@/layout/GuestLayout';
import MainLayout from '@/layout/MainLayout';
import DashboardLayout from '@/layout/DashboardLayout';
import EditorLayout from '@/layout/EditorLayout';
import StudioLayout from '@/layout/StudioLayout';
import AdminLayout from '@/layout/AdminLayout';

// Pages are lazy-loaded; every page module must default-export a component.
const Login = lazy(() => import('@/pages/Login'));
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Projects = lazy(() => import('@/pages/Projects'));
const Editor = lazy(() => import('@/pages/Editor'));
const Assets = lazy(() => import('@/pages/Assets'));
const Marketplace = lazy(() => import('@/pages/Marketplace'));
const AvatarStudio = lazy(() => import('@/pages/AvatarStudio'));
const VoiceStudio = lazy(() => import('@/pages/VoiceStudio'));
const RenderCenter = lazy(() => import('@/pages/RenderCenter'));
const Analytics = lazy(() => import('@/pages/Analytics'));
const Settings = lazy(() => import('@/pages/Settings'));
const Collaboration = lazy(() => import('@/pages/Collaboration'));
const Admin = lazy(() => import('@/pages/Admin'));

function PageFallback() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Spinner size="lg" />
    </div>
  );
}

export default function AppRoutes() {
  return (
    <Suspense fallback={<PageFallback />}>
      <Routes>
        <Route path="/login" element={<GuestLayout />}>
          <Route index element={<Login />} />
        </Route>
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
        </Route>
        <Route path="/editor" element={<EditorLayout />}>
          <Route index element={<Editor />} />
        </Route>
        <Route path="/assets" element={<MainLayout />}>
          <Route index element={<Assets />} />
        </Route>
        <Route path="/marketplace" element={<MainLayout />}>
          <Route index element={<Marketplace />} />
        </Route>
        <Route path="/avatar" element={<StudioLayout />}>
          <Route index element={<AvatarStudio />} />
        </Route>
        <Route path="/voice" element={<StudioLayout />}>
          <Route index element={<VoiceStudio />} />
        </Route>
        <Route path="/render" element={<MainLayout />}>
          <Route index element={<RenderCenter />} />
        </Route>
        <Route path="/analytics" element={<MainLayout />}>
          <Route index element={<Analytics />} />
        </Route>
        <Route path="/settings" element={<MainLayout />}>
          <Route index element={<Settings />} />
        </Route>
        <Route path="/collaboration" element={<MainLayout />}>
          <Route index element={<Collaboration />} />
        </Route>
        <Route path="/admin/*" element={<AdminLayout />}>
          <Route index element={<Admin />} />
          <Route path="*" element={<Admin />} />
        </Route>
        <Route path="*" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
