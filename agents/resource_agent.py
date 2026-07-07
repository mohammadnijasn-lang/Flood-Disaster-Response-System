def allocate_resources(priority, people):

    if priority == "CRITICAL":

        return {

            "boats": max(4, people // 8),

            "ambulances": max(3, people // 20),

            "rescue_workers": max(40, people * 2),

            "food_packets": people * 4,

            "water_packets": people * 6

        }

    elif priority == "HIGH":

        return {

            "boats": max(2, people // 10),

            "ambulances": 2,

            "rescue_workers": max(20, people),

            "food_packets": people * 3,

            "water_packets": people * 4

        }

    else:

        return {

            "boats":1,

            "ambulances":1,

            "rescue_workers":10,

            "food_packets":100,

            "water_packets":200

        }