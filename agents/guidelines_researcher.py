"""
Guidelines Researcher Agent
----------------------------
Uses Tavily Search to find evidence-based fitness & nutrition guidelines
relevant to the user's profile, then summarizes with Gemini.
"""

import json
import re
import requests


class GuidelinesResearcher:
    def __init__(self, gemini_api_key: str, tavily_api_key: str):
        self.gemini_key = gemini_api_key
        self.tavily_key = tavily_api_key
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"

    def _tavily_search(self, query: str, max_results: int = 5) -> list[dict]:
        """Call Tavily Search API and return list of results."""
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": False
        }
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])

    def _gemini_call(self, prompt: str) -> str:
        """Call Gemini API and return text response."""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048}
        }
        resp = requests.post(self.gemini_url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def research(self, profile: dict) -> dict:
        """
        Main research method:
        1. Build targeted search queries from user profile
        2. Search Tavily for evidence-based guidelines
        3. Synthesize findings with Gemini
        4. Return structured guidelines dict
        """
        goal = profile["fitness_goal"]
        level = profile["fitness_level"]
        dietary = profile["dietary_preference"]
        equipment = profile["equipment"]

        # Build targeted queries
        queries = [
            f"evidence based {goal.lower()} workout guidelines exercise science 2024",
            f"optimal training frequency volume {goal.lower()} {level.lower()} exercisers",
            f"nutrition guidelines {goal.lower()} macros protein intake research",
            f"{dietary.lower()} diet performance fitness research",
            f"progressive overload principles {level.lower()} athletes"
        ]

        # Collect Tavily results
        all_results = []
        sources = []
        for query in queries[:4]:
            try:
                results = self._tavily_search(query, max_results=3)
                all_results.extend(results)
                for r in results:
                    if r.get("url"):
                        sources.append(f"{r.get('title', 'Source')} — {r['url']}")
            except Exception:
                pass

        # Prepare context from Tavily
        tavily_context = "\n\n".join([
            f"Source: {r.get('title', 'Unknown')}\nURL: {r.get('url', '')}\nContent: {r.get('content', '')[:600]}"
            for r in all_results[:10]
        ])

        # Synthesize with Gemini
        synthesis_prompt = f"""
You are a sports science expert synthesizing research for a fitness professional.

USER PROFILE:
- Goal: {goal}
- Fitness Level: {level}
- Equipment: {', '.join(equipment)}
- Dietary Preference: {dietary}
- Age: {profile['age']}
- Days per week: {profile['days_per_week']}
- Health notes: {profile['health_notes']}

RESEARCH FINDINGS FROM TAVILY:
{tavily_context}

Synthesize the above research into a structured JSON response with this exact format:
{{
  "findings": {{
    "Training Volume & Frequency": "Specific guidelines with numbers (sets, reps, frequency)...",
    "Progressive Overload Strategy": "How to progress over 4 weeks for this goal/level...",
    "Recovery & Rest Principles": "Specific recovery guidelines...",
    "Nutrition Science": "Evidence-based macros and timing for this goal...",
    "Exercise Selection Principles": "Which exercises are most effective for this goal/equipment..."
  }},
  "key_recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3",
    "Specific actionable recommendation 4",
    "Specific actionable recommendation 5"
  ],
  "safety_flags": [
    "Any safety considerations based on profile"
  ]
}}

Be specific with numbers. No vague advice. Return ONLY valid JSON.
"""
        try:
            response_text = self._gemini_call(synthesis_prompt)
            clean = re.sub(r"```json|```", "", response_text).strip()
            findings = json.loads(clean)
        except Exception:
            # Fallback structured guidelines
            findings = self._fallback_guidelines(profile)

        findings["sources"] = sources[:8] if sources else ["Evidence-based fitness research (NSCA, ACSM guidelines)"]
        findings["sources_count"] = len(sources)
        return findings

    def _fallback_guidelines(self, profile: dict) -> dict:
        """Fallback guidelines when API calls fail."""
        return {
            "findings": {
                "Training Volume & Frequency": f"For {profile['fitness_goal']}: 10-20 working sets per muscle group per week. Train each muscle 2x/week minimum for hypertrophy.",
                "Progressive Overload Strategy": "Increase weight by 2.5-5% or add 1-2 reps per week. Track performance every session.",
                "Recovery & Rest Principles": "48-72 hours between same muscle groups. 7-9 hours sleep. Deload every 4th week.",
                "Nutrition Science": "1.6-2.2g protein/kg bodyweight. Time protein within 2 hours of training. Stay hydrated at 35ml/kg bodyweight.",
                "Exercise Selection Principles": "Compound movements first (squat, hinge, push, pull). Isolation exercises supplementary."
            },
            "key_recommendations": [
                "Train each muscle group 2x per week minimum",
                "Progressive overload is the #1 driver of adaptation",
                "Protein intake 1.6-2.2g/kg/day is essential",
                "Sleep 7-9 hours for optimal recovery",
                "Track your workouts to ensure consistent progression"
            ],
            "safety_flags": ["Always warm up 5-10 minutes before training"]
        }
