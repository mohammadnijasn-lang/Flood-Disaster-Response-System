from flask import Flask, render_template
from flask import request,redirect
from flask import jsonify
from flask import send_file
import json
import os
from agents.district_agent import (
    get_district
)
from agents.sentinel_fetch import (
    predict_location
)
from agents.crew.disaster_crew import (
    run_disaster_analysis
)
from agents.weather_agent import get_weather_risk
from agents.sos_module import (
    create_sos,
    get_active_incidents
)
from agents.admin_module import (
    get_resources

)
from agents.drone_vision_module import (
    analyze_latest_drone
)
from agents.sos_module import get_active_incidents, get_sos_count
import folium
from agents.sms_module import send_sms
from agents.kerala_districts import KERALA_DISTRICTS
from agents.district_filter import (
    get_high_risk_districts
)
from agents.district_db import save_district_status

from agents.drone_manager import get_latest_drone_image
from flask import session
from agents.alert_module import send_alert
from agents.bbox_agent import get_bbox_from_location
from agents.route_agent import get_safe_route
from agents.rescue_route_agent import get_rescue_route
from agents.rescue_route_map import create_rescue_route
from agents.map_service import create_map
from agents.alert_module import create_alert
from agents.notification_module import send_alert
from agents.resource_dispatch_module import (
    dispatch_resources
)
from agents.sos_module import get_active_incidents
from agents.citizen_db import (
    create_location,
)
from agents.weather_agent import get_weather_risk
from agents.sentinel_fetch import predict_location
from agents.citizen_db import create_location
from agents.priority_agents import calculate_priority
from agents.resource_agent import allocate_resources
from agents.rescue_route_agent import get_rescue_route
from agents.crew import disaster_crew
from agents.vision_agents import analyze_ground_image
from agents.notification_module import notify_district
from agents.mission_db import get_missions
from agents.rescue_station_agent import find_nearest_rescue_station
from agents.sos_module import delete_incident
from agents.mission_db import (clear_missions,add_mission)
from agents.alert_agent import create_admin_alert
from agents.database import get_connection
from agents.drone_db import add_drone
from agents.dispatch_db import get_dispatch_history
from agents.district_db import get_district_status
from dotenv import load_dotenv

CURRENT_DISTRICT = None
CURRENT_LAT = None
CURRENT_LON = None

def get_flood_mask_path(
    district
):
    if district is None:
        return None

    district = district.lower().strip()

    district = district.replace(
    " district",
    ""
)

    district = district.replace(
    "district",
    ""
)

    district = district.strip()

    return f"flood_mask_vv_vh_{district}.png"

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY")
admins = {

    "collector": {
        "password": "collector123",
        "role": "Collector"
    },

    "sdma": {
        "password": "kerala2026",
        "role": "SDMA Admin"
    },

    "incident_commander": {
        "password": "rescue123",
        "role": "Incident Commander"
    }
}

DISPATCH_HISTORY = []

@app.route("/login")
def login():

    return render_template(
        "login.html"
    )

@app.route(
    "/admin_login",
    methods=["POST"]
)
def admin_login():

    username = request.form["username"]
    password = request.form["password"]

    if username in admins:

        if admins[username]["password"] == password:

            session["admin"] = True

            session["user"] = username

            session["role"] = admins[username]["role"]

            add_audit_log(

                f"{username} logged in"

            )

            return redirect("/admin")

    return "Invalid Login"

@app.route("/logout")
def logout():

    user = session.get("user")

    if user:
        add_audit_log(

        f"{user} logged out"

    )

        session.clear()

    return redirect("/")

# =====================
# HOME PAGE
# =====================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

@app.route("/flood_map")
def flood_map():

    return send_file(
        "templates/flood_map.html"
    )

# =====================
# LOCATION API
# =====================

