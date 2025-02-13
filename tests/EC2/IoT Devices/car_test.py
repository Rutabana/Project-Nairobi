import subprocess
import time

# ---------------------------------- UNIT TEST ---------------------------------- #



def test_car_simulation():
  script = "src/EC2/IoT Devices/car.py"
  # Define the command to run car.py with the specified arguments
  command = [
    'python', 
    script, 
    '123', 
    '"[-1.292076, 36.821948, 0.000000]"', 
    'TEST'
  ]
  command = f"python \"{script}\" 123 \"[-1.292076, 36.821948, 0.000000]\" TEST"
  
  # Start the subprocess
  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  
  # Allow the process to run for 5 seconds
  time.sleep(5)
  
  # Terminate the process
  process.terminate()
  
  # Get the standard output and error
  stdout, stderr = process.communicate()
  
  # Decode the output from bytes to string
  output = stdout.decode('utf-8')
  error = stderr.decode('utf-8')
  print(error)
  print(output)
  
  # Check if the output is not an empty string
  assert output != '', "The output should not be an empty string"

# Run the test
test_car_simulation()