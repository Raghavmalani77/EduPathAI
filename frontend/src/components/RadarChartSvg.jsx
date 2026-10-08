import React, { useState } from 'react';

export default function RadarChartSvg({ data, width = 450, height = 320 }) {
  const [hoveredSkill, setHoveredSkill] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-400">
        No skill dimensions available
      </div>
    );
  }

  const cx = width / 2;
  const cy = height / 2;
  const radius = Math.min(cx, cy) - 50;
  const total = data.length;

  const getCoordinates = (value, index, max = 100) => {
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    const r = (value / max) * radius;
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle)
    };
  };

  // Concentric polygon grid levels: 25%, 50%, 75%, 100%
  const levels = [0.25, 0.5, 0.75, 1.0];

  const gridPolygons = levels.map((lvl) => {
    const points = data.map((_, i) => {
      const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
      const r = lvl * radius;
      return `${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`;
    }).join(' ');
    return points;
  });

  // Calculate polygon points
  const studentPoints = data.map((d, i) => {
    const pt = getCoordinates(d.student_score, i);
    return `${pt.x},${pt.y}`;
  }).join(' ');

  const jobPoints = data.map((d, i) => {
    const pt = getCoordinates(d.job_score, i);
    return `${pt.x},${pt.y}`;
  }).join(' ');

  return (
    <div className="relative flex flex-col items-center">
      <svg width={width} height={height} className="overflow-visible select-none">
        {/* Background Grids */}
        {gridPolygons.map((pts, idx) => (
          <polygon
            key={idx}
            points={pts}
            fill={idx % 2 === 0 ? 'rgba(241, 245, 249, 0.5)' : 'rgba(255, 255, 255, 0.7)'}
            stroke="#e2e8f0"
            strokeWidth="1"
          />
        ))}

        {/* Axes lines */}
        {data.map((_, i) => {
          const pt = getCoordinates(100, i);
          return (
            <line
              key={i}
              x1={cx}
              y1={cy}
              x2={pt.x}
              y2={pt.y}
              stroke="#e2e8f0"
              strokeWidth="1"
            />
          );
        })}

        {/* Job Requirement Area (Rose / Red) */}
        <polygon
          points={jobPoints}
          fill="rgba(239, 68, 68, 0.18)"
          stroke="#ef4444"
          strokeWidth="2"
          strokeLinejoin="round"
        />

        {/* Student Skills Area (Blue) */}
        <polygon
          points={studentPoints}
          fill="rgba(37, 99, 235, 0.28)"
          stroke="#2563eb"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* Data points & hover triggers */}
        {data.map((d, i) => {
          const sPt = getCoordinates(d.student_score, i);
          const jPt = getCoordinates(d.job_score, i);
          const labelAngle = (Math.PI * 2 / total) * i - Math.PI / 2;
          const labelR = radius + 24;
          const labelX = cx + labelR * Math.cos(labelAngle);
          const labelY = cy + labelR * Math.sin(labelAngle);

          return (
            <g key={i} onMouseEnter={() => setHoveredSkill(d)} onMouseLeave={() => setHoveredSkill(null)}>
              {/* Job point */}
              <circle cx={jPt.x} cy={jPt.y} r="3.5" fill="#ef4444" stroke="#ffffff" strokeWidth="1.5" />
              {/* Student point */}
              <circle cx={sPt.x} cy={sPt.y} r="4.5" fill="#2563eb" stroke="#ffffff" strokeWidth="2" />
              {/* Label */}
              <text
                x={labelX}
                y={labelY}
                textAnchor="middle"
                dominantBaseline="central"
                className="text-[11px] font-semibold fill-slate-700 cursor-pointer"
              >
                {d.skill}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Dynamic Skill Hover Tooltip */}
      {hoveredSkill && (
        <div className="absolute bottom-2 bg-slate-900/95 text-white px-3 py-1.5 rounded-lg text-xs shadow-lg flex items-center gap-3">
          <span className="font-bold text-blue-300">{hoveredSkill.skill}:</span>
          <span className="text-blue-400">Your: {hoveredSkill.student_score}%</span>
          <span className="text-slate-400">•</span>
          <span className="text-rose-400">Target: {hoveredSkill.job_score}%</span>
        </div>
      )}
    </div>
  );
}
