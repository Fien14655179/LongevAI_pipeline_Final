import json
import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, ACTIONS_LIBRARY_PATH, TOP_K_ACTIONS

model = SentenceTransformer(EMBEDDING_MODEL)

def load_actions():
    with open(ACTIONS_LIBRARY_PATH, "r") as f:
        data = json.load(f)
    return data["actions"]

def get_user_text(profile):
    return f"""
    Goal: {profile['primary_goal']}
    Diet: {profile['current_lifestyle']['diet_summary']}
    Exercise: {profile['current_lifestyle']['exercise_frequency']}
    Biomarkers: {json.dumps(profile['biomarkers'])}
    """

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_top_actions(profile):
    actions = load_actions()
    
    user_text = get_user_text(profile)
    user_embedding = model.encode(user_text)
    
    action_texts = [f"{a['title']} {a['description']}" for a in actions]
    action_embeddings = model.encode(action_texts)
    
    scores = [cosine_similarity(user_embedding, ae) for ae in action_embeddings]
    
    top_indices = np.argsort(scores)[::-1][:TOP_K_ACTIONS]
    
    top_actions = []
    for i in top_indices:
        action = actions[i].copy()
        action["relevance_score"] = round(float(scores[i]), 4)
        top_actions.append(action)
    
    return top_actions