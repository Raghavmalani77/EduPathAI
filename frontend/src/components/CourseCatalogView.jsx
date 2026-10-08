import React, { useState, useEffect } from 'react';
import { BookOpen, Search, Clock, Award, CheckCircle } from 'lucide-react';

export default function CourseCatalogView() {
  const [courses, setCourses] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('All');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCourses();
  }, [search, selectedPlatform]);

  const fetchCourses = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (selectedPlatform && selectedPlatform !== 'All') params.append('platform', selectedPlatform);

      const res = await fetch(`/api/courses?${params.toString()}`);
      const data = await res.json();
      setCourses(data);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
    }
  };

  const platforms = ['All', 'Coursera', 'Udemy', 'edX', 'LinkedIn Learning', 'DataCamp'];

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-indigo-600" />
            Curated Certification & Course Catalog
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Industry-aligned bridge courses indexed with 384-dimensional Sentence-BERT embeddings
          </p>
        </div>
        <div className="text-xs font-semibold px-3 py-1.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
          {courses.length} Courses Indexed
        </div>
      </div>

      {/* Filters bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input
            type="text"
            placeholder="Search courses by title, topic, or skills taught..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="flex gap-3">
          <select
            value={selectedPlatform}
            onChange={(e) => setSelectedPlatform(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm text-slate-800 font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {platforms.map((p) => (
              <option key={p} value={p}>{p === 'All' ? 'All Platforms' : p}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Courses Grid */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading course bridges...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((c) => (
            <div
              key={c.course_id}
              className="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <span className="text-2xs font-extrabold uppercase px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {c.platform}
                  </span>
                  <div className="flex items-center gap-1 text-xs font-semibold text-slate-500">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{c.duration_hours} hrs</span>
                  </div>
                </div>

                <h3 className="font-bold text-slate-900 text-base mb-2 leading-snug">{c.title}</h3>
                <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">{c.description}</p>
              </div>

              <div>
                <div className="pt-3 border-t border-slate-100">
                  <span className="text-2xs font-semibold uppercase text-slate-400 block mb-2">
                    Competencies & Skills Developed
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {c.skills_developed.map((sk, idx) => (
                      <span
                        key={idx}
                        className="text-2xs font-semibold px-2 py-0.5 rounded-md bg-slate-50 text-slate-700 border border-slate-200"
                      >
                        {sk}
                      </span>
                    ))}
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
