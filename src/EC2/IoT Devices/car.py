import time
import json
import boto3
import sys
import random
from botocore.exceptions import ClientError
from typing import List, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential

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


def update_location(
    location: List[float], direction: str, total_distance_km: float, speed_kmh: int
) -> Tuple[List[float], float]:
    """Updates coordinates based on movement direction and speed.

    Args:
        location: Current coordinates [lat, lon] or [lat, lon, altitude].
        direction: Movement direction ("North", "South", etc.).
        total_distance_km: Cumulative distance traveled (km).
        speed_kmh: Speed in kilometers per hour.

    Returns:
        Tuple[List[float], float]: Updated coordinates and total distance.

    Example:
        >>> update_location([-1.2921, 36.8219], "North", 0, 60)
        ([-1.2831, 36.8219], 1.0)
    """
    # Distance covered in 1 minute (km)
    km_per_ping = speed_kmh / 60  # e.g., 60 km/h → 1 km/min

    # Degrees to adjust (Nairobi-specific: 0.009° ≈ 1 km)
    increment_deg = DEGREES_PER_KM * km_per_ping  # 1 km → 0.009°
    lat, lon, *rest = location

    if direction == "North":
        new_lat = lat + increment_deg
        new_lon = lon
    elif direction == "South":
        new_lat = lat - increment_deg
        new_lon = lon
    elif direction == "East":
        new_lat = lat
        new_lon = lon + increment_deg
    elif direction == "West":
        new_lat = lat
        new_lon = lon - increment_deg
    else:
        return (location, total_distance_km)

    # Update TOTAL distance traveled (km)
    updated_distance = total_distance_km + km_per_ping  # ✅ Correct unit (km)
    new_location = [
        round(new_lat, 6),
        round(new_lon, 6),
        *rest,
    ]  # Precision to 6 decimals

    return (new_location, updated_distance)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def send_to_kinesis(client: boto3.client, data: bytes, stream: str, key: str) -> None:
    try:
        client.put_record(StreamName=stream, Data=data, PartitionKey=key)
    except ClientError as e:
        print(f"Final attempt failed: {e}")
        raise  # Re-raise after retries


def simulate(device_id: str, location: List[float], test: bool) -> None:
    kinesis_client = boto3.client("kinesis", region_name="us-east-2")
    stream_name = "nairobi-stream"
    speed_kmh = random.randint(30, 90)  # km/h
    direction = random.choice(["North", "East", "South", "West", "none"])
    total_distance_km = 0
    gas = 100.0

    while True:
        # Consider turning
        if random.randint(1, 5) == 1:
            direction = random.choice(["North", "East", "South", "West", "none"])

        # Consider getting gas
        if gas <= 30 and random.randint(1, 10) == 1:
            gas = 100.0

        # Fix: float operations may result in incorrect approximates. This also handles edge cases
        gas = min(100.0, max(round(gas - 0.2, 1), 0.0))
        location, total_distance_km = update_location(
            location, direction, total_distance_km, speed_kmh
        )

        # Construct the JSON payload
        payload = {
            "deviceId": device_id,
            "timestamp": int(time.time()),
            "status": "ping",
            "location": location,
            "gas": gas,
        }

        # Convert to bytes
        data_bytes = json.dumps(payload).encode("utf-8")

        if test:
            print(payload)
        else:
            send_to_kinesis(
                client=kinesis_client,
                data=data_bytes,
                stream=stream_name,
                key=device_id,
            )

        time.sleep(60)


if __name__ == "__main__":
    size = len(sys.argv)
    required_args = 2  # device_id and location
    if len(sys.argv) not in [
        required_args + 1,
        required_args + 2,
    ]:  # +1 for script name
        print(f"Usage: {sys.argv[0]} <id> <location> [TEST]")
        sys.exit(1)
    else:
        id = sys.argv[1]
        location = parse_location(sys.argv[2])
        device_id = f"car-{id}"
        test = size == 4 and sys.argv[3] == "TEST"

        simulate(device_id, location, test)
