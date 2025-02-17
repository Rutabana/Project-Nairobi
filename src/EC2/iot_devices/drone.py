import time
import json
import sys
import random
import logging
from typing import List
from src.util.sim_functions import parse_3d, heading_to_vector, update_location_vector, send_to_kinesis

# Constants
DEGREES_PER_KM = 0.009  # Nairobi (not explicitly used here)
ALTITUDE_CHANGE_RATE = 0.1  # Meters per second
BATTERY_DECREMENT = 0.5  # Battery drain per minute
LOW_BATTERY_THRESHOLD = 20.0  # Start descending at 20%
CHARGE_RATE = 1.2  # Battery recharge rate when landed
DESCENT_RATE = 0.3  # Altitude loss per second during descent

# Configure logging
logging.basicConfig(level=logging.INFO)

class Drone:
    def __init__(self, device_id: str, location: List[float], heading: float, test: bool = True):
        self.device_id = device_id
        self.location = location
        self.heading = heading
        self.test = test
        self.speed_kmh = random.randint(20, 60)
        self.total_distance_km = 0.0
        self.battery = 100.0
        self.is_descending = False
        self.is_landed = False

    def update_battery(self):
        """Update battery level and flight state based on current conditions."""
        if self.is_landed:
            self.battery = min(100.0, self.battery + CHARGE_RATE)
            if self.battery >= 95.0:
                self.is_landed = False
                self.is_descending = False
        elif self.battery <= LOW_BATTERY_THRESHOLD and not self.is_descending:
            self.is_descending = True
        elif self.is_descending:
            self.battery = max(0.0, self.battery - BATTERY_DECREMENT * 2)
        else:
            self.battery = max(0.0, self.battery - BATTERY_DECREMENT)

    def update_movement(self):
        """
        Update the drone's location based on its flight mode.
        
        - In normal flight, it moves according to its heading plus a random altitude change.
        - When descending, it loses altitude at a constant rate and lands if altitude reaches 0.
        - If landed, no movement occurs.
        """
        velocity_vector = (0.0, 0.0, 0.0)
        if not self.is_landed:
            if self.is_descending:
                velocity_vector = (0.0, 0.0, -DESCENT_RATE)
                if self.location[2] <= 0.0:
                    self.is_landed = True
                    velocity_vector = (0.0, 0.0, 0.0)
            else:
                velocity_vector = heading_to_vector(self.heading, self.speed_kmh)
                altitude_change = random.uniform(-ALTITUDE_CHANGE_RATE, ALTITUDE_CHANGE_RATE)
                velocity_vector = (velocity_vector[0], velocity_vector[1], altitude_change)
        self.location, self.total_distance_km = update_location_vector(
            self.location, velocity_vector, self.total_distance_km, self.speed_kmh
        )

    def get_payload(self):
        """Construct the payload dictionary for the current state."""
        status = "landed" if self.is_landed else "descending" if self.is_descending else "flying"
        payload = {
            "deviceId": self.device_id,
            "timestamp": int(time.time()),
            "status": status,
            "location": self.location,
            "battery": round(self.battery, 1),
        }
        return payload

    def simulate_step(self):
        """Perform a single simulation step: update battery, movement and send/log payload."""
        self.update_battery()
        self.update_movement()
        payload = self.get_payload()
        if self.test:
            logging.info("Drone payload: %s", payload)
        else:
            data_bytes = json.dumps(payload).encode("utf-8")
            send_to_kinesis(data=data_bytes, key=self.device_id)
        return payload

    def simulate(self, steps: int = 1, delay: float = 60.0):
        """Run the simulation for a specified number of steps."""
        for _ in range(steps):
            self.simulate_step()
            time.sleep(delay)

if __name__ == "__main__":
    if len(sys.argv) not in [4, 5]:
        print(f"Usage: {sys.argv[0]} <id> <location> <direction> [TEST]")
        sys.exit(1)
    
    id = sys.argv[1]
    location = parse_3d(sys.argv[2])
    direction = float(sys.argv[3])
    test_mode = len(sys.argv) == 5 and sys.argv[4] == "TEST"
    
    drone = Drone(f"drone-{id}", location, direction, test_mode)
    drone.simulate()
