import time
import json
import boto3
import sys
from botocore.exceptions import ClientError

kinesis_client = boto3.client('kinesis', region_name='us-east-2')
stream_name ='nairobi-stream'

def simulate(id, location):
  device_id = f'car-{id}'
  while True:
    # Construct the JSON payload
    payload = {
      "deviceId": device_id,
      "timestamp": int(time.time()),
      "status": "ping",
      "location": location,
      "gas": 100
    }

    # Convert to bytes
    data_bytes = json.dumps(payload).encode('utf-8')

    try:
      response = kinesis_client.put_record(
        StreamName=stream_name,
        Data=data_bytes,
        ParitionKey=device_id,
      )
      # print(f"Send record {response['SequenceNumber']}")
    except ClientError as e:
      print(f"Failed to send record: {e}")
      # TODO: Implement a backoff strategy here
    
    time.sleep(3) #TODO: change this to 10 when I know it's working

if __name__ == '__main__':
  if (len(sys.argv) == 3):
    id = sys.argv[1]
    location = sys.argv[2]
    simulate(id, location)