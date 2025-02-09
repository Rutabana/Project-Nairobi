#!/bin/bash
# Update packages and install python3 if not already installed
yum update -y
yum install -y python3

# Change to a working directory (optional)
cd /home/ec2-user

# Create the simulation script file
cat > phone.py << 'EOF'
#!/usr/bin/env python3
import time
import json
import boto3
from botocore.exceptions import ClientError

kinesis_client = boto3.client('kinesis', region_name='us-east-2')
stream_name ='nairobi-stream'
device_id = 'phone-123'

def simulate():
  while True:
    # Construct the JSON payload
    payload = {
      "deviceId": device_id,
      "timestamp": int(time.time()),
      "status": "ping"
    }

    # Convert to bytes
    data_bytes = json.dumps(payload).encode('utf-8')

    try:
      response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=data_bytes,
        ParitionKey=device_id,
      )
      print(f"Send record {response['SequenceNumber']}")
    except ClientError as e:
      print(f"Failed to send record: {e}")
      # TODO: Implement a backoff strategy here
    
    time.sleep(3) #TODO: change this to 10 when I know it's working

if __name__ == '__main__':
  simulate()EOF

# Make the script executable
chmod +x phone.py

# Run the simulation script in the background
nohup python3 phone.py > phone.log 2>&1 &