import os

os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

from crewai import Agent, Task, Crew, LLM

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

# ------------------------
# AGENTS
# ------------------------

# climate_agent = Agent(
#     role="Climate Analyst",
#     goal="Analyze rainfall and weather risk.",
#     backstory="Expert disaster meteorologist.",
#     llm=llm
# )

# vision_agent = Agent(
#     role="Vision Analyst",
#     goal="Analyze drone observations.",
#     backstory="Expert drone vision analyst.",
#     llm=llm
# )

# resource_agent = Agent(
#     role="Resource Manager",
#     goal="Analyze resource allocation.",
#     backstory="Emergency logistics expert.",
#     llm=llm
# )

# route_agent = Agent(
#     role="Route Planner",
#     goal="Analyze evacuation route.",
#     backstory="Disaster transportation expert.",
#     llm=llm
# )

# coordinator_agent = Agent(
#     role="Disaster Coordinator",
#     goal="Generate the final disaster response plan.",
#     backstory="National Disaster Response Coordinator.",
#     llm=llm
# )


# ------------------------
# CREW
# ------------------------

def run_disaster_analysis(

    district,

    weather,

    vision,

    resource_plan,

    route_info,

    notification_status

):
    
    # ------------------------
    # CREATE NEW AGENTS
    # ------------------------

    climate_agent = Agent(
        role="Climate Analyst",
        goal="Analyze rainfall and weather risk.",
        backstory="Expert disaster meteorologist.",
        llm=llm
    )

    vision_agent = Agent(
        role="Vision Analyst",
        goal="Analyze drone observations.",
        backstory="Expert drone vision analyst.",
        llm=llm
    )

    resource_agent = Agent(
        role="Resource Manager",
        goal="Analyze resource allocation.",
        backstory="Emergency logistics expert.",
        llm=llm
    )

    route_agent = Agent(
        role="Route Planner",
        goal="Analyze evacuation route.",
        backstory="Disaster transportation expert.",
        llm=llm
    )

    coordinator_agent = Agent(
        role="Disaster Coordinator",
        goal="Generate the final disaster response plan.",
        backstory="National Disaster Response Coordinator.",
        llm=llm
    )

    climate_task = Task(

        description=f"""

    District : {district}

    Rainfall : {weather['rainfall_24h']} mm

    Weather : {weather['weather']}

    Alert : {weather['alert']}

    Explain the weather risk.

    """,

        expected_output="Weather analysis.",

        agent=climate_agent
    )

    vision_task = Task(

        description=f"""

    Flood Severity : {vision['severity']}

    People At Risk : {vision['people_at_risk']}

    Road Blocked : {vision['road_blocked']}

    Recommendation :

    {vision['recommendation']}

    """,

        expected_output="Vision analysis.",

        agent=vision_agent
    )

    notification_task = Task(

        description=f"""

    Notification Status

    {notification_status}

    """,

        expected_output="Notification report.",

        agent=resource_agent
    )

    resource_task = Task(

        description=f"""

    Priority

    {resource_plan['priority']}

    Dispatch

    {resource_plan['dispatch']}

    Resources

    {resource_plan['resources']}

    """,

        expected_output="Resource deployment report.",

        agent=resource_agent
    )

    route_task = Task(

        description=f"""

    Evacuation Route

    {route_info}

    """,

        expected_output="Evacuation route report.",

        agent=route_agent
    )

    coordination_task = Task(

    description="""

    You are preparing a Disaster Control Room summary.

    Generate ONLY a short operational report.

    Format EXACTLY like this:

    🚨 AI Disaster Summary

    📍 Location:
    🌊 Flood Severity:
    🔴 Priority:
    👥 People at Risk:
    🚧 Road Status:
    🚑 Resources:
    🏥 Rescue Station:
    🏠 Shelter:
    📢 Citizens Alerted:
    🎯 Immediate Actions:

    Rules:

    - Maximum 10 lines.
    - No paragraphs.
    - No explanations.
    - No recommendations longer than one sentence.
    - Be concise.
    - Focus only on what the disaster officer needs to do immediately.

    """,

    expected_output="Short disaster control room summary.",

    context=[

        climate_task,

        vision_task,

        notification_task,

        resource_task,

        route_task

    ],

    agent=coordinator_agent

)

    crew = Crew(

        agents=[

            climate_agent,

            vision_agent,

            resource_agent,

            route_agent,

            coordinator_agent

        ],

        tasks=[

            climate_task,

            vision_task,

            notification_task,

            resource_task,

            route_task,

            coordination_task

        ]

    )

    result = crew.kickoff()

    return str(result)