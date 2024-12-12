# F1 Live Data Visualization and Simulation

An interactive and real-time tool to visualize live or mock F1 telemetry data. This project integrates **InfluxDB**, **Grafana**, and a **Tkinter-based simulation** to provide a comprehensive view of F1 race data.

---

## Requirements

- Docker installed
- Python 3.8 or later installed
- `pip` package manager installed

---

## Quick Start

### **Step 1: Run Docker Services**

Open a terminal window and run the following commands to start the Docker services for InfluxDB and Grafana:

1. Navigate to the project folder:

   ```bash
   cd prj
   ```

2. Set the correct permissions and start the services:

   ```bash
   docker-compose up -d
   docker build -t data-importer-image . --no-cache
   ```

3. Run the mock data importer:

   ```bash
  docker run -it --rm `
  -network f1-live-data-master_default `
  -v ${PWD}/saves/partial_saved_data_2023_03_05.txt:/tmp/save.txt `
  data-importer-image `
  dataimporter processsimulationdata /tmp/save.txt `
  --influxurl http://influxdb:8086
   ```

   - This command loads the mock telemetry data from the file `partial_saved_data_2023_03_05.txt` and populates the InfluxDB database.
   - You can view the dashboard at [http://localhost:3000](http://localhost:3000).
   - Grafana credentials:
     - Username: `admin`
     - Password: `admin`

### **Step 2: Run the Tkinter Simulation**

Open a second terminal window and run the simulation:

1. Navigate to the `src` folder:

   ```bash
   cd prj/src
   ```

2. Activate the virtual environment (if applicable):

   ```bash
   source ../env/bin/activate
   ```

3. Run the simulation script:

   ```bash
   python tkinter_simulation.py
   ```

   - The simulation animates F1 cars on a fixed track.
   - Cars are assigned driver numbers and colors based on predefined driver data (`D_LOOKUP` in the code).
   - Speeds and positions update dynamically based on mock telemetry data from InfluxDB.

---

## Features

- **Live Telemetry Visualization**:
  - Displays key race data, such as leaderboard positions, lap times, gaps to the leader, and weather data.
  - Panels include:
    - Interval
    - Gap to Leader
    - Last Lap Time
    - Weather Data
    - Speed Trap Data
- **Tkinter Simulation**:
  - A graphical simulation of cars moving on a fixed F1-style track.
  - Cars are dynamically assigned driver numbers, colors, and speeds based on telemetry data.
  - Simulates the telemetry updates in real time.
- **Mock Data Integration**:
  - Supports mock data replay with a speedup factor of 100, allowing for efficient debugging and development.

---

## Data Flow

```
┌─────────────┐      ┌────────┐      ┌───────┐
│data-importer├─────►│influxdb│◄─────┤grafana│
└─────────────┘      └────────┘      └───────┘
          ▲
          │
    ┌────────────┐
    │ Tkinter Sim│
    └────────────┘
```

- The `data-importer` processes mock telemetry data and pushes it to the InfluxDB database.
- Grafana visualizes the data in real-time using preconfigured dashboards.
- The Tkinter simulation fetches data from InfluxDB and animates cars on a track.

---

## Simulation Details

- **Track**:
  - Fixed polygonal track.
  - Configurable scale factor for the track size.
- **Drivers**:
  - Predefined drivers with unique numbers and colors (e.g., `HAM`, `VER`).
  - Each car's movement is determined by live telemetry data (`speedTrap`) from InfluxDB.
- **Execution**:
  - The simulation must be run alongside the Docker-based InfluxDB service.
  - Cars dynamically update their speeds and positions as data changes.

---

## Processed Data

The project processes a subset of data provided by `fastf1`:

```
Processed: WeatherData, RaceControlMessages, TimingData, SpeedTrap, DriverComparision, GapToLeader
```

---

## Steps to Debug or Customize

### Run the Data-Importer Locally

For debugging purposes, you can run the `data-importer` directly on your machine:

```bash
docker-compose up -d
pip install .
python -m dataimporter process-mock-data saves/partial_saved_data_2023_03_05.txt --influx-url http://localhost:8086
```

### Modify the Tkinter Simulation

To customize the simulation:

- Update the driver data (`D_LOOKUP`) in the `tkinter_simulation.py` script to reflect your desired drivers and colors.
- Adjust the track's scale or points in the script.

---

## Known Issues

- The `data-importer` may disconnect after 2 hours due to limitations of the data service.
- The Tkinter simulation currently supports only mock data, not live telemetry.

---
