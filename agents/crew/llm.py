from crewai import LLM
import os

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)
print("Gemini Key:", os.getenv("GEMINI_API_KEY"))