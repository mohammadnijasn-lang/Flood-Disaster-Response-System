# import google.generativeai as genai
# import os

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# model = genai.GenerativeModel("gemini-2.5-flash")

# response = model.generate_content("Hello")

# print(response.text)

# from dotenv import load_dotenv
# import os

# load_dotenv()

# print(os.getenv("GEMINI_API_KEY"))

from dotenv import load_dotenv
import os

load_dotenv()

from crewai import LLM

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

response = llm.call("Say hello in one sentence.")

print(response)