import os
import google.generativeai as genai

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
else:
    genai.configure(api_key=api_key)
    models = genai.list_models()
    print("Available Gemini models for your API key:")
    for m in models:
        print(m)