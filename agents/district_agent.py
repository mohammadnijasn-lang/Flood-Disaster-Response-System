from geopy.geocoders import Nominatim


def get_district(
    lat,
    lon
):

    try:

        geolocator = Nominatim(
            user_agent="flood_system"
        )

        location = geolocator.reverse(

            (
                lat,
                lon
            ),

            exactly_one=True
        )

        address = location.raw.get(
            "address",
            {}
        )

        district = (

            address.get("state_district")

            or

            address.get("county")

            or

            address.get("district")

        )

        if district:

            district = district.replace(
                " District",
                ""
            )

            district = district.replace(
                " district",
                ""
            )

        return district

    except Exception as e:

        print(
            "\nDistrict Error:",
            e
        )

        return None