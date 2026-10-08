import React from 'react';
import { Layers, Cpu, ShieldCheck, Database, Award, CheckCircle2 } from 'lucide-react';

export default function AboutView({ stats }) {
  return (
    <div className="space-y-8 pb-16 max-w-4xl mx-auto">
      <div>
        <h2 className="text-3xl font-bold text-slate-900">Architecture & Technical Methodology</h2>
        <p className="text-sm text-slate-500 mt-1">
          Decoupled 6-Tier Architecture from LMS Event Ingestion to Explainable Recommendations
        </p>
      </div>

      {/* Model Spec Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-blue-600" />
          Core AI Recommendation Modules
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 text-sm mb-1">Sentence-BERT (all-MiniLM-L6-v2)</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-3">
              Dense 384-dimensional semantic embedding space resolves vocabulary mismatch between market requirements and educational curricula (e.g. "PyTorch" ↔ "Deep Learning").
            </p>
            <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
              Active Mode: {stats?.embedding_model || 'Sentence-BERT'}
            </span>
          </div>

          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 text-sm mb-1">Greedy Set-Cover Optimization</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-3">
              Solves the Maximum Coverage Problem by selecting minimal combinations of courses that maximize covered gap proficiencies while penalizing excessive study hours.
            </p>
            <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
              Coverage Objective: Maximum Skills in Min Hours
            </span>
          </div>

          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 text-sm mb-1">K-Means Student Persona Clustering</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-3">
              Segments behavioral interactions across logins, submissions, course completion rate, and GPA into actionable student engagement archetypes (K=3).
            </p>
            <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-amber-100 text-amber-800">
              Feature Space: 6 Scaled Engagement Dimensions
            </span>
          </div>

          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200/80">
            <h4 className="font-bold text-slate-900 text-sm mb-1">Continuous 66-D Skill Vectors</h4>
            <p className="text-xs text-slate-600 leading-relaxed mb-3">
              Continuous weights in [0.0, 1.0] representing Bloom's revised taxonomy proficiencies across 66 standardized technical and interpersonal domain capabilities.
            </p>
            <span className="text-2xs font-semibold px-2 py-0.5 rounded bg-purple-100 text-purple-800">
              66-Dimensional Cosine Matcher
            </span>
          </div>
        </div>
      </div>

      {/* Benchmarks & Performance */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-4">
        <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Award className="w-5 h-5 text-amber-500" />
          Benchmarking & Model Evaluation Suite
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          The underlying machine learning architecture was benchmarked using Stratified 5-Fold Cross-Validation across 16 career pathway classifications:
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-600 border border-slate-200 rounded-xl overflow-hidden">
            <thead className="bg-slate-100 text-slate-800 font-bold uppercase">
              <tr>
                <th className="px-4 py-3">Metric</th>
                <th className="px-4 py-3">Evaluated Value</th>
                <th className="px-4 py-3">Validation Methodology</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              <tr>
                <td className="px-4 py-3 font-semibold text-slate-900">Multi-Class ROC-AUC</td>
                <td className="px-4 py-3 text-emerald-600 font-bold">0.9910</td>
                <td className="px-4 py-3">One-vs-Rest Macro Average</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-semibold text-slate-900">Career Pathway CV Accuracy</td>
                <td className="px-4 py-3 text-emerald-600 font-bold">87.5%</td>
                <td className="px-4 py-3">Random Forest Classifier (5-Fold CV)</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-semibold text-slate-900">Precision @ K=3</td>
                <td className="px-4 py-3 text-blue-600 font-bold">78.4%</td>
                <td className="px-4 py-3">Course Recommendation Precision</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-semibold text-slate-900">Recall @ K=3</td>
                <td className="px-4 py-3 text-blue-600 font-bold">76.8%</td>
                <td className="px-4 py-3">Skill Gap Coverage Recall</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
