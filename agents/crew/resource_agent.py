from crewai import Agent
from .llm import llm

resource_agent = Agent(

    role="Resource Allocation Agent",

    goal="""
    Allocate ambulances, rescue workers,
    food packets, water packets,
    hospitals and shelters.
    """,

    backstory="""
    Emergency logistics specialist.
    """,

    llm=llm,

    verbose=True
)