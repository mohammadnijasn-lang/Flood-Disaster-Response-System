from crewai import Agent
from .llm import llm

route_agent = Agent(

    role="Safe Route Agent",

    goal="""
    Evaluate evacuation route safety.
    """,

    backstory="""
    Emergency evacuation planner.
    """,

    llm=llm,

    verbose=True
)