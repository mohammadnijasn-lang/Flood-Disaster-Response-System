import osmnx as ox
import networkx as nx


def get_rescue_route(

    team_lat,
    team_lon,

    incident_lat,
    incident_lon

):

    G = ox.graph_from_point(

        (incident_lat, incident_lon),

        dist=20000,

        network_type="drive"

    )

    start = ox.distance.nearest_nodes(

        G,

        team_lon,

        team_lat

    )

    end = ox.distance.nearest_nodes(

        G,

        incident_lon,
        
        incident_lat

    )

    route = nx.shortest_path(

        G,

        start,

        end,

        weight="length"

    )

    return (

        G,

        route,

        start,

        end

    )