@app.route("/location", methods=["POST"])
def location():

    global CURRENT_DISTRICT
    global CURRENT_LAT
    global CURRENT_LON

    data = request.json

    lat = data["lat"]
    lon = data["lon"]

    CURRENT_LAT = lat
    CURRENT_LON = lon

    district = get_district(lat, lon)
    CURRENT_DISTRICT = district

    weather = get_weather_risk(district)

    prediction = predict_location(district)

    shelter = prediction["nearest_shelter"]

    return jsonify({

        "district": district,

        "weather": weather["weather"],

        "weather_alert": weather["alert"],

        "rainfall": weather["rainfall_24h"],

        "risk": prediction["risk_level"],

        "severity": prediction["severity"],

        "flood_area": prediction["flood_area"],

        "shelter_name": shelter["name"],

        "shelter_distance": round(shelter["distance"], 2)

    })

@app.route("/sos", methods=["POST"])
def sos():

    data = request.json

    create_sos(

        data["name"],
        data["lat"],
        data["lon"],
        data["phone"]

    )

    district = get_district(

    data["lat"],

    data["lon"]

)

    weather = get_weather_risk(

    district

)

    prediction = predict_location(

    district
)

    nearest = prediction["nearest_shelter"]

    alert = weather["alert"]

    alert = weather["alert"]

    message = f"""

    Kerala SDMA

    SOS RECEIVED

    Current Alert

    {alert}

    Nearest Shelter

    {nearest["name"]}

    Distance

    {nearest["distance"]:.2f} km

    Rescue Team Dispatched

    YES

    Emergency

    1077

    """

    send_sms(

        data["phone"],

        message

    )

    # Later we'll call send_sms()

    return jsonify({

        "status":"SOS Stored",

        "alert":alert

    })

@app.route("/risk")
def risk():

    global CURRENT_DISTRICT

    if CURRENT_DISTRICT is None:

        return jsonify({

            "error":
            "Get location first"
        })


    return jsonify({
    })

@app.route("/user_dashboard")
def user_dashboard():

    global CURRENT_DISTRICT
    global CURRENT_LAT
    global CURRENT_LON

    if CURRENT_DISTRICT is None:

        return jsonify({

            "error":
            "Please click Get My Location first."

        })

    # Weather

    weather = get_weather_risk(

        CURRENT_DISTRICT

    )

    # Flood Prediction

    prediction = predict_location(

        CURRENT_DISTRICT

    )

    shelter = prediction["nearest_shelter"]

    bbox = get_bbox_from_location(

        CURRENT_LAT,

        CURRENT_LON

    )

    flood_mask = (

        f"flood_mask_vv_vh_{CURRENT_DISTRICT.lower()}.png"

    )

    G, route, start, end = get_safe_route(

        CURRENT_LAT,

        CURRENT_LON,

        shelter["lat"],

        shelter["lon"],

        prediction["mask_path"],

        prediction["bbox"]

    )

    create_map(

        CURRENT_LAT,

        CURRENT_LON,

        prediction["flood_area"],

        CURRENT_DISTRICT,

        shelter,

        G,

        route,

        start,

        end

    )

    return jsonify({

        "district": CURRENT_DISTRICT,

        "weather": weather,

        "flood_area":

            prediction["flood_area"],

        "hydro":

            prediction["hydro_coverage"],

        "alert":

            weather["alert"],

        "safe_route": True,

        "shelter":

            shelter,

        "map":

            "/flood_map"

    })

@app.route(
    "/upload_drone",
    methods=["POST"]
)
def upload_drone():

    if not session.get("admin"):
        return redirect("/login")

    file = request.files["image"]

    os.makedirs(
        "uploads/drone",
        exist_ok=True
    )

    save_path = os.path.join(
        "uploads",
        "drone",
        file.filename
    )

    file.save(save_path)

    # Save image path in MySQL
    add_drone(save_path)

    return jsonify({
        "status": "uploaded"
    })

@app.route("/admin_stats")
def admin_stats():

    if not session.get("admin"):
        return redirect("/login")

    incidents = get_active_incidents()

    return jsonify({

        "active_sos":
        len(incidents),

        "incidents":
        incidents
    })

@app.route("/admin")
def admin():

    if not session.get("admin"):

        return redirect("/login")

    return render_template(
        "admin.html"
    )

@app.route("/audit_log")
def audit_log():

    if not session.get("admin"):

        return redirect("/login")

    return jsonify(get_audit_logs())

