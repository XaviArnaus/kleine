from datetime import datetime, time

class Calculations:

    @staticmethod
    def knots_to_kmh(knots: float) -> float:
        return knots * 1.852

    @staticmethod
    def kmh_to_knots(kmh: float) -> float:
        return kmh / 1.852

    @staticmethod
    def calculate_speed_between_points(previous_point: dict, current_point: dict, previous_time: time, current_time: time) -> float:
        """
        Calculate speed between two GPS points given the time difference in seconds.
        Haversine formula is used to calculate the distance between two latitude/longitude points.
        """
        from math import radians, sin, cos, sqrt, atan2

        R = 6371.0  # Radius of the Earth in kilometers

        lat1 = radians(previous_point["latitude"])
        lon1 = radians(previous_point["longitude"])
        lat2 = radians(current_point["latitude"])
        lon2 = radians(current_point["longitude"])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance_km = R * c
        distance_nm = distance_km * 0.539957  # Convert km to nautical miles

        time_diff_secs = (datetime.fromisoformat(current_time.isoformat()) - datetime.fromisoformat(previous_time)).total_seconds()

        if time_diff_secs > 0:
            speed_knots = distance_nm / (time_diff_secs / 3600)  # Convert seconds to hours
        else:
            speed_knots = 0.0

        return Calculations.knots_to_kmh(speed_knots)
