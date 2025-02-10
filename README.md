# 🌆**Project Nairobi**  
Project Nairobi is a real-time distributed analytics platform built on AWS, simulating an urban environment in Nairobi, Kenya. The project ingests high-volume IoT and social media data—such as simulated phone pings, vehicle telemetry, and drone sensor readings—using **AWS Kinesis**. This data is processed in near real-time by **AWS Lambda** and stored in **Amazon S3** for further analysis.

---

## 🚀 **Why Project Nairobi?**  
This project serves as both a learning journey and an exploration of real-world distributed systems, data streaming, and cloud architecture. By leveraging AWS services like **EC2, Kinesis, Lambda, S3, and Auto Scaling Groups (ASG)**, Project Nairobi aims to demonstrate best practices in scalability, fault tolerance, and cost optimization.

---

## 🏗 **Current Architecture**  
- **📡 Data Generation:** EC2 instances simulate thousands of IoT devices (phones, cars, and drones) sending location and status data.  
- **🚀 Streaming Ingestion:** AWS Kinesis Data Streams handles high-throughput data ingestion.  
- **⚡ Processing Pipeline:** AWS Lambda processes incoming data in real-time, detects anomalies, and forwards structured data.  
- **📂 Storage & Analysis:** Amazon S3 stores raw event data for long-term storage and future analytics.  

---

## 📌 **Next Steps**  
- ✅ Implement **DynamoDB** for real-time state tracking.  
- ✅ Improve **event processing logic** in Lambda.  
- 🔄 Automate deployment with **GitHub Actions** (pull latest scripts on ASG instances).  

---

## 📜 **License**  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.  

---

## 🤝 **Contributing**  
Pull requests are welcome! If you'd like to contribute, please fork the repository and submit a PR with your changes.  

---

## 📧 **Contact**  
For any questions, feel free to reach out or open an issue in the repo.  
