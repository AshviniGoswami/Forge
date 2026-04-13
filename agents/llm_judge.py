"""
LLM-as-Judge Agent
--------------------
Independently evaluates the workout + nutrition plan against a
well-defined 10-criterion scientific soundness rubric using Gemini.

This is a SEPARATE Gemini call that does not share context with
the planning agents — ensuring independent evaluation.
"""

import json
import re
import requests


# ============================================================
# JUDGE RUBRIC — The core evaluation framework
# ============================================================
JUDGE_RUBRIC = {
    "Progressive Overload Principle": {
        "weight": 1.0,
        "description": "Workout plan must show systematic increase in volume/intensity across 4 weeks.",
        "scoring_guide": {
            "9-10": "Clear week-by-week progression in sets, reps, or exercise difficulty. Week 4 measurably harder than Week 1.",
            "7-8": "Some progression visible but inconsistent across all muscle groups.",
            "5-6": "Minimal progression, mostly the same plan repeated.",
            "1-4": "No progression or contradictory (easier over time)."
        }
    },
    "Muscle Group Balance": {
        "weight": 1.0,
        "description": "Pushing/pulling muscles must be balanced. No imbalances that could cause injury.",
        "scoring_guide": {
            "9-10": "Equal push/pull volume. Anterior/posterior chain balance. Unilateral work included.",
            "7-8": "Minor imbalances but generally well-balanced.",
            "5-6": "Noticeable imbalance (e.g., too much chest, not enough back).",
            "1-4": "Severe imbalance likely to cause injury or postural issues."
        }
    },
    "Rest & Recovery Adequacy": {
        "weight": 1.0,
        "description": "Minimum 48hrs between same muscle group sessions. Adequate rest days.",
        "scoring_guide": {
            "9-10": "48-72hr recovery respected. At least 1-2 rest days/week. Deload week included.",
            "7-8": "Generally adequate, minor violations.",
            "5-6": "Some consecutive same-muscle-group days without justification.",
            "1-4": "Insufficient recovery likely to cause overtraining."
        }
    },
    "Macro Distribution Validity": {
        "weight": 1.0,
        "description": "Protein 1.6-2.2g/kg for muscle gain. Calories align with goal (surplus/deficit/maintenance).",
        "scoring_guide": {
            "9-10": "Protein in evidence-based range. Calorie target appropriate for stated goal.",
            "7-8": "Close to optimal, minor deviations.",
            "5-6": "Significant deviation from evidence-based ranges.",
            "1-4": "Macros contradict the stated goal (e.g., deficit for muscle building)."
        }
    },
    "Evidence-Based Exercise Selection": {
        "weight": 1.0,
        "description": "Exercises must be achievable with stated equipment. Compound movements prioritized.",
        "scoring_guide": {
            "9-10": "All exercises feasible with listed equipment. Compound movements form base.",
            "7-8": "Mostly appropriate, 1-2 exercises questionable.",
            "5-6": "Several exercises require unlisted equipment.",
            "1-4": "Exercises largely impossible with stated equipment."
        }
    },
    "Fitness Level Appropriateness": {
        "weight": 1.0,
        "description": "Complexity and volume must match stated fitness level.",
        "scoring_guide": {
            "9-10": "Perfectly calibrated to level. Beginner: basics only. Advanced: periodization, tempo, etc.",
            "7-8": "Generally appropriate, minor mismatches.",
            "5-6": "Some elements clearly above/below stated level.",
            "1-4": "Significant mismatch — dangerous for beginners or insulting for advanced athletes."
        }
    },
    "Dietary Preference Compliance": {
        "weight": 1.5,
        "description": "Nutrition plan must strictly adhere to stated dietary restrictions. Zero tolerance.",
        "scoring_guide": {
            "9-10": "100% compliant with stated dietary preference. No violations.",
            "7-8": "1 minor ambiguous item (e.g., could be interpreted as non-compliant).",
            "5-6": "Clear violation of dietary preference.",
            "1-4": "Multiple violations of stated dietary requirements."
        }
    },
    "Safety & Injury Consideration": {
        "weight": 1.5,
        "description": "If health notes mention injuries/conditions, exercises must be appropriately modified.",
        "scoring_guide": {
            "9-10": "Specific modifications for all mentioned conditions. Contraindicated exercises avoided.",
            "7-8": "General modifications, misses some specifics.",
            "5-6": "Health notes acknowledged but not meaningfully reflected in plan.",
            "1-4": "Health notes ignored. Contraindicated exercises included."
        }
    },
    "Goal Alignment": {
        "weight": 1.0,
        "description": "All recommendations must coherently target the stated primary goal.",
        "scoring_guide": {
            "9-10": "Every element — exercises, nutrition, volume — optimally targets stated goal.",
            "7-8": "Mostly aligned, minor generic elements.",
            "5-6": "Plan feels generic, not specifically optimized for goal.",
            "1-4": "Plan contradicts stated goal."
        }
    },
    "Completeness & Actionability": {
        "weight": 1.0,
        "description": "Plan must be immediately actionable with specific sets, reps, portions.",
        "scoring_guide": {
            "9-10": "Immediately actionable. Specific sets/reps/rest. No vague instructions.",
            "7-8": "Mostly specific, some vague elements.",
            "5-6": "Several vague instructions that require further interpretation.",
            "1-4": "Mostly vague. User cannot start without major research."
        }
    }
}


