from crewai import Agent
from .llm import llm

resource_agent = Agent(

    role="Resource Allocation Agent",

    goal="""
    Analyze emergency priority, allocate rescue resources,
    and recommend the required response level.
    """,

    backstory="""
    Emergency logistics specialist.
    """,

    llm=llm,

    verbose=True
)