@app.route("/dispatch_history")
def dispatch_history():

    if not session.get("admin"):
        return redirect("/login")

    return jsonify(get_dispatch_history())

@app.route(
    "/resources",
    methods=["GET","POST"]
)
def resources():
    if not session.get("admin"):

        return redirect("/login")

    if request.method == "POST":

        from agents.admin_module import (
            update_resources
        )

        update_resources({

            "ambulances":
            int(request.form["ambulances"]),

            "boats":
            int(request.form["boats"]),

            "rescue_workers":
            int(request.form["rescue_workers"]),

            "food_packets":
            int(request.form["food_packets"]),

            "water_packets":
            int(request.form["water_packets"])
            
        })

        add_audit_log(

        f"{session['user']} updated resources"

    )

        return "Resources Updated"

    return jsonify(
        get_resources()
    )

@app.route("/analyze_drone")
def analyze_drone():

    if not session.get("admin"):
        return redirect("/login")

    # -----------------------------
    # Vision Agent
    # -----------------------------

    vision = analyze_latest_drone()

    if vision is None:

        return jsonify({

            "status": "NO_DRONE_IMAGE"

        })
    
    # ---------------------------------
    # Vision AI Alert
    # ---------------------------------

    if vision["people_at_risk"]:

        print("🚨 PEOPLE IN DANGER")

        create_admin_alert({

            "type": "VISION",

            "message": f'{vision["people_count"]} people detected in danger.',

            "priority": "HIGH"

        })

    # -----------------------------
    # SAFE ?
    # -----------------------------

    safe = (

        not vision["people_at_risk"]

        and

        not vision["road_blocked"]

    )

    if safe:

        return jsonify({

            "status": "MONITOR",

            "safe": True,

            "vision": vision

        })

    # -----------------------------
    # Citizen DB
    # -----------------------------

    incidents = get_active_incidents()

    if len(incidents) == 0:

        return jsonify({

            "status": "NO_ACTIVE_INCIDENT"

        })

    incident = incidents[-1]

    district = get_district(

        incident["lat"],

        incident["lon"]

    )

    # -----------------------------
    # Rainfall
    # -----------------------------

    weather = get_weather_risk(
        district
    )

    # -----------------------------
    # Alert Agent
    # -----------------------------

    notification = create_alert(

        district,

        vision

    )

    # -----------------------------
    # Resource Agent
    # -----------------------------

    people = max(

        vision["people_count"],

        10

    )

    prediction = predict_location(

        district

    )

    priority_score, priority = calculate_priority(

        prediction["flood_area"],

        weather["rainfall_24h"],

        people,

        0,

        vision["vehicle_count"],

        get_sos_count(district)

    )

    resources = allocate_resources(

        priority,

        people

    )
    print(resources)

    lat = prediction["lat"]

    lon = prediction["lon"]

    station = find_nearest_rescue_station(

        lat,

        lon

    )

    dispatch = dispatch_resources(

        district,

        resources,

        station

    )

    resource_plan = {

        "priority": priority,

        "dispatch": dispatch,

        "resources": resources

    }

    mission = {

        "district": district,

        "priority": priority,

        "priority_score": priority_score,

        "station": station,

        "boats": resources["boats"],

        "ambulances": resources["ambulances"],

        "rescue_workers": resources["rescue_workers"],

        "food_packets": resources["food_packets"],

        "water_packets": resources["water_packets"],

        "dispatch": dispatch,

        "status": "DRONE ALERT"

    }

    add_mission(mission)

    # -----------------------------
    # Route Agent
    # -----------------------------

    shelter = prediction["nearest_shelter"]

    route_info = {

        "status": "READY",

        "station": station,

        "shelter": shelter,

        "citizen": incident,

        "priority": priority

    }

    # -----------------------------
    # Coordinator Agent
    # -----------------------------

    report = run_disaster_analysis(

        district=district,

        weather=weather,

        vision=vision,

        resource_plan=resource_plan,

        route_info=route_info,

        notification_status=notification

    )

    return jsonify({

        "status": "ALERT",

        "vision": vision,

        "resource": resources,

        "dispatch": dispatch,

        "report": report

    })

