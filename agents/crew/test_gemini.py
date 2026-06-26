# from langchain_google_genai import ChatGoogleGenerativeAI
# import os

# os.environ["GOOGLE_API_KEY"] = ""

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash"
# )

# response = llm.invoke(
#     "What is a flood?"
# )

# print(response.content)

# from langchain_ollama import ChatOllama

# llm = ChatOllama(
#     model="llama3"
# )

# response = llm.invoke(
#     "Explain flood risk in one sentence"
# )

# print(response.content)

# from crewai import Agent
# from crewai import Task
# from crewai import Crew
# from crewai import LLM

# llm = LLM(
#     model="ollama/llama3",
#     base_url="http://localhost:11434"
# )

# agent = Agent(

#     role="Flood Analyst",

#     goal="Analyze flood risk",

#     backstory="Flood expert",

#     llm=llm
# )

# task = Task(

#     description="""
#     Hydro Coverage = 13.77%

#     Flood Area = 4.26%

#     Determine alert level.
#     """,

#     expected_output="""
#     Alert level with explanation.
#     """,

#     agent=agent
# )

# crew = Crew(

#     agents=[agent],

#     tasks=[task]
# )

# result = crew.kickoff()

# print(result)


from llm import llm

print(
    llm.call(
        "What is flood risk?"
    )
)