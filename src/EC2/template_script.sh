#!/bin/bash
# Update packages and install python3 if not already installed
yum update -y
yum install -y python
yum install -y pip
yum install -y git

# Install necessary modules for python scripts
pip install boto3

# Change to a working directory (optional)
cd /home/ec2-user
# Check if the directory Project-Nairobi exists
if [ -d "Project-Nairobi" ]; then
  git pull
else
  git clone https://github.com/Rutabana/Project-Nairobi.git
fi

cd "/Project-Nairobi/src/EC2/IoT Devices"
python main.py