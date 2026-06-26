from flask import Flask, render_template
from flask import request,redirect
from flask import jsonify
from flask import send_file

import os
from agents.district_agent import (
    get_district
)

from agents.sentinel_agent import (
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
    add_drone_image,
    get_resources
)
from agents.drone_vision_module import (
    analyze_latest_drone
)
from agents.sos_module import get_active_incidents
import folium
from agents.sms_module import send_sms
from agents.kerala_districts import KERALA_DISTRICTS
from agents.district_filter import (
    get_high_risk_districts
)
from agents.cache_module import (
    save_cache,
    load_cache
)
from flask import session
from agents.alert_module import send_alert_to_district
from agents.bbox_agent import get_bbox_from_location
from agents.route_agent import get_safe_route
from agents.rescue_route_map import create_rescue_route

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
app.secret_key = "kerala_disaster_secret"
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

AUDIT_LOG = []

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

            AUDIT_LOG.append({

                "event":
                f"{username} logged in"
            })

            return redirect("/admin")

    return "Invalid Login"

@app.route("/logout")
def logout():

    user = session.get("user")

    if user:
        AUDIT_LOG.append({
        "event": f"{user} logged out"
    })

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
        "agents/flood_map.html"
    )

# =====================
# LOCATION API
# =====================

@app.route(
    "/location",
    methods=["POST"]
)
def location():

    data = request.json

    lat = data["lat"]
    lon = data["lon"]

    district = get_district(
        lat,
        lon
    )

    global CURRENT_DISTRICT
    global CURRENT_LAT
    global CURRENT_LON

    CURRENT_DISTRICT = district
    CURRENT_LAT = lat
    CURRENT_LON = lon

    return jsonify({

        "status":"success",

        "district":district,

        "lat":lat,

        "lon":lon
    })

@app.route("/sos", methods=["POST"])
def sos():

    data = request.json

    create_sos(

        data["name"],
        data["lat"],
        data["lon"]

    )

    weather = get_weather_risk(
        data["district"]
    )

    prediction = predict_location(

    data["district"]

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

@app.route("/crew")
def crew():

    if CURRENT_DISTRICT is None:

        return jsonify({
            "report":"Please click Get My Location first."
        })  


    weather = get_weather_risk(
    CURRENT_DISTRICT
)
    prediction = predict_location(
    CURRENT_DISTRICT
)

    # CrewAI Report
    crew_report = run_disaster_analysis(

        CURRENT_DISTRICT,
        CURRENT_LAT,
        CURRENT_LON,
        prediction,
        weather

    )

    print("CREW FINISHED")


    return jsonify({

    "report": crew_report,

    "risk": weather["alert"],

    "weather_alert": weather["alert"],

    "rainfall": weather["rainfall_24h"],

    "flood_area": prediction["flood_area"],

    "shelter_name":
        prediction["nearest_shelter"]["name"],

    "shelter_distance":
        prediction["nearest_shelter"]["distance"],

    "map": "/flood_map"

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

    add_drone_image(
        save_path
    )

    return jsonify({

        "status":"uploaded"
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

    return jsonify(AUDIT_LOG)

@app.route("/dispatch_history")
def dispatch_history():

    if not session.get("admin"):

        return redirect("/login")

    return jsonify(DISPATCH_HISTORY)

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

        AUDIT_LOG.append({

        "event":
        f"{session['user']} updated resources"
    })

        return "Resources Updated"

    return jsonify(
        get_resources()
    )

@app.route("/analyze_drone")
def analyze_drone():

    if not session.get("admin"):
        return redirect("/login")

    result = analyze_latest_drone()

    if result is None:

        return jsonify({

            "status":"No drone image uploaded"
        })

    return jsonify(result)

@app.route("/incident_map")
def incident_map():
    if not session.get("admin"):

        return redirect("/login")

    incidents = get_active_incidents()

    if len(incidents) == 0:

        return "No incidents"

    m = folium.Map(

        location=[
            incidents[0]["lat"],
            incidents[0]["lon"]
        ],

        zoom_start=11
    )

    for i, incident in enumerate(incidents):

        folium.Marker(

            [
                incident["lat"],
                incident["lon"]
            ],

            popup=f"""
            <b>{incident['name']}</b><br>
            Latitude : {incident['lat']}<br>
            Longitude : {incident['lon']}<br>
            Time : {incident['time']}
            """,

            tooltip=incident["name"]

        ).add_to(m)

    m.save(
        "incident_map.html"
    )

    return send_file(
        "incident_map.html"
    )

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

    cache = load_cache()

    if cache:
        return jsonify(cache)

    risky = get_high_risk_districts()

    results = []

    for d in risky:

        try:
            results.append({

            "district":d["district"],

            "rainfall":d["rainfall"],

            "flood_area":d["flood_area"],

            "alert":d["alert"]

        })

        except Exception as e:

            print(e)

    save_cache(results)

    return jsonify(results)

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

    incidents = get_active_incidents()

    if len(incidents) == 0:
        return "No SOS found"

    incident = incidents[-1]

    user_lat = incident["lat"]
    user_lon = incident["lon"]

    # Rescue team location
    team_lat = 8.8932
    team_lon = 76.6141

    bbox = get_bbox_from_location(
        user_lat,
        user_lon
    )

    G, route, start, end = get_safe_route(

        team_lat,
        team_lon,

        user_lat,
        user_lon,

        "flood_mask_vv_vh_kollam.png",

        bbox

    )

    create_rescue_route(

        team_lat,
        team_lon,

        user_lat,
        user_lon,

        G,

        route

    )

    return send_file("templates/rescue_route.html")

@app.route("/send_alert/<district>")
def send_alert(district):

    weather = get_weather_risk(district)

    send_alert_to_district(

        district,

        weather["alert"]

    )

    return jsonify({

        "status":"SMS Send"

    })

if __name__ == "__main__":

    print("Starting Flask Server...")

    app.run(
        debug=True
    )