# Project Context: AI-Powered Restaurant Recommendation System

## Overview

Build an **AI-powered restaurant recommendation service** inspired by **Zomato**. The system suggests restaurants based on user preferences by combining **structured restaurant data** with a **Large Language Model (LLM)** to produce personalized, human-like recommendations.

---

## Objective

Design and implement an application that:

1. **Accepts user preferences** — location, budget, cuisine, ratings, and other constraints
2. **Uses a real-world restaurant dataset** — Zomato data from Hugging Face
3. **Leverages an LLM** — generates personalized, natural-language recommendations
4. **Displays clear, useful results** — ranked restaurants with explanations

---

## Data Source

| Item | Detail |
|------|--------|
| **Dataset** | Zomato restaurant recommendation dataset |
| **URL** | https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation |
| **Relevant fields** | Restaurant name, location, cuisine, cost, rating, and related attributes |

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- Extract relevant fields: restaurant name, location, cuisine, cost, rating, etc.

### 2. User Input

Collect user preferences:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional** | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare restaurant data based on user input
- Pass structured (filtered) results into an LLM prompt
- Design a prompt that helps the LLM **reason** and **rank** options

### 4. Recommendation Engine

Use the LLM to:

- **Rank** restaurants
- **Explain** why each recommendation fits the user
- **Optionally summarize** the overall choice set

### 5. Output Display

Present top recommendations in a user-friendly format. Each recommendation should include:

| Field | Description |
|-------|-------------|
| Restaurant Name | Name of the venue |
| Cuisine | Type(s) of food served |
| Rating | User/restaurant rating |
| Estimated Cost | Price or cost band |
| AI-generated explanation | Why this restaurant was recommended |

---

## Architecture Summary

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│ Hugging Face│────▶│ Data Ingestion   │────▶│ Filter by user  │────▶│ LLM Prompt   │
│ Zomato DS   │     │ & Preprocessing  │     │ preferences     │     │ + Ranking    │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────┬───────┘
                                                                              │
┌─────────────┐     ┌──────────────────┐                                      ▼
│ User        │────▶│ Preference       │                              ┌──────────────┐
│ Preferences │     │ Collection       │                              │ Recommendations
└─────────────┘     └──────────────────┘                              │ + Explanations
                                                                        └──────────────┘
```

---

## Key Technical Requirements

- **Structured filtering** before LLM invocation (location, budget, cuisine, rating, extras)
- **Prompt engineering** for ranking and reasoning over filtered candidates
- **LLM integration** for ranking, explanations, and optional summaries
- **User-facing output** with structured fields plus natural-language rationale

---

## Success Criteria

- Recommendations align with stated preferences (location, budget, cuisine, rating)
- Results are grounded in real dataset records (not hallucinated restaurants)
- Explanations are clear, personalized, and tied to user input
- Output is readable and actionable for end users

---

## Out of Scope (unless extended)

This problem statement does not specify:

- Deployment platform (web, CLI, API)
- Specific LLM provider or model
- Authentication or user accounts
- Real-time Zomato API integration (dataset-only)

Clarify these when implementing.

---

## Reference

- **Source document:** `PROBLEMSTATEMENT.TXT`
- **Dataset:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
