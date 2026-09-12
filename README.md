# LessonLoop

“LessonLoop turns today's exit-ticket responses into actionable improvements for tomorrow's lesson plan.”

## Problem
Teachers often collect useful exit-ticket evidence but have little time to translate it into tomorrow's instruction.

## Solution
LessonLoop analyzes response patterns, surfaces strengths and misconceptions, groups students for differentiation, and recommends targeted, evidence-based changes to the teacher's existing plan.

## Tech stack
Python, Streamlit, Google Gemini API (free tier).

## Setup
1. Create a virtual environment and install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`.
3. Run: `streamlit run app.py`

`GEMINI_MODEL` is optional and can override the default model.

## Demo
Click **Load Demo Data**, then **Analyze Class Understanding**, review the evidence, and click **Improve Tomorrow's Lesson**. The demo uses a sixth-grade fractions lesson with ten varied responses.
