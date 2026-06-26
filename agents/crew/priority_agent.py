from crewai import Agent
from .llm import llm

priority_agent = Agent(

    role="Priority Allocation Agent",

    goal="""
    Determine which shelter
    and hospital should be used first.
    """,

    backstory="""
    Disaster logistics expert.
    """,

    llm=llm,

    verbose=True
)
