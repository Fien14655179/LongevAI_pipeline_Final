import os
import time
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_LLM_MODEL
import logging

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def generate_report(profile, top_actions, retries=3):
    name = profile["name"]
    goal = profile["primary_goal"]
    biomarkers = profile["biomarkers"]
    diet = profile["current_lifestyle"]["diet_summary"]
    exercise = profile["current_lifestyle"]["exercise_frequency"]

    actions_text = ""
    for i, action in enumerate(top_actions, 1):
        actions_text += f"{i}. {action['title']} ({action['category']}): {action['description']}\n"

    prompt = f"""
You are a longevity health coach writing a personalized health blueprint for a client.

Client: {name}
Primary Goal: {goal}
Diet: {diet}
Exercise: {exercise}
Biomarkers: {biomarkers}

Based on this data, the following actions have been identified as most relevant:
{actions_text}

Write a personalized health blueprint in JSON format with:
1. "executive_summary": A 3-4 sentence personalized overview directly referencing the client's data and goal.
2. "action_cards": A list of action cards, one per recommended action, each with:
   - "category": the category from the action
   - "priority_level": High, Medium, or Low based on the biomarkers
   - "title": a personalized title referencing the client
   - "description": a 2-3 sentence personalized description referencing their specific biomarkers

Respond ONLY with valid JSON, no extra text.
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=OPENROUTER_LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            wait = 2 ** attempt
            if attempt < retries - 1:
                logger.warning(f"LLM call failed for {name} (attempt {attempt + 1}/{retries}). Retrying in {wait}s... Error: {str(e)}")
                time.sleep(wait)
            else:
                logger.error(f"LLM call failed for {name} after {retries} attempts. Error: {str(e)}")
                raise e