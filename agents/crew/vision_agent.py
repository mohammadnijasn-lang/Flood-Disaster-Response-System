from crewai import Agent
from .llm import llm

vision_agent = Agent(

    role="Drone Vision Agent",

    goal="""
    Analyze uploaded drone imagery,
    detect trapped people,
    blocked roads,
    vehicles,
    and rescue urgency.
    """,

    backstory="""
    Remote sensing specialist.
    """,

    llm=llm,

    verbose=True
)