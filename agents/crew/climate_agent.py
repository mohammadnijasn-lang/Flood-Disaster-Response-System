from crewai import Agent
from .llm import llm

climate_agent = Agent(

    role="Climate Alert Agent",

    goal="""
    Determine flood alert level from hydro coverage and flood area.
    """,

    backstory="""
    Expert meteorologist and disaster analyst.
    """,

    llm=llm,

    verbose=True
)