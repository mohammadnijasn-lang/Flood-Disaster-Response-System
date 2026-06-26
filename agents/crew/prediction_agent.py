from crewai import Agent
from .llm import llm

prediction_agent = Agent(

    role="Flood Prediction Agent",

    goal="""
    Analyze flood severity and affected regions.
    """,

    backstory="""
    Expert flood forecaster.
    """,

    llm=llm,

    verbose=True
)