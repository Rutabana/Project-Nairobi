import sys
import json
import math
import boto3
from botocore.exceptions import ClientError
from typing import List, Tuple, Union
from tenacity import retry, stop_after_attempt, wait_exponential
DEGREES_PER_KM = 0.009  # Nairobi

def parse_3d(vector_str: str, name: str = "vector") -> Union[List[float], Tuple[float, float, float]]:
    """Parses a JSON array into a 3D vector (latitude, longitude, altitude).
    
    - Accepts 2D inputs (e.g., "[lat, lon]") and pads the third dimension with 0.
    - Enforces 3D for future compatibility.

    Args:
        vector_str: A JSON array string (e.g., "[1.2921, 36.8219]" or "[0.001, 0.001, 0.0001]").
        name: Contextual name for error messages (e.g., "location", "velocity").

    Returns:
        Union[List[float], Tuple[float, float, float]]: Parsed 3D vector.

    Raises:
        SystemExit: If the input is invalid or has the wrong dimensions.
    """
    try:
        parsed = json.loads(vector_str)
        if not isinstance(parsed, list):
            raise ValueError(f"{name} must be a JSON array.")
        
        # Pad with 0 if 2D, enforce 2-3 elements
        if len(parsed) == 2:
            parsed.append(0.0)  # Add altitude of 0 for backward compatibility
        elif len(parsed) != 3:
            raise ValueError(f"{name} must have 2 or 3 elements.")
        
        # Ensure all elements are numbers
        if not all(isinstance(x, (int, float)) for x in parsed):
            raise ValueError(f"{name} elements must be numbers.")
        
        return parsed if isinstance(parsed, list) else tuple(parsed)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Invalid {name} format: {vector_str}. Error: {e}")
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

    return (delta_lat, delta_lon, 0.0)


def update_location_vector(
    location: List[float], 
    velocity_vector: Tuple[float, float, float], 
    total_distance_km: float, 
    speed_kmh: int
) -> Tuple[List[float], float]:
    """Updates 3D coordinates based on velocity vector and speed.
    
    Args:
        location: Current 3D coordinates [lat, lon, alt].
        velocity_vector: 3D movement (delta_lat, delta_lon, delta_alt) in degrees/meters per second.
        total_distance_km: Cumulative distance traveled (km).
        speed_kmh: Speed in kilometers per hour.

    Returns:
        Tuple[List[float], float]: Updated 3D coordinates and total distance.
    """
    delta_lat, delta_lon, delta_alt = velocity_vector
    lat, lon, alt = location  # Now guaranteed to have 3 elements

    # Update coordinates
    new_lat = lat + delta_lat
    new_lon = lon + delta_lon
    new_alt = alt + delta_alt

    # Update TOTAL distance traveled (km)
    km_per_ping = speed_kmh / 3600  # km per second
    updated_distance = total_distance_km + km_per_ping

    # Round to 6 decimal places
    new_location = [round(new_lat, 6), round(new_lon, 6), round(new_alt, 6)]

    return (new_location, updated_distance)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def send_to_kinesis(data: bytes, key: str) -> None:
    client = boto3.client("kinesis", region_name="us-east-2")
    stream = "nairobi-stream"
    try:
        client.put_record(StreamName=stream, Data=data, PartitionKey=key)
    except ClientError as e:
        print(f"Final attempt failed: {e}")
        raise  # Re-raise after retries