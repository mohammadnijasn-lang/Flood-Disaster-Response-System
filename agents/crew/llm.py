from crewai import LLM

llm = LLM(
    model="ollama/llama3",
    base_url="http://localhost:11434"
)