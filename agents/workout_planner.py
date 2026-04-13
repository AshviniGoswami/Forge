"""
Workout Planner Agent
----------------------
Creates a detailed 4-week workout schedule using Gemini,
guided by the evidence-based guidelines from the researcher.
"""

import json
import re
import requests


class WorkoutPlanner:
    def __init__(self, gemini_api_key: str):
        self.gemini_key = gemini_api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    def _gemini_call(self, prompt: str) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 4096}
        }
        resp = requests.post(self.gemini_url, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def create_plan(self, profile: dict, guidelines: dict) -> dict:
        """
        Generate a complete 4-week workout plan based on profile and research.
        """
        goal = profile["fitness_goal"]
        level = profile["fitness_level"]
        equipment = ", ".join(profile["equipment"])
        days = profile["days_per_week"]
        health = profile["health_notes"]
        
        key_recs = guidelines.get("key_recommendations", [])
        training_guideline = guidelines.get("findings", {}).get("Training Volume & Frequency", "")
        overload_guideline = guidelines.get("findings", {}).get("Progressive Overload Strategy", "")
        safety_flags = guidelines.get("safety_flags", [])

        prompt = f"""
You are an expert certified personal trainer (NSCA-CSCS) creating a 4-week workout plan.

USER PROFILE:
- Goal: {goal}
- Fitness Level: {level}  
- Available Equipment: {equipment}
- Training Days per Week: {days}
- Health Notes: {health}
- Age: {profile['age']}

EVIDENCE-BASED GUIDELINES TO FOLLOW:
- Training Volume: {training_guideline}
- Progressive Overload: {overload_guideline}
- Safety: {', '.join(safety_flags)}
- Key Recommendations: {', '.join(key_recs)}

Create a complete 4-week progressive workout plan. Each week should have a theme and progressively harder than the last.

For {days} training days per week, include rest days appropriately.
Days available: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

Return ONLY a valid JSON object in this exact structure:
{{
  "plan_title": "4-Week {goal} Plan for {level}",
  "overview": "Brief overview of the plan's structure and progression philosophy",
  "weeks": {{
    "1": {{
      "theme": "Foundation",
      "focus": "Learning movement patterns, establishing baseline",
      "days": {{
        "Monday": {{
          "type": "Training",
          "muscle_groups": "Chest, Shoulders, Triceps",
          "exercises": [
            "Push-ups: 3 sets x 10-12 reps (60s rest)",
            "Pike Push-ups: 3 sets x 8-10 reps (60s rest)",
            "Tricep Dips: 3 sets x 10-12 reps (60s rest)"
          ]
        }},
        "Tuesday": {{
          "type": "Rest",
          "muscle_groups": "",
          "exercises": []
        }}
      }}
    }},
    "2": {{...same structure, harder...}},
    "3": {{...same structure, harder...}},
    "4": {{...same structure, peak/deload...}}
  }},
  "progression_notes": "How to track and apply progressive overload",
  "warm_up": "5-10 min warm-up routine to do before each session",
  "cool_down": "5 min cool-down and stretching routine"
}}

RULES:
1. Only use exercises possible with: {equipment}
2. Week 1 → Week 4 must show clear progressive overload (more reps, sets, or harder variation)
3. If health notes mention injuries, MODIFY exercises accordingly
4. Include ALL 7 days (training or rest)
5. Be specific: exact sets, reps, rest periods
6. For {level} level: {"stick to basics, proper form focus" if level == "Beginner" else "include periodization and tempo work" if level == "Advanced" else "moderate complexity"}

Return ONLY valid JSON. No markdown, no explanation.
"""
        try:
            response_text = self._gemini_call(prompt)
            clean = re.sub(r"```json|```", "", response_text).strip()
            plan = json.loads(clean)
            return plan
        except Exception as e:
            return self._fallback_plan(profile)

    def _fallback_plan(self, profile: dict) -> dict:
        """Minimal fallback workout plan."""
        days = profile["days_per_week"]
        goal = profile["fitness_goal"]
        
        workout_days = ["Monday", "Wednesday", "Friday", "Saturday"][:days]
        rest_days = [d for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] if d not in workout_days]
        
        base_days = {}
        workouts = [
            ("Push Day", "Chest, Shoulders, Triceps", ["Push-ups: 3x12", "Pike Push-ups: 3x10", "Tricep Dips: 3x12"]),
            ("Pull Day", "Back, Biceps", ["Pull-ups/Rows: 3x10", "Face Pulls: 3x15", "Bicep Curls: 3x12"]),
            ("Legs Day", "Quadriceps, Hamstrings, Glutes", ["Squats: 3x15", "Lunges: 3x12 each", "Glute Bridges: 3x20"]),
            ("Full Body", "Full Body", ["Burpees: 3x10", "Mountain Climbers: 3x20", "Plank: 3x45s"]),
        ]
        
        for i, day in enumerate(workout_days):
            w = workouts[i % len(workouts)]
            base_days[day] = {"type": "Training", "muscle_groups": w[1], "exercises": w[2]}
        
        for day in rest_days:
            base_days[day] = {"type": "Rest", "muscle_groups": "", "exercises": []}
        
        return {
            "plan_title": f"4-Week {goal} Plan",
            "overview": f"A progressive 4-week plan for {goal.lower()} with {days} training days per week.",
            "weeks": {
                "1": {"theme": "Foundation", "focus": "Establish movement patterns", "days": base_days},
                "2": {"theme": "Build", "focus": "Increase volume", "days": base_days},
                "3": {"theme": "Intensify", "focus": "Peak intensity", "days": base_days},
                "4": {"theme": "Peak & Deload", "focus": "Test progress, reduce volume", "days": base_days}
            },
            "progression_notes": "Add 1-2 reps each week, then increase weight/difficulty.",
            "warm_up": "5 min: jumping jacks, arm circles, hip rotations, light jog",
            "cool_down": "5 min: child's pose, hip flexor stretch, chest opener, forward fold"
        }
