from dotenv import load_dotenv
import os

load_dotenv("config/.env")

print("🔍 Environment Variables Check:")
for key in ["OPENAI_API_KEY", "SEMANTIC_SCHOLAR_API_KEY", "HUGGINGFACE_TOKEN"]:
    val = os.getenv(key)
    print(f"{key}: {'✅ Set' if val else '❌ Missing'}")
