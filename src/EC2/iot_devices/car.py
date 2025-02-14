import time
import json
import sys
import random
import logging
from typing import List
from src.util.sim_functions import *

# Constants
DEGREES_PER_KM = 0.009  # Nairobi
GAS_DECREMENT = 0.2  # Gas consumption per minute
GAS_REFILL_THRESHOLD = 30.0  # Refill gas when below this value
GAS_REFILL_AMOUNT = 100.0  # Gas refill amount

# Configure logging
logging.basicConfig(level=logging.INFO)

def simulate(device_id: str, location: List[float], initial_heading: float, test: bool) -> None:
    """Simulates a car's movement and sends data to Kinesis or logs it.

    Args:
        device_id: Unique ID for the car (e.g., "car-123").
        location: Initial 3D coordinates [lat, lon, alt].
        initial_heading: Initial direction in degrees (0 = North, 90 = East, etc.).
        test: If True, log payloads instead of sending to Kinesis.
    """
    speed_kmh = random.randint(30, 90)  # Random speed between 30-90 km/h
    total_distance_km = 0.0
    gas = GAS_REFILL_AMOUNT

    while True:
        # Consider changing direction
        if random.randint(1, 5) == 1:
            initial_heading = random.choice([0, 90, 180, 270])  # Random new heading

        # Consider refilling gas
        if gas <= GAS_REFILL_THRESHOLD and random.randint(1, 10) == 1:
            gas = GAS_REFILL_AMOUNT

        # Update gas level (ensure it stays within bounds)
        gas = min(GAS_REFILL_AMOUNT, max(round(gas - GAS_DECREMENT, 1), 0.0))

        # Calculate velocity vector and update location
        velocity_vector = heading_to_vector(initial_heading, speed_kmh)
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
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
            logging.info("Simulation payload: %s", payload)
        else:
            send_to_kinesis(data=data_bytes, key=device_id)

        # Wait for 1 minute before the next iteration
        time.sleep(60)

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) not in [4, 5]:  # 4 required args + 1 optional TEST flag
        print(f"Usage: {sys.argv[0]} <id> <location> <direction> [TEST]")
        sys.exit(1)

    id = sys.argv[1]
    location_str = sys.argv[2]
    direction = float(sys.argv[3])  # Convert direction to float
    test = len(sys.argv) == 5 and sys.argv[4] == "TEST"

    # Parse location and initialize simulation
    location = parse_3d(location_str)
    device_id = f"car-{id}"
    simulate(device_id, location, direction, test)