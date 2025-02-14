import sys
import json
import math
from typing import List, Tuple

DEGREES_PER_KM = 0.009  # Nairobi

def parse_location(location_str: str) -> List[float]:
    """Parses a location string into a list of floats.

    Args:
        location_str: A string formatted as a JSON array (e.g., "[lat, lon]" or "[lat, lon, alt]").

    Returns:
        List[float]: Parsed coordinates (latitude, longitude, and optional altitude).

    Raises:
        SystemExit: If the input is not a valid JSON array.

    Example:
        >>> parse_location("[1.2921, 36.8219]")
        [1.2921, 36.8219]
    """
    try:
        return json.loads(location_str)  # Handles "[lat, lon]" or "[lat, lon, alt]"
    except json.JSONDecodeError:
        print(f"Invalid location format: {location_str}")
        sys.exit(1)

def heading_to_vector(heading: float, speed_kmh: int) -> Tuple[float, float]:
    """Converts heading and speed into a velocity vector (delta_lat, delta_lon).

    Args:
        heading: Direction in degrees (0 = North, 90 = East, etc.).
        speed_kmh: Speed in kilometers per hour.

    Returns:
        Tuple[float, float]: Velocity vector (delta_lat, delta_lon) in degrees per second.
    """
    # Convert heading to radians
    heading_rad = math.radians(heading)

    # Calculate velocity components (km/h)
    delta_lat_km = speed_kmh * math.cos(heading_rad)  # North-South component
    delta_lon_km = speed_kmh * math.sin(heading_rad)  # East-West component

    # Convert km to degrees (Nairobi-specific: 0.009° ≈ 1 km)
    delta_lat = delta_lat_km * DEGREES_PER_KM / 3600  # Degrees per second
    delta_lon = delta_lon_km * DEGREES_PER_KM / 3600  # Degrees per second

    return (delta_lat, delta_lon)


def update_location_vector(
    location: List[float], velocity_vector: Tuple[float, float], total_distance_km: float, speed_kmh: int
) -> Tuple[List[float], float]:
    """Updates coordinates based on velocity vector and speed.

    Args:
        location: Current coordinates [lat, lon] or [lat, lon, altitude].
        velocity_vector: Movement vector (delta_lat, delta_lon) in degrees per second.
        total_distance_km: Cumulative distance traveled (km).
        speed_kmh: Speed in kilometers per hour.

    Returns:
        Tuple[List[float], float]: Updated coordinates and total distance.

    Example:
        >>> update_location_vector([-1.2921, 36.8219], (0.001, 0.001), 0, 60)
        ([-1.2901, 36.8229], 1.0)
    """
    delta_lat, delta_lon = velocity_vector
    lat, lon, *rest = location

    # Update coordinates
    new_lat = lat + delta_lat
    new_lon = lon + delta_lon

    # Update TOTAL distance traveled (km)
    km_per_ping = speed_kmh / 3600  # km per second
    updated_distance = total_distance_km + km_per_ping

    # Round to 6 decimal places
    new_location = [round(new_lat, 6), round(new_lon, 6), *rest]

    return (new_location, updated_distance)