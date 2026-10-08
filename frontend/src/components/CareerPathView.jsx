import React, { useState, useEffect } from 'react';
import RadarChartSvg from './RadarChartSvg';
import { 
  Sparkles, UserCheck, Compass, Briefcase, Award, CheckCircle2, AlertTriangle, 
  BookOpen, ChevronRight, Filter, RefreshCw, Send, Star, Zap
} from 'lucide-react';

export default function CareerPathView({ filters }) {
  const [mode, setMode] = useState('existing'); // 'existing' or 'custom'
  
  // Existing student mode state
  const [selectedInterest, setSelectedInterest] = useState('All');
  const [selectedMarket, setSelectedMarket] = useState('All');
  const [students, setStudents] = useState([]);
  const [selectedStudentId, setSelectedStudentId] = useState('');
  
  // Student details & match results
  const [studentDetails, setStudentDetails] = useState(null);
  const [matchData, setMatchData] = useState(null);
  const [selectedJobIndex, setSelectedJobIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  
  // Custom profile form state
  const [customForm, setCustomForm] = useState({
    name: 'Jane Doe',
    degree: 'B.Tech',
    specialisation: 'Computer Science',
    gpa: 7.8,
    career_interest: 'Data Scientist',
    technical_skills: ['Python', 'SQL', 'Machine Learning', 'Data Analysis'],
    soft_skills: ['Problem Solving', 'Communication', 'Teamwork'],
    market: 'All'
  });

  // Fetch student list when career interest filter changes
  useEffect(() => {
    fetchStudents();
  }, [selectedInterest]);

  const fetchStudents = async () => {
    try {
      const url = selectedInterest === 'All' 
        ? '/api/students' 
        : `/api/students?career_interest=${encodeURIComponent(selectedInterest)}`;
      const res = await fetch(url);
      const data = await res.json();
      setStudents(data);
      if (data.length > 0) {
        setSelectedStudentId(data[0].student_id);
      }
    } catch (err) {
      console.error('Failed to fetch students:', err);
    }
  };

  // Fetch student details and match recommendations when student ID or market changes
  useEffect(() => {
    if (selectedStudentId && mode === 'existing') {
      loadStudentData(selectedStudentId, selectedMarket);
    }
  }, [selectedStudentId, selectedMarket, mode]);

  const loadStudentData = async (studentId, market) => {
    setLoading(true);
    try {
      const [detailRes, matchRes] = await Promise.all([
        fetch(`/api/student/${studentId}`),
        fetch(`/api/match/${studentId}?market=${encodeURIComponent(market)}&top_n=3`)
      ]);
      const detailData = await detailRes.json();
      const matchData = await matchRes.json();
      setStudentDetails(detailData);
      setMatchData(matchData);
      setSelectedJobIndex(0);
    } catch (err) {
      console.error('Failed to load student details or matches:', err);
    } finally {
      setLoading(false);
    }
  };

  // Custom profile submission
  const handleCustomSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/custom-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customForm)
      });
      const data = await res.json();
      
      // Also fetch the synthetic student details
      const detailRes = await fetch('/api/student/CUSTOM_USER');
      const detailData = await detailRes.json();
      
      setStudentDetails(detailData);
      setMatchData(data);
      setSelectedJobIndex(0);
    } catch (err) {
      console.error('Failed to create custom profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleSkill = (skillListKey, skill) => {
    setCustomForm(prev => {
      const current = prev[skillListKey];
      const exists = current.includes(skill);
      return {
        ...prev,
        [skillListKey]: exists ? current.filter(s => s !== skill) : [...current, skill]
      };
    });
  };

  const currentJobMatch = matchData?.matches?.[selectedJobIndex];

  return (
    <div className="space-y-8 pb-16">
      {/* Mode Switcher Tabs */}
      <div className="flex bg-slate-200/80 p-1.5 rounded-2xl max-w-md mx-auto">
        <button
          onClick={() => setMode('existing')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-sm font-semibold transition-all ${
            mode === 'existing'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <UserCheck className="w-4 h-4" />
          Select Existing Profile
        </button>
        <button
          onClick={() => setMode('custom')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-sm font-semibold transition-all ${
            mode === 'custom'
              ? 'bg-white text-blue-700 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Create Custom Profile
        </button>
      </div>

      {/* Mode 1: Existing Profile Selector */}
      {mode === 'existing' && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 text-slate-800 font-bold text-base">
            <Filter className="w-4 h-4 text-blue-600" />
            <span>Select Student Profile & Market Benchmark</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Filter by Career Interest */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                Career Interest Filter
              </label>
              <select
                value={selectedInterest}
                onChange={(e) => setSelectedInterest(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All Interests</option>
                {filters?.career_interests?.map((ci) => (
                  <option key={ci} value={ci}>{ci}</option>
                ))}
              </select>
            </div>

            {/* Select Profile */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                Student Record ({students.length} available)
              </label>
              <select
                value={selectedStudentId}
                onChange={(e) => setSelectedStudentId(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {students.map((st) => (
                  <option key={st.student_id} value={st.student_id}>
                    {st.student_id} — {st.career_interest} ({st.degree}, {st.specialisation})
                  </option>
                ))}
              </select>
            </div>

            {/* Target Job Market */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                Target Market / Country
              </label>
              <select
                value={selectedMarket}
                onChange={(e) => setSelectedMarket(e.target.value)}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All Global Markets</option>
                {filters?.markets?.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Mode 2: Custom Profile Form */}
      {mode === 'custom' && (
        <form onSubmit={handleCustomSubmit} className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                Build Your Custom Student Profile
              </h3>
              <p className="text-xs text-slate-500">Provide your academic status and select your skills for instant AI matching</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-500 mb-1">Full Name</label>
              <input
                type="text"
                value={customForm.name}
                onChange={(e) => setCustomForm({ ...customForm, name: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-500 mb-1">Degree</label>
              <select
                value={customForm.degree}
                onChange={(e) => setCustomForm({ ...customForm, degree: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                {['B.Tech', 'B.Sc', 'BBA', 'B.Des', 'MCA', 'M.Tech', 'MBA'].map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-500 mb-1">Specialisation</label>
              <input
                type="text"
                value={customForm.specialisation}
                onChange={(e) => setCustomForm({ ...customForm, specialisation: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-500 mb-1">
                GPA / Assessment Score: <span className="text-blue-600 font-bold">{customForm.gpa} / 10</span>
              </label>
              <input
                type="range"
                min="5.0"
                max="10.0"
                step="0.1"
                value={customForm.gpa}
                onChange={(e) => setCustomForm({ ...customForm, gpa: parseFloat(e.target.value) })}
                className="w-full accent-blue-600 cursor-pointer"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-500 mb-1">Target Career Role</label>
              <select
                value={customForm.career_interest}
                onChange={(e) => setCustomForm({ ...customForm, career_interest: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                {filters?.career_interests?.map((ci) => (
                  <option key={ci} value={ci}>{ci}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase text-slate-500 mb-1">Job Market</label>
              <select
                value={customForm.market}
                onChange={(e) => setCustomForm({ ...customForm, market: e.target.value })}
                className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="All">All Global Markets</option>
                {filters?.markets?.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Technical Skills Selection */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Select Your Technical Skills
            </label>
            <div className="flex flex-wrap gap-2 max-h-36 overflow-y-auto p-3 rounded-xl bg-slate-50 border border-slate-200">
              {filters?.master_skills?.slice(0, 35).map((sk) => {
                const selected = customForm.technical_skills.includes(sk);
                return (
                  <button
                    type="button"
                    key={sk}
                    onClick={() => toggleSkill('technical_skills', sk)}
                    className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                      selected
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {selected ? '✓ ' : '+ '} {sk}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md transition-all active:scale-95 disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              Generate AI Recommendations
            </button>
          </div>
        </form>
      )}

      {/* Student Profile Overview Card */}
      {studentDetails && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-slate-100 pb-6">
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-bold text-slate-900">{studentDetails.name}</h2>
                <span className="text-xs px-2.5 py-1 rounded-full font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                  {studentDetails.student_id}
                </span>
              </div>
              <p className="text-sm text-slate-500 mt-1">
                {studentDetails.degree} in {studentDetails.specialisation} • {studentDetails.education_level}
              </p>
            </div>
            <div className="flex sm:flex-col items-start sm:items-end gap-3 sm:gap-1">
              <div className="text-2xl font-black text-blue-600 tracking-tight">
                GPA {studentDetails.gpa.toFixed(1)} <span className="text-xs text-slate-400 font-normal">/ 10</span>
              </div>
              <div className="text-xs font-semibold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg">
                Target: {studentDetails.career_interest}
              </div>
            </div>
          </div>

          {/* Persona & Engagement Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 pb-6 border-b border-slate-100">
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                LMS Behavioral Persona (K-Means)
              </div>
              <div className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-500" />
                {studentDetails.cluster_name}
              </div>
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Willingness to Learn Index
                </span>
                <span className="text-xs font-bold text-slate-800">
                  {studentDetails.willingness_to_learn}%
                </span>
              </div>
              <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden mt-2">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${
                    studentDetails.willingness_to_learn >= 70 
                      ? 'bg-emerald-500' 
                      : studentDetails.willingness_to_learn >= 45 
                      ? 'bg-amber-500' 
                      : 'bg-rose-500'
                  }`}
                  style={{ width: `${studentDetails.willingness_to_learn}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Student's Current Skills */}
          <div className="pt-6">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
              Verified Student Skill Proficiencies
            </h4>
            <div className="flex flex-wrap gap-2.5">
              {studentDetails.skills?.map((sk, idx) => (
                <div 
                  key={idx}
                  className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 flex items-center gap-2 shadow-2xs"
                >
                  <span className="text-xs font-semibold text-slate-800">{sk.name}</span>
                  <span className="text-2xs font-bold px-1.5 py-0.5 rounded-md bg-blue-100 text-blue-800">
                    {Math.round(sk.proficiency)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Career Match Recommendations Section */}
      {matchData && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                <Compass className="w-5 h-5 text-blue-600" />
                AI Career Pathway Recommendations
              </h3>
              <p className="text-xs text-slate-500">
                Matched against live job requirements in {selectedMarket} market
              </p>
            </div>
          </div>

          {/* Job Selection Tabs */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {matchData.matches.map((item, index) => {
              const isSelected = selectedJobIndex === index;
              return (
                <button
                  key={item.job.Job_ID}
                  onClick={() => setSelectedJobIndex(index)}
                  className={`text-left p-5 rounded-2xl border transition-all relative ${
                    isSelected
                      ? 'bg-blue-50/70 border-blue-500 shadow-md ring-2 ring-blue-500/20'
                      : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                      Rank #{index + 1}
                    </span>
                    <span className={`text-xs font-extrabold px-2.5 py-1 rounded-full ${
                      item.job.Match_Score >= 75
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.job.Match_Score >= 60
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {item.job.Match_Score}% Match
                    </span>
                  </div>
                  <h4 className="font-bold text-slate-900 text-sm line-clamp-1">{item.job.Job_Title}</h4>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-1">{item.job.Company_Name} • {item.job.Location}</p>
                </button>
              );
            })}
          </div>

          {/* Detailed Job Analysis Panel */}
          {currentJobMatch && (
            <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-8">
              {/* Job Header */}
              <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 border-b border-slate-100 pb-6">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-2xl font-black text-slate-900">{currentJobMatch.job.Job_Title}</h3>
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                      {currentJobMatch.job.Country}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1">
                    {currentJobMatch.job.Company_Name} • {currentJobMatch.job.Industry} • {currentJobMatch.job.Location}
                  </p>
                </div>
                <div className="bg-blue-50 border border-blue-200 rounded-2xl px-5 py-3 text-center sm:text-right">
                  <div className="text-xs font-bold uppercase text-blue-600 tracking-wider">Suitability Score</div>
                  <div className="text-3xl font-extrabold text-blue-700">{currentJobMatch.job.Match_Score}%</div>
                </div>
              </div>

              {/* Skills Radar & Skill Gaps Dual Panel */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
                {/* Radar Chart */}
                <div className="bg-slate-50/80 rounded-2xl p-4 sm:p-6 border border-slate-200/80">
                  <h4 className="text-sm font-bold text-slate-800 mb-1 flex items-center gap-2">
                    <Compass className="w-4 h-4 text-blue-600" />
                    Student Skills vs. Industry Benchmark Radar
                  </h4>
                  <p className="text-xs text-slate-500 mb-4">Direct vector alignment on top relevant skills</p>
                  
                  <div className="w-full flex flex-col items-center justify-center py-2">
                    <RadarChartSvg data={currentJobMatch.radar_skills} width={420} height={280} />
                  </div>
                  <div className="flex justify-center gap-6 text-xs font-semibold pt-2">
                    <div className="flex items-center gap-2 text-blue-600">
                      <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                      Your Skills
                    </div>
                    <div className="flex items-center gap-2 text-rose-600">
                      <span className="w-3 h-3 rounded-full bg-rose-500"></span>
                      Job Requirement Benchmark
                    </div>
                  </div>
                </div>

                {/* Skill Gaps Breakdown */}
                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-bold text-slate-800 mb-1 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-500" />
                      Detected Skill Gaps ({currentJobMatch.skill_gaps.length})
                    </h4>
                    <p className="text-xs text-slate-500 mb-3">
                      Skills explicitly required for this role but absent from your profile
                    </p>
                    
                    {currentJobMatch.skill_gaps.length === 0 ? (
                      <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-sm font-medium flex items-center gap-2">
                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        You fulfill all key prerequisite skills for this role!
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {currentJobMatch.skill_gaps.map((gap, i) => (
                          <span
                            key={i}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 shadow-2xs"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                            {gap}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Required Skills for Role */}
                  <div>
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                      Full Role Requirements
                    </h4>
                    <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-200">
                      {currentJobMatch.job.Skills_Required}
                    </p>
                  </div>
                </div>
              </div>

              {/* Recommended Course Bridges */}
              <div className="space-y-4 pt-4 border-t border-slate-100">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-indigo-600" />
                    Recommended Course Bridges (Greedy Maximum Coverage)
                  </h4>
                  <span className="text-xs font-semibold text-slate-500">
                    Optimized to close skill gaps
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                  {currentJobMatch.recommended_courses.map((course) => {
                    const isSemantic = course.Match_Type?.includes('Semantic');
                    return (
                      <div
                        key={course.Course_ID}
                        className="bg-white rounded-xl border border-slate-200 p-5 hover:border-slate-300 hover:shadow-md transition-all flex flex-col justify-between"
                      >
                        <div>
                          <div className="flex items-center justify-between gap-2 mb-2">
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">
                              {course.Platform} • {course.Duration_Hours}h
                            </span>
                            <span className={`text-2xs font-extrabold px-2 py-0.5 rounded-md ${
                              isSemantic
                                ? 'bg-indigo-50 text-indigo-700 border border-indigo-200'
                                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            }`}>
                              {course.Match_Type}
                            </span>
                          </div>

                          <h5 className="font-bold text-slate-900 text-sm mb-2">{course.Course_Title}</h5>
                          <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                            {course.Description}
                          </p>
                        </div>

                        <div className="pt-3 border-t border-slate-100">
                          <span className="text-2xs font-semibold uppercase text-slate-400 block mb-1">
                            Bridges Missing Skills:
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {course.Skills_Covered_All.split(',').map((s, idx) => (
                              <span
                                key={idx}
                                className="text-2xs font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-100"
                              >
                                {s.trim()}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Explainable AI (XAI) Rationale Box */}
              <div className="bg-gradient-to-r from-blue-50/80 to-indigo-50/80 border border-blue-200/80 rounded-2xl p-6 space-y-3">
                <div className="flex items-center gap-2 text-blue-900 font-bold text-sm">
                  <Sparkles className="w-4 h-4 text-blue-600" />
                  <span>Explainable AI (XAI) Recommendation Rationale</span>
                </div>
                <div className="text-xs sm:text-sm text-slate-700 leading-relaxed font-mono whitespace-pre-line bg-white/70 p-4 rounded-xl border border-blue-100">
                  {currentJobMatch.explanation}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
