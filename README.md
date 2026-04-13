# 💪 Fitness & Wellness Plan Builder

An AI-powered multi-agent system that generates personalized 4-week fitness & nutrition plans, evaluated by an independent LLM-as-Judge for scientific soundness.

---

## 🏗️ Architecture

```
User Profile Input
       │
       ▼
┌─────────────────────┐
│ Guidelines          │  ← Tavily Search (evidence-based research)
│ Researcher Agent    │  ← Gemini synthesis
└─────────┬───────────┘
          │ Evidence-based guidelines
          ▼
┌─────────────────────┐
│ Workout Planner     │  ← Gemini (4-week progressive plan)
│ Agent               │
└─────────┬───────────┘
          │
┌─────────────────────┐
│ Nutrition Advisor   │  ← Gemini (macros + meal plan)
│ Agent               │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ LLM-as-Judge        │  ← Independent Gemini call
│ (10-criterion rubric│  ← Weighted scoring
│  evaluation)        │
└─────────────────────┘
          │
          ▼
     Final Report
  (Plan + Judge Score)
```

## 🚀 Setup & Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Keys
- **Gemini API Key**: https://aistudio.google.com/ → Get API Key (Free tier available)
- **Tavily API Key**: https://tavily.com → Sign up (Free tier: 1000 searches/month)

### 3. Run the App
```bash
streamlit run app.py
```

### 4. Enter Keys in Sidebar
Enter your Gemini and Tavily API keys in the sidebar when prompted.

---

## ⚖️ LLM-as-Judge: Rubric Criteria

The judge evaluates on **10 criteria** with **weighted scoring**:

| Criterion | Weight | What It Checks |
|-----------|--------|----------------|
| Progressive Overload | 1.0x | Week-over-week intensity increase |
| Muscle Group Balance | 1.0x | Push/pull balance, no injury risk |
| Rest & Recovery | 1.0x | 48hr rule, deload week |
| Macro Distribution | 1.0x | Evidence-based protein/calorie targets |
| Exercise Selection | 1.0x | Equipment-feasible, compound-first |
| Fitness Level Match | 1.0x | Complexity matches stated level |
| **Dietary Compliance** | **1.5x** | Zero tolerance for preference violations |
| **Safety** | **1.5x** | Injury modifications applied |
| Goal Alignment | 1.0x | Every element targets stated goal |
| Actionability | 1.0x | Specific sets/reps/portions |

**Total weight: 11.0x → Normalized to /10 score**

### Score Interpretation
- **8-10**: Excellent — scientifically sound, ready to use
- **6-7**: Good — minor improvements recommended
- **< 6**: Needs improvement — review flagged criteria

---

## 📁 Project Structure

```
fitness_wellness_builder/
├── app.py                          # Streamlit UI
├── requirements.txt
├── README.md
└── agents/
    ├── __init__.py
    ├── guidelines_researcher.py    # Tavily + Gemini research agent
    ├── workout_planner.py          # 4-week plan generation
    ├── nutrition_advisor.py        # Macro + meal planning
    └── llm_judge.py               # Independent evaluation + rubric
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| UI / Frontend | Streamlit |
| Search Tool | Tavily Search API |
| LLM Provider | Google Gemini 2.0 Flash |
| Deployment | Streamlit Cloud / Railway / Vercel |

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo → select `app.py`
4. Add secrets in Settings:
   ```
   GEMINI_API_KEY = "your-key"
   TAVILY_API_KEY = "your-key"
   ```
   Or let users enter keys in the sidebar (current implementation).

## Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Set environment variables in Railway dashboard.

---

## ⚠️ Disclaimer

This application provides **general wellness information only** and is **not medical advice**. Always consult a qualified healthcare professional before starting any fitness or nutrition program, especially if you have pre-existing health conditions.

---

## 🎯 Hackathon Notes

This project implements:
- ✅ **Multi-agent pipeline** (4 specialized agents)
- ✅ **Tavily Search integration** for evidence-based research
- ✅ **LLM-as-Judge** with well-defined 10-criterion weighted rubric
- ✅ **Gemini 2.0 Flash** as LLM provider
- ✅ **Streamlit** frontend
- ✅ **Independent judge** (separate API call, no shared context with planners)
- ✅ **Fallback handling** for all agents
