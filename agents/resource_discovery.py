import osmnx as ox


def get_live_resources(lat, lon):

    try:

        hospitals = ox.features_from_point(

        (lat, lon),

        tags={
            "amenity":"hospital"
        },

        dist=10000
    )

    except:

        hospitals = []
    
    try:

        police = ox.features_from_point(

        (lat, lon),

        tags={
            "amenity": "police"
        },

        dist=10000
    )
        
    except:
        police=[]

    
    try:
        fire = ox.features_from_point(

        (lat, lon),

        tags={
            "amenity": "fire_station"
        },

        dist=10000
    )
        
    except:
        fire=[]

    
    try:
        schools = ox.features_from_point(

        (lat, lon),

        tags={
            "amenity": "school"
        },

        dist=10000
    )
    
    except:
        schools=[]

    return {

        "hospitals":
        len(hospitals),

        "police":
        len(police),

        "fire":
        len(fire),

        "schools":
        len(schools)
    }