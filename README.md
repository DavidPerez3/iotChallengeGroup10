# IoT Project: Group 10

## Project Description
This repository contains the implementation of our IoT project for the course "Internet of Things." Our project focuses on creating a system that integrates sensors, data processing, and visualization to provide innovative solutions for monitoring and managing environmental data effectively. This project consists of a simulation of a medical consult with an elderly patient, who lives alone in his house.

### Objectives
1. Develop a functional IoT solution integrating multiple components.
2. Utilize diverse sensors and actuators to gather and process data.
3. Implement data visualization and interaction capabilities.
4. Incorporate advanced features to enhance usability and functionality.

## System Overview

### Hardware Components
- **Sensors:** 
  - Temperature and Humidity Sensor: Tracks climate data.
  - Ultrasonic Ranger: Measures distances for object detection.
  - Sound Sensor: Detects sound around it.
  - Touch Sensor: Recognizes physical contact.
- **Actuators:**
  - LED: Indicates system states or alerts.
  - LCD Screen: Shows customizable text.
  - Buzzer: Emits sound.

### Software Components
- **Programming Languages:**
  - Python
- **Frameworks and Libraries:**
  - Flask for web interface
  - InfluxDB for data storage

### Features
- Real-time data collection and monitoring.
- Interactive web-based dashboard.
- Historical data analysis.

## System Architecture
The system architecture includes sensor data acquisition, data processing via Raspberry Pi, storage in InfluxDB, and visualization on Flask.

## Installation and Setup

### Prerequisites
1. Raspberry Pi.
2. Sensors and actuators listed above.
3. Python 3.x installed on the system.
4. InfluxDB installed on the system.
5. Flask installed on the system.

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/DavidPerez3/iotChallengeGroup10.git
   ```
2. Create a virtual environment

3. Activate the environment
   ```bash
   source /route_to_the_environment/bin/activate
   ```

4. Configure your sensors and actuators pins inside the medicalConsult.py file.

5. Run InfluxDB (in another terminal); make sure you are running this command where your influxd.exe file is located.
   ```bash
   influxd.exe
   ```

6. Access localhost:8086, where the InfluxDB host is running, and create your own bucket.

7. Configure your InfluxDB token, URL and bucket name inside the medicalConsult.py file.

8. Execute the file, medicalConsult.py, and follow the screen instructions:
   ```bash
   python3 medicalConsult.py
   ```

9. Run the main script:
   ```bash
   cd iot-project/   
   python app.py
   ```

## Usage
1. Access the web dashboard by navigating to it in `http://<your-raspberry-pi-ip>:<port>` in a browser.
2. Monitor real-time sensor data.
3. Review historical data and insights on the Flask dashboard.

## Documentation

### API Endpoints
| Endpoint         | Method | Description                   |
|------------------|--------|-------------------------------|
| `/`              | GET    | Show last consult data        |
| `/graphs`        | GET    | Show historical data          |

## Contributions

### Team Members
1. Member 1: David Perez
2. Member 2: Iker Ordoñez
3. Member 3: Imanol Alonso
