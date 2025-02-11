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
  cd /Project-Nairobi
  git pull
else
  git clone https://github.com/Rutabana/Project-Nairobi.git
  cd /Project-Nairobi
fi

python "/src/EC2/IoT Devices/main.py"