import time
import json
import sys
import random
import logging
from typing import List
from src.util.sim_functions import *

# Constants
DEGREES_PER_KM = 0.009  # Nairobi
ALTITUDE_CHANGE_RATE = 0.1  # Meters per second
BATTERY_DECREMENT = 0.5  # Battery drain per minute
LOW_BATTERY_THRESHOLD = 20.0  # Start descending at 20%
CHARGE_RATE = 1.2  # Battery recharge rate when landed
DESCENT_RATE = 0.3  # Altitude loss per second during descent

# Configure logging
logging.basicConfig(level=logging.INFO)

def simulate(device_id: str, location: List[float], initial_heading: float, test: bool) -> None:
    """Simulates a drone's movement with battery management."""
    speed_kmh = random.randint(20, 60)
    total_distance_km = 0.0
    battery = 100.0
    is_descending = False
    is_landed = False

    while True:
        # Update battery based on state
        if is_landed:
            battery = min(100.0, battery + CHARGE_RATE)
            if battery >= 95.0:  # Resume flight at 95% charge
                is_landed = False
                is_descending = False
        elif battery <= LOW_BATTERY_THRESHOLD and not is_descending:
            is_descending = True
        elif is_descending:
            battery = max(0.0, battery - BATTERY_DECREMENT * 2)  # Faster drain during descent
        else:
            battery = max(0.0, battery - BATTERY_DECREMENT)

        # Calculate movement
        velocity_vector = (0.0, 0.0, 0.0)
        if not is_landed:
            if is_descending:
                # Descend while maintaining horizontal position
                velocity_vector = (0.0, 0.0, -DESCENT_RATE)
                if location[2] <= 0.0:  # Landed
                    is_landed = True
                    velocity_vector = (0.0, 0.0, 0.0)
            else:
                # Normal flight
                velocity_vector = heading_to_vector(initial_heading, speed_kmh)
                altitude_change = random.uniform(-ALTITUDE_CHANGE_RATE, ALTITUDE_CHANGE_RATE)
                velocity_vector = (velocity_vector[0], velocity_vector[1], altitude_change)

        # Update location
        location, total_distance_km = update_location_vector(
            location, velocity_vector, total_distance_km, speed_kmh
        )

        # Construct payload
        payload = {
            "deviceId": device_id,
            "timestamp": int(time.time()),
            "status": "landed" if is_landed else "descending" if is_descending else "flying",
            "location": location,
            "battery": round(battery, 1),
        }

        # Send/log data
        data_bytes = json.dumps(payload).encode("utf-8")
        if test:
            logging.info("Drone payload: %s", payload)
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
    
    simulate(f"drone-{id}", location, direction, test)