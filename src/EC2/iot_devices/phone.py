import time
import json
import sys
import random
import logging
from typing import List
from src.util.sim_functions import parse_3d, heading_to_vector, update_location_vector, send_to_kinesis

# Constants
DEGREES_PER_KM = 0.009  # Nairobi
WALKING_SPEED_KMH = 5.0
BATTERY_DECREMENT = 0.3  # Battery drain per minute
LOW_BATTERY_THRESHOLD = 15.0  # Start charging at 15%
CHARGE_RATE = 0.8  # Slower recharge rate

logging.basicConfig(level=logging.INFO)

class Phone:
    def __init__(self, device_id: str, location: List[float], heading: float, test: bool = True):
        self.device_id = device_id
        self.location = location
        self.heading = heading
        self.test = test
        self.speed_kmh = WALKING_SPEED_KMH
        self.total_distance_km = 0.0
        self.battery = 100.0
        self.is_charging = False

    def update_battery(self):
        """Update battery state based on current level and charging state."""
        if self.is_charging:
            self.battery = min(100.0, self.battery + CHARGE_RATE)
            if self.battery >= 95.0:
                self.is_charging = False
        elif self.battery <= LOW_BATTERY_THRESHOLD:
            self.is_charging = True
        else:
            self.battery = max(0.0, self.battery - BATTERY_DECREMENT)

    def update_heading(self):
        """Randomly update heading (1 in 5 chance) if not charging."""
        if not self.is_charging and random.randint(1, 5) == 1:
            self.heading = random.choice([0, 90, 180, 270])

    def update_location(self):
        """Update location based on the current heading and speed."""
        if not self.is_charging:
            velocity_vector = heading_to_vector(self.heading, self.speed_kmh)
            self.location, self.total_distance_km = update_location_vector(
                self.location, velocity_vector, self.total_distance_km, self.speed_kmh
            )
        else:
            # When charging, do not update location or distance.
            pass


    def get_payload(self):
        """Construct the payload dictionary reflecting the current state."""
        payload = {
            "deviceId": self.device_id,
            "timestamp": int(time.time()),
            "status": "charging" if self.is_charging else "moving",
            "location": self.location,
            "battery": round(self.battery, 1),
        }
        return payload

    def simulate_step(self):
        """Run one simulation step: update battery, heading, location and send/log payload."""
        self.update_battery()
        self.update_heading()
        self.update_location()
        payload = self.get_payload()
        if self.test:
            logging.info("Phone payload: %s", payload)
        else:
            data_bytes = json.dumps(payload).encode("utf-8")
            send_to_kinesis(data=data_bytes, key=self.device_id)
        return payload

    def simulate(self, steps: int = 1, delay: float = 60.0):
        """Run the simulation for a given number of steps."""
        for _ in range(steps):
            self.simulate_step()
            time.sleep(delay)

if __name__ == "__main__":
    if len(sys.argv) not in [4, 5]:
        print(f"Usage: {sys.argv[0]} <id> <location> <direction> [TEST]")
        sys.exit(1)
    
    device_id = sys.argv[1]
    location = parse_3d(sys.argv[2])
    heading = float(sys.argv[3])
    test_mode = len(sys.argv) == 5 and sys.argv[4] == "TEST"
    
    phone = Phone(f"phone-{device_id}", location, heading, test_mode)
    phone.simulate()
