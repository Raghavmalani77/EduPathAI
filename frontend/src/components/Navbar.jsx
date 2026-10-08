import React from 'react';
import { Compass, Briefcase, BookOpen, Info, Home, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, apiStatus }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'pathway', label: 'Find Career Path', icon: Compass },
    { id: 'jobs', label: 'Job Market', icon: Briefcase },
    { id: 'courses', label: 'Course Catalog', icon: BookOpen },
    { id: 'about', label: 'About & XAI', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div 
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={() => setActiveTab('home')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <span className="text-xl">🎓</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  EduPathAI
                </span>
                <span className="text-xs px-2 py-0.5 font-semibold bg-blue-50 text-blue-700 rounded-full border border-blue-200">
                  React 2.0
                </span>
              </div>
              <p className="text-xs text-slate-500 -mt-0.5">AI Student Employability Platform</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-1 sm:gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="hidden md:inline">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Status Indicator */}
          <div className="hidden lg:flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200">
            {apiStatus ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-slate-700">AI Engine Online</span>
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                <span className="text-slate-500">Connecting Engine...</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
