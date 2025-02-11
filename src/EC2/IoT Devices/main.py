import random
import threading
import os

nairobi_coordinates = [-1.292076, 36.821948]

# Returns a random location in the city
# square of Nairobi
def random_coordinates():
  return [
    round(random.uniform(-1.307963, -1.282735), 6), # Latitude
    round(random.uniform(36.808427, 36.844133), 6), # Longitude
    0                                               # Altitude
    ]
  
def random_seven_digit_integer():
  return random.randint(1000000, 9999999)

def run_script(script_name):
    # Call the functions and convert the coordinates list to a comma-separated string
    number_arg = random_seven_digit_integer()
    coords = random_coordinates()
    coords_str = ','.join(map(str, coords))
    
    os.system(f"python {script_name}\" {number_arg} {coords_str}")


def spawn_threads():
  max_threads = 25
  phone_threads = int(max_threads * 0.55)
  car_threads = int(max_threads * 0.35)
  drone_threads = max_threads - phone_threads - car_threads

  threads = []

  # Simulate multiple devices concurrently
  for _ in range(phone_threads):
    thread = threading.Thread(target=run_script, args=("phone.py",))
    threads.append(thread)

  for _ in range(car_threads):
    thread = threading.Thread(target=run_script, args=("car.py",))
    threads.append(thread)

  for _ in range(drone_threads):
    thread = threading.Thread(target=run_script, args=("drone.py",))
    threads.append(thread)

  for thread in threads:
    thread.start()

  for thread in threads:
    thread.join()

if __name__ == "__main__":
  spawn_threads()
