import React, { useState, useEffect } from 'react';
import HomeView from './components/HomeView';
import CareerPathView from './components/CareerPathView';
import JobMarketView from './components/JobMarketView';
import CourseCatalogView from './components/CourseCatalogView';
import AboutView from './components/AboutView';
import { FloatingDock } from './components/ui/FloatingDock';
import {
  IconHome,
  IconRoute,
  IconBriefcase,
  IconBooks,
  IconInfoCircle,
} from '@tabler/icons-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [filters, setFilters] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/filters')
      .then((r) => r.json())
      .then((data) => setFilters(data))
      .catch((err) => console.warn('Could not load filters:', err));

    fetch('/api/stats')
      .then((r) => r.json())
      .then((data) => setStats(data))
      .catch((err) => console.warn('Could not load stats:', err));
  }, []);

  // ── Aceternity Floating Dock navigation items ──────────────────────
  const dockItems = [
    {
      title: "Home",
      icon: <IconHome className="h-full w-full text-neutral-500 dark:text-neutral-300" />,
      href: "#",
      onClick: () => setActiveTab('home'),
    },
    {
      title: "Career Path",
      icon: <IconRoute className="h-full w-full text-neutral-500 dark:text-neutral-300" />,
      href: "#",
      onClick: () => setActiveTab('pathway'),
    },
    {
      title: "Job Market",
      icon: <IconBriefcase className="h-full w-full text-neutral-500 dark:text-neutral-300" />,
      href: "#",
      onClick: () => setActiveTab('jobs'),
    },
    {
      title: "Courses",
      icon: <IconBooks className="h-full w-full text-neutral-500 dark:text-neutral-300" />,
      href: "#",
      onClick: () => setActiveTab('courses'),
    },
    {
      title: "About",
      icon: <IconInfoCircle className="h-full w-full text-neutral-500 dark:text-neutral-300" />,
      href: "#",
      onClick: () => setActiveTab('about'),
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-neutral-950 flex flex-col font-sans transition-colors duration-200">
      {/* Main View Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-4 pb-28">
        {activeTab === 'home' && (
          <HomeView />
        )}
        {activeTab === 'pathway' && (
          <CareerPathView filters={filters} />
        )}
        {activeTab === 'jobs' && (
          <JobMarketView filters={filters} />
        )}
        {activeTab === 'courses' && (
          <CourseCatalogView />
        )}
        {activeTab === 'about' && (
          <AboutView stats={stats} />
        )}
      </main>

      {/* ── Aceternity UI Floating Dock ─────────────────────────────────
           Fixed at the bottom-center of the viewport, z-50.
           Desktop: horizontal spring-magnifying icon bar
           Mobile:  collapsible radial toggle button
      ─────────────────────────────────────────────────────────────────── */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <FloatingDock items={dockItems} />
      </div>
    </div>
  );
}
