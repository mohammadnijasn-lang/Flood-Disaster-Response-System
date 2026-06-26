from crewai import Agent
from .llm import llm

vision_agent = Agent(

    role="Satellite Vision Agent",

    goal="""
    Analyze flood extent from satellite imagery.
    """,

    backstory="""
    Remote sensing specialist.
    """,

    llm=llm,

    verbose=True
)