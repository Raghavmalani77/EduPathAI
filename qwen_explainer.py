"""
qwen_explainer.py
=================
Qwen-Powered Explainability Engine for EduPath AI.
Replaces static heuristic XAI templates with neural natural-language reasoning
using Qwen 2.5 (7B) via Ollama / OpenAI-compatible endpoint, with seamless
fallback to deterministic glass-box rationale if offline or timeout occurs.
"""

import os
import time
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger("qwen_explainer")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class QwenExplainer:
    def __init__(
        self,
        host: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 60,
    ):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        self.model_name = model_name or os.getenv("QWEN_MODEL", "qwen2.5:7b")
        self.timeout = timeout
        self.cache: Dict[str, Dict[str, Any]] = {}

    def is_available(self) -> bool:
        """Quickly check if Ollama server is reachable and model is available."""
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=1.5)
            if r.status_code == 200:
                data = r.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check if configured model or any qwen variant exists
                return any(
                    self.model_name in m or "qwen" in m.lower() for m in models
                )
            return False
        except Exception:
            return False

    def generate_explanation(
        self,
        student_id: str,
        student_profile: Dict[str, Any],
        job_profile: Dict[str, Any],
        overlapping_skills: List[str],
        skill_gaps: List[str],
        recommended_courses: List[Dict[str, Any]],
        use_qwen: bool = True,
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate transparent explainability narrative.
        Returns a dictionary with explanation text, model provider, and metadata.
        """
        job_id = str(job_profile.get("Job_ID", ""))
        cache_key = f"{student_id}_{job_id}"

        if not force_regenerate and cache_key in self.cache:
            cached = dict(self.cache[cache_key])
            cached["cached"] = True
            return cached

        # If Qwen is disabled or unavailable, use deterministic fallback
        if not use_qwen:
            baseline = self._generate_baseline_explanation(
                student_profile,
                job_profile,
                overlapping_skills,
                skill_gaps,
                recommended_courses,
            )
            return {
                "explanation": baseline,
                "provider": "baseline",
                "is_qwen": False,
                "model": "rule-based-v2",
                "cached": False,
            }

        # Attempt neural generation via Qwen
        try:
            prompt = self._build_prompt(
                student_profile,
                job_profile,
                overlapping_skills,
                skill_gaps,
                recommended_courses,
            )

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 180,
                },
            }

            t0 = time.time()
            resp = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout,
            )

            if resp.status_code == 200:
                raw_text = resp.json().get("response", "").strip()
                if raw_text:
                    result = {
                        "explanation": raw_text,
                        "provider": self.model_name,
                        "is_qwen": True,
                        "model": self.model_name,
                        "generation_time_s": round(time.time() - t0, 2),
                        "cached": False,
                    }
                    self.cache[cache_key] = result
                    return result

            logger.warning(
                f"Qwen HTTP {resp.status_code}: falling back to baseline rationale"
            )
        except Exception as e:
            logger.warning(f"Qwen generation error ({e}); using baseline rationale")

        # Fallback to baseline glass-box explanation
        baseline = self._generate_baseline_explanation(
            student_profile,
            job_profile,
            overlapping_skills,
            skill_gaps,
            recommended_courses,
        )
        return {
            "explanation": baseline,
            "provider": "baseline_fallback",
            "is_qwen": False,
            "model": "rule-based-v2",
            "cached": False,
        }

    def _build_prompt(
        self,
        student: Dict[str, Any],
        job: Dict[str, Any],
        overlapping: List[str],
        gaps: List[str],
        courses: List[Dict[str, Any]],
    ) -> str:
        student_name = student.get("Name", student.get("Student_ID", "Student"))
        degree = student.get("Degree", "Undergraduate")
        spec = student.get("Specialisation", "General")
        job_title = job.get("Job_Title", "Target Role")
        company = job.get("Company_Name", "Global Enterprise")
        location = job.get("Location", "Global")
        match_score = job.get("Match_Score", 80.0)

        course_lines = []
        for c in courses[:3]:
            title = c.get("Course_Title", "Course")
            platform = c.get("Platform", "Online")
            cov = c.get("Skills_Covered_All", c.get("Skills_Covered", "Key skills"))
            course_lines.append(f"- '{title}' ({platform}) -> bridges: {cov}")

        prompt = f"""You are EduPath AI's Explainability Engine (powered by Qwen 2.5).
Generate a concise, transparent, and encouraging career recommendation explanation for:
- Student: {student_name} ({degree} in {spec})
- Target Role: {job_title} at {company} ({location})
- Match Score: {match_score}%
- Existing Strong Skills: {', '.join(overlapping) if overlapping else 'Foundational curriculum'}
- Detected Skill Gaps: {', '.join(gaps) if gaps else 'None (Fully qualified)'}
- Curated Upskilling Pathway:
{chr(10).join(course_lines) if course_lines else '- No courses needed; fully qualified'}

Instructions:
1. Briefly state why the student's existing skills align with the {job_title} role.
2. Clearly explain how the recommended courses target their specific skill gaps to make them job-ready.
Format with clean bullet points. Keep total length under 140 words. Be objective and direct."""
        return prompt

    def _generate_baseline_explanation(
        self,
        student: Dict[str, Any],
        job: Dict[str, Any],
        overlapping: List[str],
        gaps: List[str],
        courses: List[Dict[str, Any]],
    ) -> str:
        job_title = job.get("Job_Title", "Target Role")
        company = job.get("Company_Name", "Global Enterprise")
        location = job.get("Location", "Global")
        
        lines = []
        lines.append(
            f"- **Role Alignment & Baseline Strengths:** The profile exhibits strong qualification for **'{job_title}'** at **{company}** ({location}). "
            f"Current verified competencies include: {', '.join(overlapping) if overlapping else 'Foundational academic qualifications'}."
        )

        if gaps:
            lines.append(
                f"- **Identified Competency Gaps:** To achieve full readiness, development is required in: {', '.join(gaps)}."
            )

        if courses:
            lines.append("- **Curated Remediation Pathway:**")
            for c in courses[:3]:
                title = c.get("Course_Title", "")
                platform = c.get("Platform", "")
                cov = c.get("Skills_Covered_All", c.get("Skills_Covered", ""))
                lines.append(f"  * **{title}** ({platform}): Bridges `{cov}` to meet role prerequisites.")
        else:
            lines.append("- **Skill Coverage:** All required skills are already met by current competencies.")

        return "\n".join(lines)
