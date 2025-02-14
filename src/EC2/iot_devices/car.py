import time
import json
import sys
import random
import logging
from typing import List, Tuple
from src.util.sim_functions import *

DEGREES_PER_KM = 0.009  # Nairobi
logging.basicConfig(level=logging.INFO)

def simulate(device_id: str, location: List[float], 
             direction: float, test: bool) -> None:
    speed_kmh = random.randint(30, 90)  # km/h
    direction = random.choice(["North", "East", "South", "West", "none"])
    total_distance_km = 0
    gas = 100.0

    while True:
        # Consider turning
        if random.randint(1, 5) == 1:
            direction = random.choice([0, 90, 180, 270, "none"])

        # Consider getting gas
        if gas <= 30 and random.randint(1, 10) == 1:
            gas = 100.0

        # Fix: float operations may result in incorrect approximates. This also handles edge cases
        gas = min(100.0, max(round(gas - 0.2, 1), 0.0))
        
        velocity_vector = heading_to_vector(direction, speed_kmh)
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
            send_to_kinesis(
                data=data_bytes,
                key=device_id,
            )
        time.sleep(60)


if __name__ == "__main__":
    size = len(sys.argv)
    required_args = 3  # device_id, location and direction
    if len(sys.argv) not in [
        required_args + 1,
        required_args + 2,
    ]:  # +1 for script name
        print(f"Usage: {sys.argv[0]} <id> <location> <direction> [TEST]")
        sys.exit(1)
    else:
        id = sys.argv[1]
        location = parse_3d(sys.argv[2])
        direction = sys.argv[3]
        device_id = f"car-{id}"
        test = size == 5 and sys.argv[4] == "TEST"

        simulate(device_id, location, direction, test)
