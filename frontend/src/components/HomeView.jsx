import React from 'react';
import { ArrowRight, Sparkles, Target, BookOpen, Layers, Users, Briefcase, Award, TrendingUp } from 'lucide-react';

export default function HomeView({ stats, onNavigate }) {
  const cards = [
    {
      icon: Target,
      color: 'from-blue-500 to-indigo-600',
      bgColor: 'bg-blue-50 text-blue-600',
      title: 'AI Job Matching',
      description: 'Dense semantic skill analysis aligns student capabilities with real-time global industry opportunities.'
    },
    {
      icon: TrendingUp,
      color: 'from-amber-500 to-orange-600',
      bgColor: 'bg-amber-50 text-amber-600',
      title: 'Precision Skill Gap Analysis',
      description: 'Pinpoints the exact delta between your current proficiencies and what high-paying industry roles require.'
    },
    {
      icon: BookOpen,
      color: 'from-emerald-500 to-teal-600',
      bgColor: 'bg-emerald-50 text-emerald-600',
      title: 'Smart Course Bridges',
      description: 'Prescribes tailored course recommendations via Greedy Set-Cover optimization to close skill gaps with minimum duration.'
    }
  ];

  return (
    <div className="space-y-12 pb-16">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-700 via-indigo-700 to-cyan-600 text-white p-8 sm:p-14 shadow-xl shadow-blue-900/10">
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/15 backdrop-blur-md text-xs font-semibold uppercase tracking-wider text-blue-100 border border-white/20">
            <Sparkles className="w-4 h-4 text-amber-300" />
            Phase 7 ML Recommendation Architecture
          </div>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Discover Your Perfect Career Path with AI
          </h1>
          <p className="text-lg sm:text-xl text-blue-100/90 leading-relaxed max-w-2xl">
            Get personalized job matches, identify hidden skill gaps, and explore explainable course pathways designed to land your dream role.
          </p>
          <div className="pt-2 flex flex-wrap gap-4">
            <button
              onClick={() => onNavigate('pathway')}
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white text-blue-700 font-bold text-sm sm:text-base hover:bg-blue-50 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
            >
              Get Started → Find My Career Path
              <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={() => onNavigate('jobs')}
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm sm:text-base backdrop-blur-md transition-all border border-white/20"
            >
              Explore Job Postings
            </button>
          </div>
        </div>

        {/* Decorative backdrop shapes */}
        <div className="absolute -right-20 -bottom-20 w-96 h-96 bg-white/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute right-40 -top-20 w-72 h-72 bg-cyan-400/20 rounded-full blur-2xl pointer-events-none"></div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((c, i) => {
          const Icon = c.icon;
          return (
            <div
              key={i}
              className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-sm hover:shadow-md transition-all hover:-translate-y-1 flex flex-col justify-between"
            >
              <div>
                <div className={`w-12 h-12 rounded-xl ${c.bgColor} flex items-center justify-center mb-5`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{c.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{c.description}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live System Metrics */}
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
        <div className="text-center max-w-xl mx-auto mb-8">
          <h2 className="text-xl font-bold text-slate-900">Enterprise AI Infrastructure Metrics</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">Live data ingested and processed in the system</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center divide-y md:divide-y-0 md:divide-x divide-slate-100">
          <div className="pt-4 md:pt-0">
            <div className="text-3xl sm:text-4xl font-extrabold text-blue-600 tracking-tight">
              {stats?.students_count ? `${stats.students_count}+` : '480+'}
            </div>
            <div className="text-xs uppercase font-semibold text-slate-500 tracking-wider mt-1">
              Students Analyzed
            </div>
          </div>
          <div className="pt-4 md:pt-0">
            <div className="text-3xl sm:text-4xl font-extrabold text-indigo-600 tracking-tight">
              {stats?.jobs_count || '176'}
            </div>
            <div className="text-xs uppercase font-semibold text-slate-500 tracking-wider mt-1">
              Job Postings Tracked
            </div>
          </div>
          <div className="pt-4 md:pt-0">
            <div className="text-3xl sm:text-4xl font-extrabold text-cyan-600 tracking-tight">
              {stats?.courses_count || '28'}
            </div>
            <div className="text-xs uppercase font-semibold text-slate-500 tracking-wider mt-1">
              Curated Courses
            </div>
          </div>
          <div className="pt-4 md:pt-0">
            <div className="text-3xl sm:text-4xl font-extrabold text-emerald-600 tracking-tight">
              {stats?.skills_count || '66'}
            </div>
            <div className="text-xs uppercase font-semibold text-slate-500 tracking-wider mt-1">
              Continuous Skill Vectors
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Steps */}
      <div className="space-y-6">
        <div className="text-center max-w-xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-900">How EduPathAI Works</h2>
          <p className="text-sm text-slate-500 mt-1">A transparent, explainable 4-step recommendation pipeline</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            { step: '01', title: 'Student Profiling', desc: 'Ingests academic records, GPA, skills, and LMS engagement logs.' },
            { step: '02', title: 'Vector Matching', desc: 'Computes cosine similarity across 66-D skill space and target job seniority.' },
            { step: '03', title: 'Gap Detection', desc: 'Identifies technical and soft skill deficits between profile and job.' },
            { step: '04', title: 'Curriculum Bridges', desc: 'Applies S-BERT dense embeddings & Greedy Set Cover to recommend courses.' }
          ].map((s, idx) => (
            <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200/80 relative">
              <span className="text-2xl font-black text-blue-600/30 mb-2 block">{s.step}</span>
              <h4 className="font-bold text-slate-900 mb-1">{s.title}</h4>
              <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
