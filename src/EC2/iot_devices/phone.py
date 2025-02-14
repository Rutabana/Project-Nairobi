import time
import json
import sys
import random
import logging
from typing import List
from src.util.sim_functions import *

# Constants
DEGREES_PER_KM = 0.009  # Nairobi
WALKING_SPEED_KMH = 5.0
BATTERY_DECREMENT = 0.3  # Battery drain per minute
LOW_BATTERY_THRESHOLD = 15.0  # Start charging at 15%
CHARGE_RATE = 0.8  # Slower recharge rate

# Configure logging
logging.basicConfig(level=logging.INFO)

def simulate(device_id: str, location: List[float], initial_heading: float, test: bool) -> None:
    """Simulates a phone's movement with battery management."""
    speed_kmh = WALKING_SPEED_KMH
    total_distance_km = 0.0
    battery = 100.0
    is_charging = False

    while True:
        # Update battery state
        if is_charging:
            battery = min(100.0, battery + CHARGE_RATE)
            if battery >= 95.0:  # Resume movement at 95%
                is_charging = False
        elif battery <= LOW_BATTERY_THRESHOLD:
            is_charging = True
        else:
            battery = max(0.0, battery - BATTERY_DECREMENT)

        # Calculate movement
        velocity_vector = (0.0, 0.0, 0.0)
        if not is_charging:
            if random.randint(1, 5) == 1:
                initial_heading = random.choice([0, 90, 180, 270])
            velocity_vector = heading_to_vector(initial_heading, speed_kmh)

        # Update location
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
        )

        # Construct payload
        payload = {
            "deviceId": device_id,
            "timestamp": int(time.time()),
            "status": "charging" if is_charging else "moving",
            "location": location,
            "battery": round(battery, 1),
        }

        # Send/log data
        data_bytes = json.dumps(payload).encode("utf-8")
        if test:
            logging.info("Phone payload: %s", payload)
        else:
            send_to_kinesis(data=data_bytes, key=device_id)

        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) not in [4, 5]:
        print(f"Usage: {sys.argv[0]} <id> <location> <direction> [TEST]")
        sys.exit(1)
    
    id = sys.argv[1]
    location = parse_3d(sys.argv[2])
    direction = float(sys.argv[3])
    test = len(sys.argv) == 5 and sys.argv[4] == "TEST"
    
    simulate(f"phone-{id}", location, direction, test)