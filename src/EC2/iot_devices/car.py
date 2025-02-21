import time
import json
import sys
import random
import logging
from typing import List
from src.util.sim_functions import parse_3d, heading_to_vector, update_location_vector, send_to_kinesis
# from ....src.util.sim_functions import parse_3d, heading_to_vector, update_location_vector, send_to_kinesis

# Constants
DEGREES_PER_KM = 0.009  # Nairobi (not explicitly used here)
GAS_DECREMENT = 0.2  # Gas consumption per minute
GAS_REFILL_THRESHOLD = 30.0  # Refill gas when below this value
GAS_REFILL_AMOUNT = 100.0  # Gas refill amount

# Configure logging
logging.basicConfig(level=logging.INFO)

class Car:
    def __init__(self, device_id: str, location: List[float], heading: float, test: bool = True):
        self.device_id = device_id
        self.location = location
        self.heading = heading
        self.test = test
        # Random speed between 30-90 km/h on initialization
        self.speed_kmh = random.randint(30, 90)
        self.total_distance_km = 0.0
        self.gas = GAS_REFILL_AMOUNT

    def update_heading(self):
        """Randomly update the heading (1 in 5 chance)."""
        if random.randint(1, 5) == 1:
            self.heading = random.choice([0, 90, 180, 270])

    def update_gas(self):
        """Update gas level: refill if below threshold (with chance) and then consume gas."""
        did_refill = False
        if self.gas <= GAS_REFILL_THRESHOLD and random.randint(1, 10) == 1:
            self.gas = GAS_REFILL_AMOUNT
            did_refill = True
    
        if not did_refill:
            self.gas = min(GAS_REFILL_AMOUNT, max(round(self.gas - GAS_DECREMENT, 1), 0.0))


    def update_location(self):
        """Update location and total distance based on current heading and speed."""
        velocity_vector = heading_to_vector(self.heading, self.speed_kmh)
        self.location, self.total_distance_km = update_location_vector(
            self.location, velocity_vector, self.total_distance_km, self.speed_kmh
        )

    def get_payload(self):
        """Construct and return the payload dictionary."""
        payload = {
            "deviceId": self.device_id,
            "timestamp": int(time.time()),
            "status": "ping",
            "location": self.location,
            "gas": self.gas,
        }
        return payload

    def simulate_step(self):
        """Simulate a single step: update heading, gas, location and send/log payload."""
        self.update_heading()
        self.update_gas()
        self.update_location()
        payload = self.get_payload()
        if self.test:
            logging.info("Simulation payload: %s", payload)
        else:
            data_bytes = json.dumps(payload).encode("utf-8")
            send_to_kinesis(data=data_bytes, key=self.device_id)
        return payload

    def simulate(self, steps: int = 0, delay: float = 60.0):
        """Run the simulation for a given number of steps."""
        if steps == 0:
            while True:
                self.simulate_step()
                time.sleep(delay)
        for _ in range(steps):
            self.simulate_step()
            time.sleep(delay)

if __name__ == "__main__":
    if len(sys.argv) not in [4, 5]:
        print(f"Usage: {sys.argv[0]} <id> <location> <direction> [TEST]")
        sys.exit(1)

    device_id_arg = sys.argv[1]
    location_str = sys.argv[2]
    direction = float(sys.argv[3])
    test_mode = len(sys.argv) == 5 and sys.argv[4] == "TEST"

    location = parse_3d(location_str)
    device_id = f"car-{device_id_arg}"
    car = Car(device_id, location, direction, test_mode)
    car.simulate()