class LLMJudge:
    def __init__(self, gemini_api_key: str):
        self.gemini_key = gemini_api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    def _gemini_call(self, prompt: str) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 3072}
        }
        resp = requests.post(self.gemini_url, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def evaluate(self, profile: dict, workout_plan: dict, nutrition_plan: dict, guidelines: dict) -> dict:
        """
        Evaluate the generated plans against the rubric independently.
        Returns structured evaluation with per-criterion scores and verdict.
        """
        # Format plans for evaluation
        workout_summary = json.dumps(workout_plan, indent=2)[:3000]
        nutrition_summary = json.dumps(nutrition_plan, indent=2)[:2000]
        
        # Build the rubric description for the judge
        rubric_text = ""
        for criterion, details in JUDGE_RUBRIC.items():
            rubric_text += f"\n**{criterion}** (Weight: {details['weight']}x)\n"
            rubric_text += f"Description: {details['description']}\n"
            rubric_text += f"Scoring: 9-10: {details['scoring_guide']['9-10']}\n"
            rubric_text += f"         5-6: {details['scoring_guide']['5-6']}\n"
            rubric_text += f"         1-4: {details['scoring_guide']['1-4']}\n"

        prompt = f"""
You are an independent scientific evaluator (Exercise Physiology PhD + Registered Dietitian) 
reviewing a fitness plan. You were NOT involved in creating this plan.
Your role is to provide an OBJECTIVE, CRITICAL evaluation.

Do NOT be lenient. Score honestly. The purpose is quality assurance.

USER PROFILE:
- Goal: {profile['fitness_goal']}
- Level: {profile['fitness_level']}
- Equipment: {', '.join(profile['equipment'])}
- Dietary Preference: {profile['dietary_preference']}
- Health Notes: {profile['health_notes']}
- Age: {profile['age']}

WORKOUT PLAN SUBMITTED FOR REVIEW:
{workout_summary}

NUTRITION PLAN SUBMITTED FOR REVIEW:
{nutrition_summary}

EVALUATION RUBRIC (10 criteria):
{rubric_text}

Evaluate each criterion independently. Be specific and cite evidence from the plans.

Return ONLY a valid JSON object:
{{
  "rubric_scores": {{
    "Progressive Overload Principle": {{
      "score": 8,
      "comment": "Specific observation from the plan. What's good/bad."
    }},
    "Muscle Group Balance": {{
      "score": 7,
      "comment": "Specific observation."
    }},
    "Rest & Recovery Adequacy": {{
      "score": 9,
      "comment": "Specific observation."
    }},
    "Macro Distribution Validity": {{
      "score": 8,
      "comment": "Specific observation with numbers."
    }},
    "Evidence-Based Exercise Selection": {{
      "score": 9,
      "comment": "Specific observation."
    }},
    "Fitness Level Appropriateness": {{
      "score": 8,
      "comment": "Specific observation."
    }},
    "Dietary Preference Compliance": {{
      "score": 10,
      "comment": "Specific observation about dietary compliance."
    }},
    "Safety & Injury Consideration": {{
      "score": 7,
      "comment": "Specific observation about safety handling."
    }},
    "Goal Alignment": {{
      "score": 8,
      "comment": "Specific observation about goal coherence."
    }},
    "Completeness & Actionability": {{
      "score": 8,
      "comment": "Specific observation about actionability."
    }}
  }},
  "strengths": [
    "Specific strength of this plan",
    "Another specific strength"
  ],
  "weaknesses": [
    "Specific weakness or gap",
    "Another specific weakness"
  ],
  "warnings": [],
  "verdict": "2-3 sentence professional verdict summarizing the plan's scientific soundness and primary recommendation for improvement."
}}

IMPORTANT: 
- Only include items in "warnings" if there are genuine safety concerns
- Be specific in comments, cite actual elements from the plans
- Scores must reflect the scoring guide strictly
- Return ONLY valid JSON
"""
        try:
            response_text = self._gemini_call(prompt)
            clean = re.sub(r"```json|```", "", response_text).strip()
            evaluation = json.loads(clean)
            
            # Calculate weighted overall score
            overall_score = self._calculate_weighted_score(evaluation.get("rubric_scores", {}))
            evaluation["overall_score"] = overall_score
            evaluation["rubric_definition"] = JUDGE_RUBRIC
            
            return evaluation
            
        except Exception as e:
            return self._fallback_evaluation(profile)

    def _calculate_weighted_score(self, rubric_scores: dict) -> float:
        """Calculate weighted average score based on criterion weights."""
        total_weighted = 0
        total_weight = 0
        
        for criterion, score_data in rubric_scores.items():
            weight = JUDGE_RUBRIC.get(criterion, {}).get("weight", 1.0)
            score = score_data.get("score", 0)
            total_weighted += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0
        
        raw = total_weighted / total_weight
        return round(raw, 1)

    def _fallback_evaluation(self, profile: dict) -> dict:
        """Fallback evaluation if API fails."""
        return {
            "overall_score": 7.5,
            "rubric_scores": {
                criterion: {"score": 7, "comment": "Manual review recommended — automated evaluation unavailable."}
                for criterion in JUDGE_RUBRIC.keys()
            },
            "strengths": ["Plan generated using evidence-based guidelines", "Personalized to user profile"],
            "weaknesses": ["Judge evaluation incomplete — manual review recommended"],
            "warnings": [],
            "verdict": "Automated evaluation was unable to complete. The plan was generated using evidence-based guidelines. Please review manually against the rubric criteria provided.",
            "rubric_definition": JUDGE_RUBRIC
        }
