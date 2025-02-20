import random
import threading
import subprocess
import sys
from typing import List

# Constants
NAIROBI_COORDINATES = [-1.292076, 36.821948, 0.000000]

def random_coordinates() -> List[float]:
    """Returns a random location within the square of Nairobi."""
    return [
        round(random.uniform(-1.307963, -1.282735), 6),  # Latitude
        round(random.uniform(36.808427, 36.844133), 6),  # Longitude
        0.000000  # Altitude
    ]

def random_seven_digit_integer() -> int:
    """Returns a random 7-digit integer."""
    return random.randint(1000000, 9999999)

def random_heading() -> float:
    """Returns a random heading in degrees (0 = North, 90 = East, etc.)."""
    return random.choice([0, 90, 180, 270])

def run_script(module_name: str) -> None:
    """Runs a device simulation module with random arguments.
    
    module_name: the module path without the .py extension,
                 e.g. "src.ec2.iot_devices.phone"
    """
    number_arg = random_seven_digit_integer()
    coords = random_coordinates()

    # Wrapping the coordinates in square brackets to form a valid JSON array string
    coords_str = f"[{','.join(map(str, coords))}]"
    heading = random_heading()
    
    # Running the module using subprocess
    command = [
        "python", "-m", module_name,
        str(number_arg), coords_str, str(heading)
    ]
    subprocess.run(command)

def spawn_threads(num_threads: int) -> None:
    """Spawns threads to simulate multiple devices concurrently."""
    max_threads = num_threads
    phone_threads = int(max_threads * 0.55)  # 55% phones
    car_threads = int(max_threads * 0.35)    # 35% cars
    drone_threads = max_threads - phone_threads - car_threads  # 10% drones

    threads = []

    # Simulate phones
    for _ in range(phone_threads):
        thread = threading.Thread(target=run_script, args=("src.ec2.iot_devices.phone",))
        threads.append(thread)

    # Simulate cars
    for _ in range(car_threads):
        thread = threading.Thread(target=run_script, args=("src.ec2.iot_devices.car",))
        threads.append(thread)

    # Simulate drones
    for _ in range(drone_threads):
        thread = threading.Thread(target=run_script, args=("src.ec2.iot_devices.drone",))
        threads.append(thread)

    # Start and join threads
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    if (len(sys.argv) not in [1, 2]):
        print(f"Usage: {sys.argv[0]} [NUM_THREADS]")
        sys.exit(1)
    num_threads = int(sys.argv[1]) if len(sys.argv) == 2 else 25
    spawn_threads(num_threads)