@app.route("/incident_map")
def incident_map():

    if not session.get("admin"):
        return redirect("/login")

    # -----------------------------------
    # Load Active Incidents
    # -----------------------------------

    incidents = get_active_incidents()

    if len(incidents) == 0:

        return "No Active Incidents"

    missions = get_missions()

    # -----------------------------------
    # Keep only valid missions
    # -----------------------------------

    missions = [

        m

        for m in missions

        if (
            "priority_score" in m
            and
            "district" in m
            and
            "priority" in m
        )

    ]

    highest = None

    if len(missions) > 0:

        try:

            highest = max(

                missions,

                key=lambda x: x["priority_score"]

            )

        except Exception as e:

            print("Mission Error:", e)

            highest = None

    # -----------------------------------
    # Create Map
    # -----------------------------------

    m = folium.Map(

        location=[

            incidents[0]["lat"],

            incidents[0]["lon"]

        ],

        zoom_start=10

    )

    # -----------------------------------
    # Add Every Citizen
    # -----------------------------------

    for incident in incidents:

        # -----------------------------
        # Default Marker Colour
        # -----------------------------

        if incident["status"] == "ACTIVE":

            color = "red"

        elif incident["status"] == "MONITORING":

            color = "orange"

        elif incident["status"] == "RESCUED":

            color = "green"

        else:

            color = "blue"

        icon = "user"

        priority_text = "NORMAL"

        # -----------------------------
        # Highest Priority Mission
        # -----------------------------

        if (

            highest is not None

            and

            incident["district"] == highest["district"]

        ):

            color = "purple"

            icon = "star"

            priority_text = highest["priority"]

        # -----------------------------
        # Popup
        # -----------------------------

        popup = f"""

        <h4>🚨 Active Incident</h4>

        <b>Name:</b> {incident['name']}<br>

        <b>Phone:</b> {incident['phone']}<br>

        <b>District:</b> {incident['district']}<br>

        <b>Status:</b> {incident['status']}<br>

        <b>Priority:</b> {priority_text}

        """

        # -----------------------------
        # Marker
        # -----------------------------

        folium.Marker(

            [

                incident["lat"],

                incident["lon"]

            ],

            popup=folium.Popup(

                popup,

                max_width=300

            ),

            tooltip=incident["name"],

            icon=folium.Icon(

                color=color,

                icon=icon,

                prefix="fa"

            )

        ).add_to(m)

    # -----------------------------------
    # Save
    # -----------------------------------

    m.save("incident_map.html")

    return send_file("incident_map.html")

@app.route("/forecast")
def forecast():

    if not session.get("admin"):
        return redirect("/login")

    results = []

    for district in KERALA_DISTRICTS:

        try:

            weather = get_weather_risk(
                district
            )

            rainfall = weather["rainfall_24h"]

            probability = min(
                100,
                rainfall * 4
            )

            if probability > 80:
                severity = "CRITICAL"

            elif probability > 60:
                severity = "HIGH"

            elif probability > 30:
                severity = "MEDIUM"

            else:
                severity = "LOW"

            results.append({

                "district": district,

                "rainfall": rainfall,

                "probability": probability,

                "severity": severity
            })

        except Exception as e:

            print(e)

    return jsonify(results)

@app.route("/district_status")
def district_status():

    if not session.get("admin"):

        return redirect("/login")

    try:

        return jsonify(

            get_district_status()

        )

    except Exception as e:

        print("District DB Error:", e)

        return jsonify([])

@app.route("/control_room")
def control_room():

    if not session.get("admin"):
        return redirect("/login")

    if session.get("role") not in [
        "Collector",
        "SDMA Admin"
    ]:
        return "Access Denied", 403

    return render_template("control_room.html")

@app.route("/live_resources")
def live_resources():

    if not session.get("admin"):

        return redirect("/login")

    return jsonify(
        get_resources()
    )
@app.route("/admin_profile")
def admin_profile():

    if not session.get("admin"):
        return redirect("/login")

    return jsonify({

        "user":
        session["user"],

        "role":
        session["role"]

    })

