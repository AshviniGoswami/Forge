"""
Nutrition Advisor Agent
------------------------
Creates an evidence-based nutrition overview using Gemini,
guided by research guidelines and user's dietary preferences.
"""

import json
import re
import requests


class NutritionAdvisor:
    def __init__(self, gemini_api_key: str):
        self.gemini_key = gemini_api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    def _gemini_call(self, prompt: str) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 3072}
        }
        resp = requests.post(self.gemini_url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def create_plan(self, profile: dict, guidelines: dict) -> dict:
        """
        Generate a comprehensive nutrition overview.
        """
        goal = profile["fitness_goal"]
        dietary = profile["dietary_preference"]
        age = profile["age"]
        nutrition_guideline = guidelines.get("findings", {}).get("Nutrition Science", "")

        prompt = f"""
You are a registered sports dietitian creating a nutrition overview (not medical advice).

USER PROFILE:
- Fitness Goal: {goal}
- Dietary Preference: {dietary}
- Age: {age}
- Training Days/Week: {profile['days_per_week']}
- Health Notes: {profile['health_notes']}

EVIDENCE-BASED NUTRITION GUIDELINES:
{nutrition_guideline}

Create a practical nutrition overview. Assume an average adult body weight of 70-75kg for calculations.
Adjust calorie estimates based on goal:
- Muscle Building: slight surplus (~300-500 cal above maintenance)
- Weight Loss: moderate deficit (~400-600 cal below maintenance)  
- Endurance/General Fitness: maintenance calories
- Flexibility: maintenance with emphasis on anti-inflammatory foods

STRICT RULES:
1. ALL food suggestions must comply with: {dietary} diet. Zero tolerance for violations.
2. If "No Restriction", suggest a balanced omnivore diet
3. If "Vegetarian", NO meat or fish. Eggs and dairy OK
4. If "Vegan", NO animal products whatsoever
5. If "Keto", keep carbs under 50g/day, high fat
6. If "Mediterranean", emphasize olive oil, fish, legumes, vegetables
7. If "High Protein", prioritize protein in every meal

Return ONLY a valid JSON object:
{{
  "macros": {{
    "calories": "~2200 kcal/day",
    "protein": "~165g/day (2.2g/kg)",
    "carbs": "~220g/day",
    "fats": "~73g/day",
    "rationale": "Brief explanation of why these macros suit the goal"
  }},
  "meals": {{
    "Breakfast (7-8 AM)": "Detailed breakfast description with specific foods, portions, and macro breakdown. Must be {dietary} compliant.",
    "Pre-Workout Snack (1hr before training)": "Specific snack options with portions.",
    "Lunch (12-1 PM)": "Detailed lunch with specific foods and portions.",
    "Post-Workout Nutrition (within 30-45 min)": "Recovery meal/shake details with rationale.",
    "Dinner (6-7 PM)": "Detailed dinner with specific foods and portions.",
    "Optional Evening Snack": "If needed for calorie goals."
  }},
  "hydration": {{
    "daily_target": "~2.5-3L water/day",
    "training_days": "Add 500-750ml per hour of training",
    "tips": "Practical hydration tips"
  }},
  "supplements": {{
    "recommended": ["Creatine Monohydrate 3-5g/day (well-researched)", "Vitamin D3 2000IU (if limited sun)"],
    "optional": ["Omega-3 Fish Oil 2g/day"],
    "disclaimer": "Consult a healthcare provider before starting supplements"
  }},
  "tips": [
    "Actionable nutrition tip 1",
    "Actionable nutrition tip 2",
    "Actionable nutrition tip 3",
    "Actionable nutrition tip 4",
    "Actionable nutrition tip 5"
  ],
  "foods_to_prioritize": ["food1", "food2", "food3", "food4", "food5"],
  "foods_to_minimize": ["food1", "food2", "food3"]
}}

Return ONLY valid JSON.
"""
        try:
            response_text = self._gemini_call(prompt)
            clean = re.sub(r"```json|```", "", response_text).strip()
            plan = json.loads(clean)
            return plan
        except Exception:
            return self._fallback_nutrition(profile)

    def _fallback_nutrition(self, profile: dict) -> dict:
        """Fallback nutrition plan."""
        goal = profile["fitness_goal"]
        dietary = profile["dietary_preference"]
        
        is_vegan = "Vegan" in dietary
        protein_source = "tofu/legumes/tempeh" if is_vegan else "chicken/eggs/fish"
        
        calorie_map = {
            "Build Muscle": "~2400 kcal/day",
            "Lose Weight": "~1800 kcal/day",
            "Build Endurance": "~2200 kcal/day",
            "General Fitness": "~2000 kcal/day",
            "Improve Flexibility": "~2000 kcal/day"
        }
        
        return {
            "macros": {
                "calories": calorie_map.get(goal, "~2000 kcal/day"),
                "protein": "~150g/day",
                "carbs": "~200g/day",
                "fats": "~65g/day",
                "rationale": f"Balanced macros optimized for {goal.lower()}"
            },
            "meals": {
                "Breakfast (7-8 AM)": f"Oats with {protein_source}, berries, and nuts — ~500 kcal, 30g protein",
                "Pre-Workout Snack": "Banana with almond butter — ~200 kcal, fast-acting carbs",
                "Lunch (12-1 PM)": f"Large salad with {protein_source}, quinoa, olive oil — ~600 kcal, 40g protein",
                "Post-Workout Nutrition": f"Protein shake or {protein_source} with rice — ~350 kcal, 35g protein",
                "Dinner (6-7 PM)": f"{protein_source} with roasted vegetables and sweet potato — ~550 kcal, 40g protein",
                "Optional Evening Snack": "Greek yogurt or casein protein shake"
            },
            "hydration": {
                "daily_target": "~2.5-3L water/day",
                "training_days": "Add 500ml per hour of training",
                "tips": "Drink 500ml water first thing in the morning"
            },
            "supplements": {
                "recommended": ["Creatine Monohydrate 3-5g/day", "Vitamin D3 2000IU"],
                "optional": ["Omega-3 2g/day"],
                "disclaimer": "Consult a healthcare provider before starting supplements"
            },
            "tips": [
                "Eat protein with every meal",
                "Meal prep on Sundays to stay consistent",
                "Track food intake for at least the first 2 weeks",
                "Don't skip post-workout nutrition — critical for recovery",
                "Prioritize sleep — it's when muscle is actually built"
            ],
            "foods_to_prioritize": ["Lean proteins", "Complex carbs", "Leafy greens", "Healthy fats", "Colorful vegetables"],
            "foods_to_minimize": ["Ultra-processed foods", "Excess alcohol", "Sugary drinks"]
        }
