
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

# Initialize Groq client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# Test AI connection
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are JARVIS, an intelligent virtual assistant. Help with general tasks, coding, and productivity. Respond naturally and clearly."
        },
        {
            "role": "user",
            "content": "Introduce yourself."
        }
    ]
)

print(completion.choices[0].message.content)
