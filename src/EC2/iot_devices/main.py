import random
import threading
import os

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

def run_script(script_name: str):
    """Runs a device simulation script with random arguments."""
    number_arg = random_seven_digit_integer()
    coords = random_coordinates()
    coords_str = ','.join(map(str, coords))
    heading = random_heading()
    
    # Run the script with arguments: <id> <location> <heading>
    os.system(f"python {script_name} {number_arg} {coords_str} {heading}")

def spawn_threads():
    """Spawns threads to simulate multiple devices concurrently."""
    max_threads = 30
    phone_threads = int(max_threads * 0.55)  # 55% phones
    car_threads = int(max_threads * 0.35)   # 35% cars
    drone_threads = max_threads - phone_threads - car_threads  # 10% drones

    threads = []

    # Simulate phones
    for _ in range(phone_threads):
        thread = threading.Thread(target=run_script, args=("phone.py",))
        threads.append(thread)

    # Simulate cars
    for _ in range(car_threads):
        thread = threading.Thread(target=run_script, args=("car.py",))
        threads.append(thread)

    # Simulate drones
    for _ in range(drone_threads):
        thread = threading.Thread(target=run_script, args=("drone.py",))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    spawn_threads()