# Cognify 🧠 – Clarity from Chaos, powered by Agentic AI

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cognify-app.streamlit.app)

Cognify is an AI-powered executive function assistant designed to help users navigate overwhelming tasks by breaking them down into clear, manageable steps. It leverages a multi-agent system built with **CrewAI** and **LangChain** to provide a supportive, human-in-the-loop planning experience.

App URL : https://cognify-app.streamlit.app

## 🤔 The Problem

We all know the feeling: staring at a task that’s too big, too vague, and you don’t know where to start. This mental clutter can lead to procrastination and overwhelm. Cognify is designed to be a gentle partner in these moments, guiding you from a state of chaos to a clear, actionable plan.

## ✨ How It Works

Cognify uses a collaborative team of specialized AI agents to transform a user's vague goal into a concrete plan. The entire process is conversational and adaptive.

1️⃣ **The Clarifier Agent:** A user starts by entering a thought or goal (e.g., "I want to buy a new phone"). The Clarifier analyzes this and proposes a more specific, actionable goal (e.g., "Research and purchase a specific phone model within your budget").

2️⃣ **The Planner Agent:** Once the user accepts the clarified goal, the Planner, acting as a compassionate productivity coach, designs a gentle, step-by-step plan. This plan includes concrete actions and scheduled breaks to prevent burnout.

3️⃣ **The Refiner Agent:** Plans often need to change. The user can have a conversation with the Refiner Agent (e.g., "my budget is $500") to modify, add, or remove steps. The agent intelligently integrates the feedback, ensuring the plan remains relevant and helpful.

## 🛠️ Tech Stack Showcase

This project utilizes a modern, AI-native stack to create a sophisticated agentic workflow.

* **AI Frameworks:** **CrewAI** & **LangChain** (For defining agents, tasks, and managing the collaborative process).
* **LLM:** **OpenAI** (GPT-4).
* **Interface:** **Streamlit** & **Python** (For building the interactive web application).

## 🚀 Running Locally

To run Cognify on your own machine, follow these steps:

### 1. Prerequisites
* Python 3.8+
* An OpenAI API Key

### 2. Clone the Repository
```bash
git clone https://github.com/vivek-suryavanshi/cognify.git
cd cognify
