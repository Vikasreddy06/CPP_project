"""
LocationTracker -- campus zone management and proximity calculation.

Defines campus zones with coordinates, maps buildings to zones, and
provides proximity-based search for narrowing lost/found item locations.

Author: Vikas Reddy Amanagantti (x25178849)
"""

import math


class LocationTracker:
    """
    Manages campus zones, building mappings, and distance calculations
    to support location-aware item matching.
    """

    # Pre-defined campus zones with approximate centre coordinates (lat, lon)
    DEFAULT_ZONES = {
        "main_campus": {"name": "Main Campus", "lat": 53.3498, "lon": -6.2603, "radius_m": 500},
        "library": {"name": "Library Complex", "lat": 53.3502, "lon": -6.2598, "radius_m": 100},
        "science_block": {"name": "Science Block", "lat": 53.3495, "lon": -6.2610, "radius_m": 80},
        "sports_centre": {"name": "Sports Centre", "lat": 53.3488, "lon": -6.2580, "radius_m": 120},
        "student_union": {"name": "Student Union", "lat": 53.3501, "lon": -6.2615, "radius_m": 60},
        "cafeteria": {"name": "Cafeteria", "lat": 53.3499, "lon": -6.2590, "radius_m": 50},
        "parking": {"name": "Parking Area", "lat": 53.3485, "lon": -6.2625, "radius_m": 150},
        "admin_building": {"name": "Admin Building", "lat": 53.3505, "lon": -6.2608, "radius_m": 70},
    }

    # Building-to-zone mapping
    DEFAULT_BUILDING_MAP = {
        "Library Building A": "library",
        "Library Building B": "library",
        "Science Lab 1": "science_block",
        "Science Lab 2": "science_block",
        "Lecture Hall 1": "main_campus",
        "Lecture Hall 2": "main_campus",
        "Computer Lab": "main_campus",
        "Gym": "sports_centre",
        "Swimming Pool": "sports_centre",
        "SU Building": "student_union",
        "Main Canteen": "cafeteria",
        "Coffee Shop": "cafeteria",
        "Car Park A": "parking",
        "Car Park B": "parking",
        "Reception": "admin_building",
        "Exam Hall": "main_campus",
    }

    def __init__(self, zones=None, building_map=None):
        """
        Initialise the tracker with optional custom zones and building map.

        Args:
            zones: dict of zone_id -> zone info dicts.
            building_map: dict of building_name -> zone_id.
        """
        self.zones = zones or self.DEFAULT_ZONES.copy()
        self.building_map = building_map or self.DEFAULT_BUILDING_MAP.copy()

    # ------------------------------------------------------------------
    # Zone management
    # ------------------------------------------------------------------

    def add_zone(self, zone_id, name, lat, lon, radius_m=100):
        """Register a new campus zone."""
        self.zones[zone_id] = {
            "name": name,
            "lat": lat,
            "lon": lon,
            "radius_m": radius_m,
        }

    def get_zone(self, zone_id):
        """Return zone info or None."""
        return self.zones.get(zone_id)

    def list_zones(self):
        """Return a list of all zone IDs and names."""
        return [{"id": zid, "name": z["name"]} for zid, z in self.zones.items()]

    def add_building(self, building_name, zone_id):
        """Map a building name to a zone."""
        self.building_map[building_name] = zone_id

    def get_zone_for_building(self, building_name):
        """
        Look up which zone a building belongs to.

        Args:
            building_name: The name of the building.

        Returns:
            The zone_id string, or None if unmapped.
        """
        return self.building_map.get(building_name)

    def get_buildings_in_zone(self, zone_id):
        """Return all building names mapped to the given zone."""
        return [b for b, z in self.building_map.items() if z == zone_id]

    # ------------------------------------------------------------------
    # Distance and proximity
    # ------------------------------------------------------------------

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance in metres between two
        latitude/longitude points using the Haversine formula.

        Args:
            lat1, lon1: Coordinates of point A.
            lat2, lon2: Coordinates of point B.

        Returns:
            Distance in metres as a float.
        """
        R = 6371000  # Earth radius in metres
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = (math.sin(d_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def distance_between_zones(self, zone_a_id, zone_b_id):
        """
        Compute the distance in metres between the centres of two zones.

        Args:
            zone_a_id: First zone identifier.
            zone_b_id: Second zone identifier.

        Returns:
            Distance in metres, or None if either zone is unknown.
        """
        za = self.zones.get(zone_a_id)
        zb = self.zones.get(zone_b_id)
        if za is None or zb is None:
            return None
        return self.haversine_distance(za["lat"], za["lon"], zb["lat"], zb["lon"])

    def distance_between_buildings(self, building_a, building_b):
        """
        Compute approximate distance between two buildings via their zones.

        Returns:
            Distance in metres, or None if buildings are unmapped.
        """
        za_id = self.get_zone_for_building(building_a)
        zb_id = self.get_zone_for_building(building_b)
        if za_id is None or zb_id is None:
            return None
        return self.distance_between_zones(za_id, zb_id)

    def are_nearby(self, location_a, location_b, threshold_m=200):
        """
        Determine whether two locations (building names or zone IDs) are
        within *threshold_m* metres of each other.

        Args:
            location_a: A building name or zone ID.
            location_b: A building name or zone ID.
            threshold_m: Maximum distance to be considered nearby.

        Returns:
            True if the locations are within the threshold.
        """
        # Try building lookup first, fall back to zone IDs
        dist = self.distance_between_buildings(location_a, location_b)
        if dist is None:
            dist = self.distance_between_zones(location_a, location_b)
        if dist is None:
            return False
        return dist <= threshold_m

    # ------------------------------------------------------------------
    # Zone-based search
    # ------------------------------------------------------------------

    def find_items_in_zone(self, items, zone_id):
        """
        Filter a list of item dicts to those whose 'location' maps to
        the given zone.

        Args:
            items: List of item dicts (each must have a 'location' key).
            zone_id: The zone to filter by.

        Returns:
            A filtered list of items.
        """
        buildings = set(self.get_buildings_in_zone(zone_id))
        return [item for item in items if item.get("location") in buildings]

    def find_nearby_items(self, items, reference_location, threshold_m=200):
        """
        Filter items to those whose location is near the reference location.

        Args:
            items: List of item dicts.
            reference_location: Building name or zone ID to measure from.
            threshold_m: Maximum distance in metres.

        Returns:
            A list of (item, distance_m) tuples sorted by distance.
        """
        results = []
        for item in items:
            loc = item.get("location", "")
            dist = self.distance_between_buildings(reference_location, loc)
            if dist is None:
                continue
            if dist <= threshold_m:
                results.append((item, round(dist, 1)))
        results.sort(key=lambda x: x[1])
        return results
