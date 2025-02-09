#!/bin/bash
# Update packages and install python3 if not already installed
yum update -y
yum install -y python3
yum install -y git

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

python3 "/src/EC2/IoT Devices/main.py"