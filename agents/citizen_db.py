import json

FILE = "agents/citizens.json"


def get_citizens():

    with open(FILE, "r") as f:

        return json.load(f)


def get_citizens_by_district(district):

    citizens = get_citizens()

    return [

        c

        for c in citizens

        if c["district"].lower() == district.lower()

    ]