@app.route("/rescue_route")
def rescue_route():

    if not session.get("admin"):
        return redirect("/login")

    # ---------------------------------
    # Load Missions
    # ---------------------------------

    missions = get_missions()

    missions = [

        m

        for m in missions

        if (
            "station" in m
            and
            "district" in m
        )

    ]

    if len(missions) == 0:
        return "No Valid Missions"

    # ---------------------------------
    # USE THE LATEST MISSION
    # ---------------------------------

    mission = missions[-1]

    print("\n========== SELECTED MISSION ==========")
    print(mission)
    print("======================================")

    # ---------------------------------
    # Load Active Incidents
    # ---------------------------------

    incidents = [

        i

        for i in get_active_incidents()

        if (
            i.get("district") == mission.get("district")
            and
            i.get("status") == "ACTIVE"
        )

    ]

    print("\n========== ACTIVE INCIDENTS ==========")

    for i in incidents:
        print(i)

    print("======================================")

    if len(incidents) == 0:
        return "Citizen not found"

    # ---------------------------------
    # USE THE LATEST INCIDENT
    # ---------------------------------

    incident = incidents[-1]

    station = mission.get("station")

    if not isinstance(station, dict):
        return "Invalid Station Data"

    if "lat" not in station or "lon" not in station:
        return "Invalid Station Coordinates"

    print("\n========== ROUTE ==========")
    print("Station :", station)
    print("Incident:", incident)
    print("===========================\n")

    # ---------------------------------
    # Generate Route
    # ---------------------------------

    try:

        G, route, start, end = get_rescue_route(

            station["lat"],
            station["lon"],

            incident["lat"],
            incident["lon"]

        )

    except Exception as e:

        print("Route Error:", e)

        return "Unable to generate rescue route."

    # ---------------------------------
    # Create Rescue Map
    # ---------------------------------

    try:

        create_rescue_route(

            station["lat"],
            station["lon"],

            incident["lat"],
            incident["lon"],

            G,
            route

        )

    except Exception as e:

        print("Map Error:", e)

        return "Unable to create rescue map."

    return send_file("templates/rescue_route.html")

@app.route("/send_alert/<district>")
def send_alert_to_district(district):

    weather = get_weather_risk(district)

    send_alert(

        district,

        weather["alert"]

    )

    return jsonify({

        "status":"SMS Send"

    })

@app.route("/update_forecast")
def update_forecast():

    if not session.get("admin"):
        return redirect("/login")

    risky = get_high_risk_districts()

    # Save latest forecast to MySQL
    save_district_status(risky)

    return jsonify({

        "status": "Forecast Updated"

    })

@app.route("/share_location", methods=["POST"])
def share_location():

    data = request.json

    name = data["name"]
    phone = data["phone"]
    lat = data["lat"]
    lon = data["lon"]

    district = get_district(lat, lon)

    create_location(

        name,
        phone,
        lat,
        lon,
        district
    )

    create_sos(

        name,
        lat,
        lon,
        phone,
        district
    )

    return jsonify({

        "status":"SUCCESS",

        "message":"Location shared successfully.",

        "district":district

    })

