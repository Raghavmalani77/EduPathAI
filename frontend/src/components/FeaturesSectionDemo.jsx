"use client";
import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { motion } from "motion/react";
import {
  IconCheck,
  IconClock,
  IconArrowRight,
  IconSparkles,
  IconSchool,
  IconBriefcase,
  IconChartBar,
  IconMapPin,
  IconBuildingSkyscraper,
  IconCurrencyEuro,
  IconBrain,
} from "@tabler/icons-react";

/**
 * Aceternity UI — Features Section (EduPath Student Career Recommender)
 * Featuring interactive student pathway milestone steps and global country placements (Germany, France, etc.).
 */
export default function FeaturesSectionDemo() {
  const features = [
    {
      title: "Interactive Student Career Pathway",
      description:
        "Live student pathway demonstration: maps profile GPA, technical competencies, and bridges exact skill deficits to land the target role.",
      skeleton: <SkeletonOnePathwayExample />,
      className:
        "col-span-1 lg:col-span-4 border-b lg:border-r border-neutral-200 dark:border-neutral-800",
    },
    {
      title: "Personalized Course Bridges",
      description:
        "Greedy Set-Cover optimization calculates the minimum-duration course pathways to close identified technical deficits.",
      skeleton: <SkeletonTwo />,
      className: "border-b col-span-1 lg:col-span-2 border-neutral-200 dark:border-neutral-800",
    },
    {
      title: "Explainable Skill Gap Analytics",
      description:
        "Feature importance and S-BERT cosine similarity clearly explain which skills bridge the gap to top-tier placements.",
      skeleton: <SkeletonThree />,
      className:
        "col-span-1 lg:col-span-3 lg:border-r border-neutral-200 dark:border-neutral-800",
    },
    {
      title: "Global Tech Placements & Opportunities",
      description:
        "Real-time opportunities with student placements across key tech economies including Germany, France, India, UK, and USA.",
      skeleton: <SkeletonFourGlobalCountries />,
      className: "col-span-1 lg:col-span-3 border-b lg:border-none border-neutral-200 dark:border-neutral-800",
    },
  ];

  return (
    <div className="relative z-20 mx-auto max-w-7xl py-10 lg:py-16">
      <div className="px-6 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50/80 px-4 py-1 text-xs font-semibold uppercase tracking-wider text-blue-700 shadow-sm dark:border-blue-900 dark:bg-blue-950/50 dark:text-blue-300">
          <IconSparkles className="h-3.5 w-3.5" />
          <span>AI Student Career & Employability System</span>
        </div>

        <h2 className="mx-auto mt-4 max-w-5xl text-center text-3xl font-extrabold tracking-tight text-neutral-900 lg:text-5xl lg:leading-tight dark:text-white">
          Intelligent Student Pathway Recommender
        </h2>

        <p className="mx-auto my-4 max-w-2xl text-center text-sm font-normal text-neutral-600 lg:text-base dark:text-neutral-400">
          Empowering engineering and science students to bridge academic skill gaps, explore country hiring markets, and follow step-by-step career pathways.
        </p>
      </div>

      <div className="relative mt-8">
        <div className="grid grid-cols-1 rounded-3xl border border-neutral-200 bg-white shadow-xl shadow-neutral-200/50 lg:grid-cols-6 dark:border-neutral-800 dark:bg-neutral-900 dark:shadow-none overflow-hidden">
          {features.map((feature) => (
            <FeatureCard key={feature.title} className={feature.className}>
              <FeatureTitle>{feature.title}</FeatureTitle>
              <FeatureDescription>{feature.description}</FeatureDescription>
              <div className="h-full w-full">{feature.skeleton}</div>
            </FeatureCard>
          ))}
        </div>
      </div>
    </div>
  );
}

const FeatureCard = ({ children, className }) => {
  return (
    <div className={cn("relative overflow-hidden p-6 sm:p-8 flex flex-col justify-between bg-white dark:bg-neutral-900", className)}>
      {children}
    </div>
  );
};

const FeatureTitle = ({ children }) => {
  return (
    <p className="max-w-5xl text-left text-xl font-bold tracking-tight text-neutral-900 md:text-2xl md:leading-snug dark:text-white">
      {children}
    </p>
  );
};

const FeatureDescription = ({ children }) => {
  return (
    <p
      className={cn(
        "max-w-md text-left text-sm font-normal text-neutral-500 dark:text-neutral-400",
        "mx-0 my-2 text-left"
      )}
    >
      {children}
    </p>
  );
};

/**
 * Card 1: Interactive Real Student Career Pathway Example
 */
export const SkeletonOnePathwayExample = () => {
  const [selectedStep, setSelectedStep] = useState(2);

  const steps = [
    {
      id: 1,
      phase: "Phase 1: Academic Base",
      status: "Completed",
      badgeColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
      skills: ["GPA: 8.4/10", "Python Core", "Linear Algebra", "Data Structures"],
      desc: "Core academic record verified from transcript records.",
    },
    {
      id: 2,
      phase: "Phase 2: Machine Learning",
      status: "In Progress",
      badgeColor: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      skills: ["Scikit-Learn", "S-BERT Embeddings", "Pandas", "K-Means"],
      desc: "Skill gap analysis completed. Cosine similarity: 0.88.",
    },
    {
      id: 3,
      phase: "Phase 3: MLOps Bridge",
      status: "Prescribed Courses",
      badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
      skills: ["Docker & Kubernetes", "FastAPI Serving", "MLflow CI/CD"],
      desc: "Greedy Set-Cover: 2 Curated Courses (44 Hours total).",
    },
    {
      id: 4,
      phase: "Phase 4: Target Placement",
      status: "Ready for Matching",
      badgeColor: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      skills: ["AI Engineer (€75k DE)", "ML Specialist (₹18L IN)", "Remote Global"],
      desc: "Predicted interview readiness score: 94.2%.",
    },
  ];

  return (
    <div className="relative flex h-full min-h-[340px] flex-col justify-between gap-4 py-3">
      {/* Student Profile Header Bar */}
      <div className="rounded-2xl bg-neutral-950 p-4 border border-neutral-800 text-white shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 pb-3">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center font-bold text-white shadow-md">
              AS
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-neutral-100">Aarav Sharma</span>
                <span className="text-[10px] rounded-full bg-blue-500/20 text-blue-300 font-mono px-2 py-0.5 border border-blue-500/30">
                  B.Tech CSE · Sem 7
                </span>
              </div>
              <p className="text-xs text-neutral-400">Target Role: <strong className="text-cyan-300 font-semibold">AI / Machine Learning Engineer</strong></p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="text-right">
              <div className="text-[10px] text-neutral-400 font-mono uppercase">Target Fit Match</div>
              <div className="text-base font-extrabold text-emerald-400 font-mono">91.8%</div>
            </div>
            <div className="h-9 w-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <IconSparkles className="h-5 w-5" />
            </div>
          </div>
        </div>

        {/* Pathway Stepper Roadmap */}
        <div className="pt-4">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-2">
            {steps.map((s, idx) => {
              const isSelected = selectedStep === s.id;
              return (
                <div
                  key={s.id}
                  onClick={() => setSelectedStep(s.id)}
                  className={cn(
                    "cursor-pointer rounded-xl p-3 border transition-all text-left relative",
                    isSelected
                      ? "bg-neutral-900 border-blue-500 ring-1 ring-blue-500/50 shadow-md shadow-blue-500/10"
                      : "bg-neutral-900/60 border-neutral-800/80 hover:border-neutral-700"
                  )}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-mono text-neutral-400">0{s.id}</span>
                    <span className={cn("text-[9px] font-mono px-1.5 py-0.5 rounded border", s.badgeColor)}>
                      {s.status}
                    </span>
                  </div>
                  <h4 className="text-xs font-bold text-neutral-200 mb-1">{s.phase}</h4>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {s.skills.slice(0, 2).map((sk, i) => (
                      <span key={i} className="text-[9px] bg-neutral-800 text-neutral-300 px-1.5 py-0.5 rounded">
                        {sk}
                      </span>
                    ))}
                    {s.skills.length > 2 && (
                      <span className="text-[9px] text-neutral-500">+{s.skills.length - 2}</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Milestone Detail Banner */}
        <div className="mt-3 rounded-xl bg-neutral-900 p-3 border border-neutral-800/90 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="font-semibold text-neutral-200">{steps[selectedStep - 1].phase}:</span>
            <span className="text-neutral-400">{steps[selectedStep - 1].desc}</span>
          </div>
          <div className="flex items-center gap-1.5 self-end sm:self-auto font-mono text-[11px] text-cyan-300">
            <span>Course Bridges Active</span>
            <IconArrowRight className="h-3.5 w-3.5" />
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Card 2: Student Learning Cohorts & Certified Courses
 */
export const SkeletonTwo = () => {
  const studentImages = [
    {
      url: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600&auto=format&fit=crop",
      tag: "Peer Learning Cohorts",
    },
    {
      url: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=600&auto=format&fit=crop",
      tag: "Coding & AI Labs",
    },
    {
      url: "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=600&auto=format&fit=crop",
      tag: "Faculty Mentorship",
    },
    {
      url: "/student-cohort-4.jpg",
      tag: "Career Placement",
    },
  ];

  const imageVariants = {
    whileHover: {
      scale: 1.1,
      rotate: 0,
      zIndex: 100,
    },
    whileTap: {
      scale: 1.05,
      rotate: 0,
      zIndex: 100,
    },
  };

  return (
    <div className="relative flex h-full flex-col items-start gap-4 overflow-hidden py-4">
      <div className="-ml-10 flex flex-row">
        {studentImages.map((item, idx) => (
          <motion.div
            variants={imageVariants}
            key={"student-img-1" + idx}
            style={{
              rotate: (idx % 2 === 0 ? 1 : -1) * (idx * 3 + 2),
            }}
            whileHover="whileHover"
            whileTap="whileTap"
            className="mt-2 -mr-3 shrink-0 overflow-hidden rounded-xl border border-neutral-200 bg-white p-1.5 shadow-md dark:border-neutral-700 dark:bg-neutral-800"
          >
            <img
              src={item.url}
              alt={item.tag}
              loading="lazy"
              className="h-24 w-28 shrink-0 rounded-lg object-cover sm:h-28 sm:w-32"
            />
            <div className="text-[10px] font-semibold text-neutral-600 dark:text-neutral-300 mt-1 text-center truncate max-w-[110px]">
              {item.tag}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="flex flex-row pl-2">
        {studentImages.slice().reverse().map((item, idx) => (
          <motion.div
            key={"student-img-2" + idx}
            style={{
              rotate: (idx % 2 === 0 ? -1 : 1) * (idx * 2 + 1),
            }}
            variants={imageVariants}
            whileHover="whileHover"
            whileTap="whileTap"
            className="mt-1 -mr-3 shrink-0 overflow-hidden rounded-xl border border-neutral-200 bg-white p-1.5 shadow-md dark:border-neutral-700 dark:bg-neutral-800"
          >
            <img
              src={item.url}
              alt={item.tag}
              loading="lazy"
              className="h-24 w-28 shrink-0 rounded-lg object-cover sm:h-28 sm:w-32"
            />
            <div className="text-[10px] font-semibold text-neutral-600 dark:text-neutral-300 mt-1 text-center truncate max-w-[110px]">
              {item.tag}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="pointer-events-none absolute inset-y-0 left-0 z-40 h-full w-12 bg-gradient-to-r from-white to-transparent dark:from-neutral-900" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-40 h-full w-12 bg-gradient-to-l from-white to-transparent dark:from-neutral-900" />
    </div>
  );
};

/**
 * Card 3: Real Cumulative Feature Importance & Skill Gap Chart
 */
export const SkeletonThree = () => {
  return (
    <div className="group/chart relative flex h-full min-h-[260px] flex-col justify-between overflow-hidden rounded-2xl bg-neutral-950 p-4 border border-neutral-800 text-white shadow-xl">
      <div className="flex items-center justify-between border-b border-neutral-800 pb-2">
        <div className="flex items-center gap-2 text-xs font-mono text-neutral-300">
          <IconChartBar className="h-4 w-4 text-cyan-400" />
          <span>Top Career Predictive Skills</span>
        </div>
        <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/30 font-mono">
          Random Forest + SHAP
        </span>
      </div>

      <div className="relative my-2 overflow-hidden rounded-xl bg-neutral-900/90 border border-neutral-800 p-2 flex items-center justify-center">
        <img
          src="/skill-importance.png"
          alt="Student Skill Feature Importance"
          className="w-full max-h-48 object-contain rounded-lg filter contrast-105 group-hover/chart:scale-[1.02] transition-transform duration-300"
        />
      </div>

      <div className="flex items-center justify-between text-[11px] text-neutral-400 font-mono pt-1">
        <span>Highest Impact: Python, SQL, Cloud, Statistics</span>
        <span className="text-emerald-400 font-semibold">AUC-ROC: 0.94</span>
      </div>
    </div>
  );
};

/**
 * Card 4: Global Tech Placements with Country Images (Germany, France, India, UK, USA)
 */
export const SkeletonFourGlobalCountries = () => {
  const [activeCountry, setActiveCountry] = useState("germany");

  const countries = [
    {
      id: "germany",
      name: "Germany",
      flag: "🇩🇪",
      city: "Munich & Berlin",
      jobs: "65+ Positions",
      pkg: "€68,000 – €85,000",
      image: "/countries/germany.jpg",
      topSkills: "AI, Automotive ML, Cloud",
    },
    {
      id: "france",
      name: "France",
      flag: "🇫🇷",
      city: "Paris Station F",
      jobs: "38+ Positions",
      pkg: "€62,000 – €78,000",
      image: "/countries/france.jpg",
      topSkills: "Computer Vision, LLMs",
    },
    {
      id: "india",
      name: "India",
      flag: "🇮🇳",
      city: "Bangalore & Pune",
      jobs: "110+ Positions",
      pkg: "₹14 LPA – ₹26 LPA",
      image: "/countries/india.jpg",
      topSkills: "Python, Microservices, MLOps",
    },
    {
      id: "uk",
      name: "United Kingdom",
      flag: "🇬🇧",
      city: "London Tech City",
      jobs: "45+ Positions",
      pkg: "£65,000 – £82,000",
      image: "/countries/uk.jpg",
      topSkills: "FinTech AI, Data Science",
    },
    {
      id: "usa",
      name: "United States",
      flag: "🇺🇸",
      city: "Silicon Valley",
      jobs: "75+ Positions",
      pkg: "$110,000 – $145,000",
      image: "/countries/usa.jpg",
      topSkills: "Deep Learning, PyTorch",
    },
  ];

  return (
    <div className="relative flex h-full min-h-[300px] flex-col justify-between gap-3 py-2">
      {/* Country Tabs Header */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {countries.map((c) => {
          const isActive = activeCountry === c.id;
          return (
            <button
              key={c.id}
              onClick={() => setActiveCountry(c.id)}
              className={cn(
                "flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold whitespace-nowrap transition-all border",
                isActive
                  ? "bg-blue-600 text-white border-blue-500 shadow-sm"
                  : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200 border-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:border-neutral-700"
              )}
            >
              <span>{c.flag}</span>
              <span>{c.name}</span>
            </button>
          );
        })}
      </div>

      {/* Featured Country Showcase Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
        {countries.slice(0, 3).map((c) => {
          const isSelected = activeCountry === c.id;
          return (
            <div
              key={c.id}
              onClick={() => setActiveCountry(c.id)}
              className={cn(
                "group/cnt relative h-36 rounded-2xl overflow-hidden cursor-pointer border transition-all duration-300",
                isSelected
                  ? "ring-2 ring-blue-500 border-transparent shadow-lg scale-[1.02]"
                  : "border-neutral-200 dark:border-neutral-800 hover:border-blue-400"
              )}
            >
              {/* Background Country Photo */}
              <img
                src={c.image}
                alt={c.name}
                className="absolute inset-0 h-full w-full object-cover group-hover/cnt:scale-110 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-neutral-950/60 to-neutral-950/20" />

              {/* Card Overlay Text */}
              <div className="absolute inset-0 p-3 flex flex-col justify-between text-white">
                <div className="flex items-center justify-between">
                  <span className="text-lg">{c.flag}</span>
                  <span className="text-[10px] rounded-full bg-black/60 backdrop-blur-md px-2 py-0.5 border border-white/20 font-mono text-cyan-300">
                    {c.jobs}
                  </span>
                </div>

                <div>
                  <div className="font-bold text-xs text-white leading-tight">{c.name}</div>
                  <div className="text-[10px] text-neutral-300 flex items-center gap-1 mt-0.5">
                    <IconMapPin className="h-3 w-3 text-cyan-400" />
                    <span className="truncate">{c.city}</span>
                  </div>
                  <div className="text-[10px] font-mono text-emerald-400 font-semibold mt-1">
                    {c.pkg}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Country Detail Highlight */}
      {(() => {
        const curr = countries.find((c) => c.id === activeCountry) || countries[0];
        return (
          <div className="rounded-xl bg-neutral-950 p-3 border border-neutral-800 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-base">{curr.flag}</span>
              <div>
                <span className="font-bold text-neutral-100">{curr.name} Placement Hub ({curr.city}):</span>{" "}
                <span className="text-neutral-400">Demand in {curr.topSkills}</span>
              </div>
            </div>
            <div className="font-mono text-emerald-400 text-[11px] font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              Avg: {curr.pkg}
            </div>
          </div>
        );
      })()}
    </div>
  );
};
