from crewai import Agent
from .llm import llm

coordination_agent = Agent(

    role="Disaster Coordination Agent",

    goal="""
    Combine all reports and generate
    final disaster response plan.
    """,

    backstory="""
    National disaster response commander.
    """,
    

    llm=llm,

    verbose=True
)