@app.route("/run_disaster_pipeline")
def run_disaster_pipeline():

    if not session.get("admin"):
        return redirect("/login")

    # ---------------------------------------
    # Read Latest District Forecast Cache
    # ---------------------------------------

    try:

        districts = get_district_status()

    except Exception as e:

        return jsonify({

            "status": "ERROR",

            "message": "Unable to load district status from database",

            "error": str(e)

        })
    
    clear_missions()

    reports = []

    # ---------------------------------------
    # Loop through High Risk Districts
    # ---------------------------------------

    for prediction in districts:

        if prediction["alert"] not in [

            "🔴 RED",

            "🟠 ORANGE"

        ]:

            continue

        print(f"\nRunning pipeline for {prediction['district']}")

        # ---------------------------------------
        # Estimated People
        # ---------------------------------------

        if prediction["flood_area"] >= 20:

            estimated_people = 150

        elif prediction["flood_area"] >= 10:

            estimated_people = 80

        elif prediction["flood_area"] >= 5:

            estimated_people = 40

        else:

            estimated_people = 10

        # ---------------------------------------
        # Vision Agent
        # ---------------------------------------

        latest_drone = get_latest_drone_image()

        if latest_drone:

            print("\nDrone image found")

            vision = analyze_ground_image(latest_drone)

        else:

            print("\nNo Drone Image")

            vision = {

                "people_count": estimated_people,

                "vehicle_count":0,

                "house_count":0,

                "people_at_risk":False,

                "road_blocked":False,

                "severity":"Unknown",

                "recommendation":"No Drone Image"

            }

        # ---------------------------------------
        # Priority
        # ---------------------------------------

        priority_score, priority = calculate_priority(

            prediction["flood_area"],

            prediction["rainfall"],

            vision["people_count"],

            vision["house_count"],

            vision["vehicle_count"],

            get_sos_count(

                prediction["district"]

            )

        )

        # ---------------------------------------
        # Resources
        # ---------------------------------------

        resources = allocate_resources(

            priority,

            vision["people_count"]

        )

        # ---------------------------------------
        # Get Prediction Details
        # ---------------------------------------

        prediction_details = predict_location(

            prediction["district"]

        )

        lat = prediction_details["lat"]

        lon = prediction_details["lon"]

        shelter = prediction_details["nearest_shelter"]

        # ---------------------------------------
        # Rescue Base
        # ---------------------------------------

        station = find_nearest_rescue_station(

            lat,

            lon

        )

        # ---------------------------------------
        # Dispatch
        # ---------------------------------------

        dispatch = dispatch_resources(

            prediction["district"],

            resources,

            station

        )

        # ---------------------------------------
        # ETA
        # ---------------------------------------

        if station:

            eta = f"{round(station['distance']*2)} minutes"

        else:

            eta = "Unknown"

        # ---------------------------------------
        # CrewAI
        # ---------------------------------------

        crew_input = {

            "district":prediction["district"],

            "prediction":prediction,

            "vision":vision,

            "priority":priority,

            "priority_score":priority_score,

            "resources":resources,

            "station":station,

            "eta":eta

        }

        report = disaster_crew.kickoff(

            inputs=crew_input

        )

        report = str(report)

        # ---------------------------------------
        # Notify Citizens
        # ---------------------------------------

        notify_district(

            prediction["district"],

            report

        )

        # ---------------------------------------
        # Save Mission
        # ---------------------------------------

        mission = {

            "district": prediction["district"],

            "alert": prediction["alert"],

            "rainfall": prediction["rainfall"],

            "flood_area": prediction["flood_area"],

            "priority": priority,

            "priority_score": priority_score,

            "station": station,

            "eta": eta,

            "status": "ACTIVE",

            "boats": resources["boats"],

            "ambulances": resources["ambulances"],

            "rescue_workers": resources["rescue_workers"],

            "shelter": shelter["name"],

            "report": report

    }

        add_mission(mission)

        reports.append(mission)

    if len(reports)==0:

        return jsonify({

            "status":"SAFE",

            "districts":[]

        })

    return jsonify({

        "status":"SUCCESS",

        "districts":reports

    })

@app.route("/safe_route")
def safe_route():

    return send_file(

        "templates/safe_route.html"

    )

@app.route("/missions")
def missions():

    if not session.get("admin"):

        return redirect("/login")

    try:

        missions = get_missions()

        return jsonify(missions)

    except Exception as e:

        print("Mission Error:", e)

        return jsonify([])

@app.route("/delete_sos/<int:id>", methods=["POST"])
def delete_sos(id):

    delete_incident(id)

    return redirect("/admin")

@app.route("/admin_alerts")
def admin_alerts():

    if not os.path.exists("admin_alerts.json"):

        return jsonify([])

    with open("admin_alerts.json","r") as f:

        return jsonify(json.load(f))
    
def add_audit_log(event):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO audit_logs(event)

        VALUES(%s)

    """, (event,))

    conn.commit()

    cursor.close()

    conn.close()


def get_audit_logs():

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute("""

        SELECT *

        FROM audit_logs

        ORDER BY id DESC

    """)

    logs = cursor.fetchall()

    cursor.close()

    conn.close()

    return logs

if __name__ == "__main__":

    print("Starting Flask Server...")

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )