from importlib import resources

from crewai import Agent
from crewai import Task
from crewai import Crew
from crewai import LLM

from agents.crew.priority_agent import priority_agent
from agents.route_agent import get_safe_route
from agents.flood_check_agent import is_user_in_flood
from agents.bbox_agent import get_bbox_from_location
from agents.resource_discovery import (
    get_live_resources
) 
from agents.map_agents import create_map
from agents.drone_vision_module import analyze_latest_drone
from agents.resource_dispatch_module import (
    calculate_resources
)

from agents.flood_forecast_module import (
    predict_future_flood
)
from agents.resource_dispatch_module import (
    calculate_priority
)
from agents.resource_dispatch_module import (
    auto_dispatch
)
from agents.rescue_route_map import create_rescue_route


llm = LLM(
    model="ollama/llama3",
    base_url="http://localhost:11434"
)

climate_agent = Agent(

    role="Climate Analyst",

    goal="Determine flood alert level",

    backstory="Expert disaster meteorologist",

    llm=llm
)

prediction_agent = Agent(

    role="Flood Prediction Specialist",

    goal="Analyze flood severity",

    backstory="Expert flood forecaster",

    llm=llm
)

resource_agent = Agent(

    role="Resource Manager",

    goal="Allocate shelters and rescue teams",

    backstory="Emergency logistics expert",

    llm=llm
)

route_agent = Agent(

    role="Evacuation Planner",

    goal="Analyze evacuation route",

    backstory="Disaster transportation expert",

    llm=llm
)

coordination_agent = Agent(

    role="Disaster Commander",

    goal="Generate final emergency plan",

    backstory="National disaster response commander",

    llm=llm
)

def run_disaster_analysis(
    district,
    lat,
    lon,
    result,
    weather
): 
    
    if result["flood_area"] < 2:

        alert = "🟢 GREEN"

    elif result["flood_area"] < 5:

        alert = "🟡 YELLOW"

    elif result["flood_area"] < 10:

        alert = "🟠 ORANGE"

    else:

        alert = "🔴 RED"

    shelter = result.get(
    "nearest_shelter"
)

    if shelter is None:

        return "No shelter found nearby."

    resources = get_live_resources(
        lat,
        lon
)
    ambulances = resources["hospitals"] * 2

    workers = (
    resources["fire"] * 10
    +
    resources["police"] * 5
)

    food_packets = workers * 20

    water_packets = workers * 50

    bbox = get_bbox_from_location(
    lat,
    lon
)

    flood_mask_path = (
    f"flood_mask_vv_vh_{district.lower()}.png"
)

    print("USING NEW ROUTE CALL")
    G, route, start, end = get_safe_route(
        lat,
        lon,
        shelter["lat"],
        shelter["lon"],
        flood_mask_path,
        bbox
    )

    create_map(
        lat,
        lon,
        result["flood_area"],
        district,
        shelter,
        G,
        route,
        start,
        end
)

    TEAM_LAT = 8.8932
    TEAM_LON = 76.6141

    coords = [

        (

            G.nodes[node]["y"],

            G.nodes[node]["x"]

        )

        for node in route

    ]

    create_rescue_route(

        TEAM_LAT,

        TEAM_LON,

        lat,

        lon,

        coords

    )

    flood_mask = (
        f"flood_mask_vv_vh_{district.lower()}.png"
    )

#     vision = analyze_ground_image(
#         flood_mask
# )
    drone = analyze_latest_drone()

    if drone:

        vision = drone

    else:

        vision = {

            "flood_detected": False,

            "severity": "UNKNOWN",

            "road_blocked": False,

            "people_at_risk": False,

            "recommendation":
            "No drone image available",

            "people_count":0,

            "vehicle_count":0
        }

    bbox = get_bbox_from_location(
        lat,
        lon
    )

    flooded = is_user_in_flood(
        flood_mask,
        lat,
        lon,
        bbox
    )

    climate_task = Task(

description=f"""

District:
{district}

Flood Area:
{result['flood_area']} %

Hydro Coverage:
{result['hydro_coverage']} %

Rainfall:
{weather['rainfall_24h']} mm

Alert Level:
{alert}

This alert is already calculated.

DO NOT recalculate it.

Explain why this alert was assigned.

""",

expected_output="""
Return alert level and explanation.
""",

agent=climate_agent

)
    print("CREATING PREDICTION TASK...")
    prediction_task = Task(

        description=f"""

    Flood Prediction Results

    🌊 Flood Area:
    {result['flood_area']:.2f} %

    💧 Hydro Coverage:
    {result['hydro_coverage']:.2f} %

    🌧️ Rainfall Next 24h:
    {weather['rainfall_24h']} mm

    ☁️ Weather:
    {weather['weather']}

    🚨 Weather Alert:
    {weather['alert']}

    🚨 User Flooded:
    {flooded}

    👥 People Detected:
    {vision['people_count']}

    🚗 Vehicles:
    {vision['vehicle_count']}

    Generate:

    - Flood Percentage
    - Risk Level
    - Short Warning

""",

    expected_output="""
    Return:

    🌊 Flood Percentage

    🌧️ Rain Risk

    🚨 Risk Level

    ⚠️ Warning Message

    """,

    agent=prediction_agent
)
    print("PREDICTION TASK CREATED")

    people = max(
        vision.get("people_count", 0),
        int(result["flood_area"] * 100)
)
    boats_needed = max(
    1,
    people // 20
)
    ambulances = max(
    1,
    people // 100
)

    workers = max(
    5,
    people // 20
)

    food_packets = people * 3

    water_packets = people * 5

    forecast = predict_future_flood(

    result["flood_area"],

    weather["rainfall_24h"]
)
    
    sos_count = 0

    priority_score = calculate_priority(

    forecast["probability"],

    people,

    sos_count,

    result["flood_area"]

)

    resource_plan = calculate_resources(
    people
)   

    dispatch_status = auto_dispatch(

    district,

    priority_score,

    resource_plan

)
    
    resource_task = Task(

    description=f"""

    Shelter:
    {shelter['name']}

    Hospitals:
    {resources['hospitals']}

    Police Stations:
    {resources['police']}

    Fire Stations:
    {resources['fire']}

    Schools:
    {resources['schools']}

    Estimated People:
    {people}

    People:
    {people}

    Flood Forecast:
    {forecast['probability']} %

    Expected Severity:
    {forecast['severity']}

    Boats Needed:
    {resource_plan['boats']}

    Ambulances Needed:
    {resource_plan['ambulances']}

    Rescue Workers Needed:
    {resource_plan['rescue_workers']}

    Food Packets Needed:
    {resource_plan['food_packets']}

    Water Packets Needed:
    {resource_plan['water_packets']}

    Priority Score:
    {priority_score}

    Dispatch Status:
    {dispatch_status}

Create a complete resource deployment plan.

""",

expected_output="""
Resource allocation plan.
""",

agent=resource_agent
)
    
    route_task = Task(

    description=f"""

    Route Length:
    {len(route)}

    Shelter:
    {shelter['name']}

    User Flooded:
    {flooded}

    Analyze route safety.

    """,

    expected_output="""
    Safe evacuation recommendation.
    """,

    agent=route_agent
)
    
    priority_task = Task(

    description=f"""

    Nearest Shelter:
        {shelter['name']}

    Distance:
        {shelter['distance']}

    Hospitals:
    {resources['hospitals']}

    Determine priorities.

    """,

    expected_output="""
    Priority deployment plan.
    """,

    agent=priority_agent
)
    
    vision_task = Task(

    description=f"""

    Flood Detected:
    {vision['flood_detected']}

    Severity:
    {vision['severity']}

    Road Blocked:
    {vision['road_blocked']}

    People At Risk:
    {vision['people_at_risk']}

    Recommendation:
    {vision['recommendation']}

    Analyze satellite flood damage.

    """,

    expected_output="""
    Ground situation report.
    """,

    agent=prediction_agent
    )
    
    coordination_task = Task(

    description=f"""

    Combine all previous reports.

    Generate:

    - Use Alert Level: {alert}

    DO NOT recalculate alert.

    - Flood Severity
    - Shelter Recommendation
    - Evacuation Plan
    - Resource Allocation

    """,

    expected_output="""
    Full disaster response report.
    """,
    

    context=[

        climate_task,
        prediction_task,
        resource_task,
        route_task,
        priority_task,
        vision_task
    ],

    agent=coordination_agent
)
    
    crew = Crew(

    agents=[

        climate_agent,
        prediction_agent,
        resource_agent,
        route_agent,
        coordination_agent,
        priority_agent
    ],

    tasks=[

        climate_task,
        prediction_task,
        resource_task,
        route_task,
        priority_task,
        vision_task,
        coordination_task
    ]
)
    
    

    result = crew.kickoff()
    return str(result)