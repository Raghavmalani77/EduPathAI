import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomeView from './components/HomeView';
import CareerPathView from './components/CareerPathView';
import JobMarketView from './components/JobMarketView';
import CourseCatalogView from './components/CourseCatalogView';
import AboutView from './components/AboutView';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState(null);
  const [apiStatus, setApiStatus] = useState(false);

  useEffect(() => {
    checkHealthAndFetchStats();
  }, []);

  const checkHealthAndFetchStats = async () => {
    try {
      const [healthRes, statsRes, filterRes] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/stats'),
        fetch('/api/filters')
      ]);

      if (healthRes.ok) setApiStatus(true);
      const statsData = await statsRes.json();
      const filterData = await filterRes.json();

      setStats(statsData);
      setFilters(filterData);
    } catch (err) {
      console.warn('API not ready yet, will retry...', err);
      setApiStatus(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        apiStatus={apiStatus} 
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activeTab === 'home' && (
          <HomeView stats={stats} onNavigate={setActiveTab} />
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

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div>
            <span className="font-semibold text-slate-700">EduPathAI Platform</span> — AI Student Learning, Employability & Career Pathway System
          </div>
          <div>
            Phase 7 ML Architecture • Sentence-BERT • React 19 + Vite + Tailwind
          </div>
        </div>
      </footer>
    </div>
  );
}
