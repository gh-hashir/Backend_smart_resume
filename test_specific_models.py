import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=key)

# Exact names from the previous list_models output
models_to_try = [
    'gemini-flash-latest',
    'gemini-pro-latest',
    'gemini-2.0-flash-lite-preview-09-2025', # seen in list
    'gemini-1.5-flash-8b'
]

for model_name in models_to_try:
    print(f"Testing model: {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"  Success with {model_name}: {response.text[:20]}...")
        break
    except Exception as e:
        print(f"  Failed with {model_name}: {e}")
