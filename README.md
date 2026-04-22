# ⚡ FORGE - AI-Powered Fitness & Wellness Plan Builder

> An intelligent multi-agent system that generates personalized 4-week fitness and nutrition plans, grounded in real-time research and evaluated by an LLM-as-Judge.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Gemini](https://img.shields.io/badge/Gemini-API-orange?style=flat-square&logo=google)
![Tavily](https://img.shields.io/badge/Tavily-Search-green?style=flat-square)
![Railway](https://img.shields.io/badge/Deployed-Railway-purple?style=flat-square&logo=railway)

---

## 🧩 Problem Statement

**User:** Fitness enthusiasts, beginners, and health-conscious individuals.

**Problem:** Generic fitness plans found online don't account for a person's unique goals, fitness level, available equipment, dietary restrictions, or health conditions. Hiring a personal trainer or nutritionist is expensive and inaccessible to most people.

**Why Agentic?** Creating a truly personalized fitness + nutrition plan requires multiple specialized tasks researching current evidence-based guidelines, structuring a progressive workout schedule, calculating macros, and evaluating the output for scientific validity. No single prompt can do all of this reliably. An agentic approach decomposes this into specialized agents, each with a focused role, producing a far more accurate and trustworthy result.

---

## 📋 Task Decomposition & Specs

The system breaks down the plan generation into **4 discrete agent tasks**:

| Step | Agent | Input | Output |
|------|-------|-------|--------|
| 1 | **Guidelines Researcher** | User profile | Evidence-based fitness & nutrition findings from the web |
| 2 | **Workout Planner** | Profile + Research | 4-week progressive workout schedule (sets, reps, days) |
| 3 | **Nutrition Advisor** | Profile + Research | Macro targets, meal plan, hydration & supplement guide |
| 4 | **LLM-as-Judge** | All outputs + Profile | Scientific score (0–10), rubric breakdown, strengths & warnings |

### Decision Points
- If no equipment selected → agent defaults to bodyweight-only exercises
- If health notes present → Workout Planner avoids contraindicated movements
- If dietary preference is Vegan/Vegetarian → Nutrition Advisor enforces strict compliance (1.5x weight in rubric)
- If Judge score < 6 → warnings are surfaced prominently in the UI

---

## 🏗️ Architecture Diagram

![image alt](https://github.com/AshviniGoswami/Forge/blob/278c325d319fd76dc2b4871062e22e8ec06bacd0/Architecutecture%20diagram.png)
```

---

## ✨ Features

- 🤖 **Multi-Agent Pipeline** - 4 specialized agents working sequentially
- 🔍 **Real-Time Research** - Tavily Search fetches current evidence-based guidelines
- 🏋️ **Progressive 4-Week Workout Plan** - Tailored to goal, level, equipment
- 🥗 **Full Nutrition Plan** - Macros, meals, hydration, supplements
- ⚖️ **LLM-as-Judge Evaluation** - 10-criterion rubric with scientific scoring
- 🎨 **Clean Light UI** - Built with Streamlit + custom CSS

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| LLM | Google Gemini API (`gemini-1.5-flash`) |
| Web Search | Tavily Search API |
| Language | Python 3.10+ |
| Deployment | Railway |

---

## 🚀 Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/AshviniGoswami/Forge.git
cd Forge
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Add your API keys in the sidebar
- **Gemini API Key** → [aistudio.google.com](https://aistudio.google.com)
- **Tavily API Key** → [tavily.com](https://tavily.com)

---

## 📁 Project Structure

```
Forge/
├── app.py                   # Main Streamlit app + UI
├── agents/
│   ├── guidelines_researcher.py   # Agent 1 — Tavily + Gemini research
│   ├── workout_planner.py         # Agent 2 — 4-week workout generator
│   ├── nutrition_advisor.py       # Agent 3 — Macro + meal planner
│   └── llm_judge.py               # Agent 4 — LLM-as-Judge evaluator
├── requirements.txt
├── Procfile                 # Railway deployment config
└── README.md
```

---

## ⚖️ LLM-as-Judge Rubric

The Judge agent evaluates the final plan across **10 scientific criteria**:

| Criterion | Weight |
|-----------|--------|
| Progressive Overload Principle | 1.0x |
| Muscle Group Balance | 1.0x |
| Rest & Recovery Adequacy | 1.0x |
| Macro Distribution Validity | 1.0x |
| Evidence-Based Exercise Selection | 1.0x |
| Fitness Level Appropriateness | 1.0x |
| **Dietary Preference Compliance** | **1.5x** |
| **Safety & Injury Consideration** | **1.5x** |
| Goal Alignment | 1.0x |
| Completeness & Actionability | 1.0x |

Scores are weighted, producing a final **0–10 scientific quality score**.

---

## 🌐 Deployed App

🔗 **Live URL:** `https://web-production-5abb8.up.railway.app/`

---

## ⚠️ Disclaimer

This app is for **general wellness purposes only** and does not constitute medical advice. Always consult a qualified healthcare professional before starting any fitness or nutrition program.

---

## 👨‍💻 Built By

**Ashvini Goswami** & **Deepjoti**
