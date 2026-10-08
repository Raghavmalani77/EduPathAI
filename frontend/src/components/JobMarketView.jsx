import React, { useState, useEffect } from 'react';
import { Search, MapPin, Building, Briefcase, Filter, Globe, Sparkles } from 'lucide-react';

export default function JobMarketView({ filters }) {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('All');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchJobs();
  }, [search, selectedCountry]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (selectedCountry && selectedCountry !== 'All') params.append('country', selectedCountry);
      
      const res = await fetch(`/api/jobs?${params.toString()}`);
      const data = await res.json();
      setJobs(data);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-blue-600" />
            Global Job Market Explorer
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Browse and search live job postings ingested into the EduPathAI vector database
          </p>
        </div>
        <div className="text-xs font-semibold px-3 py-1.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
          {jobs.length} Positions Active
        </div>
      </div>

      {/* Filters bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Search by role title, company, skills..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="flex gap-3">
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Regions / Countries</option>
            {filters?.markets?.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Job Cards Grid */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading jobs...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {jobs.map((job) => (
            <div
              key={job.job_id}
              className="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-2xs font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {job.industry}
                  </span>
                  <span className="text-2xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                    {job.country}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-base mb-1 line-clamp-1">{job.title}</h3>
                
                <div className="space-y-1 text-xs text-slate-500 mb-4">
                  <div className="flex items-center gap-1.5">
                    <Building className="w-3.5 h-3.5 text-slate-400" />
                    <span>{job.company}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{job.location}</span>
                  </div>
                </div>
              </div>

              <div>
                <div className="pt-3 border-t border-slate-100">
                  <div className="text-2xs font-semibold uppercase text-slate-400 mb-2">
                    Key Required Skills
                  </div>
                  <div className="flex flex-wrap gap-1.5 max-h-20 overflow-hidden">
                    {job.skills.slice(0, 5).map((sk, idx) => (
                      <span
                        key={idx}
                        className="text-2xs font-medium px-2 py-0.5 rounded-md bg-slate-50 text-slate-700 border border-slate-200"
                      >
                        {sk}
                      </span>
                    ))}
                    {job.skills.length > 5 && (
                      <span className="text-2xs font-semibold text-slate-400 px-1 py-0.5">
                        +{job.skills.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
