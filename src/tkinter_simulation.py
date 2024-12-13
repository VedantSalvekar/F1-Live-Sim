#MOCK DATA TRAIL D_LOOKUP
import tkinter as tk
import math
from influxdb_client import InfluxDBClient
import time

# Tkinter Setup
root = tk.Tk()
root.title("F1 Race Simulation")
root.geometry("1000x800")
root.configure(bg="#202A44")

canvas_width = 1000
canvas_height = 800

canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#202A44")
canvas.pack()

# Track Configuration
scale_factor = 2.9
track_points = [
    (int(120 * scale_factor), int(canvas_height - 120 * scale_factor)),
    (int(300 * scale_factor), int(canvas_height - 120 * scale_factor)),
    (int(320 * scale_factor), int(canvas_height - 140 * scale_factor)),
    (int(210 * scale_factor), int(canvas_height - 140 * scale_factor)),
    (int(150 * scale_factor), int(canvas_height - 150 * scale_factor)),
    (int(100 * scale_factor), int(canvas_height - 200 * scale_factor)),
    (int(50 * scale_factor), int(canvas_height - 190 * scale_factor))
]

canvas.create_polygon(track_points, outline="orange", fill="", width=10, joinstyle=tk.ROUND)
track_path = [(track_points[i][0], track_points[i][1]) for i in range(len(track_points))]

# Driver Lookup (from message_handler.py)
D_LOOKUP = [
    [44, 'HAM', 'Mercedes', '#6CD3BF', 'SOLID'],
    [63, 'RUS', 'Mercedes', '#6CD3BF', 'DOT'],
    [55, 'SAI', 'Ferrari', '#F91536', 'DOT'],
    [16, 'LEC', 'Ferrari', '#F91536', 'SOLID'],
    [1, 'VER', 'Red Bull', '#3671C6', 'SOLID'],
    [11, 'PER', 'Red Bull', '#3671C6', 'DOT']
]

# Car Configuration
car_radius = 6
cars = []

# InfluxDB Configuration
influx_url = "http://localhost:8086"
token = "LoOFvHw1tUXrUZ8oUqaozmEjxxG9UNO5H5YfRI4cGu306xwQVu_KMNxRYRMrWbhdD886N2PuRgpo9v4v_58pHw=="
org = "f1"
bucket = "data"

# Fetch live car speeds
def fetch_car_speeds():
    speeds = {}
    with InfluxDBClient(url=influx_url, token=token, org=org) as client:
        query_api = client.query_api()
        query = f'''
        from(bucket: "{bucket}")
        |> range(start: -10s)
        |> filter(fn: (r) => r._measurement == "speedTrap")
        |> group(columns: ["driver"])
        |> last()
        '''
        tables = query_api.query(query)
        for table in tables:
            for record in table.records:
                speeds[record["driver"]] = float(record["_value"]) / 100  # Scale down for simulation
    return speeds

# Initialize cars
def initialize_cars():
    speeds = fetch_car_speeds()
    for driver_entry in D_LOOKUP:
        driver_no = driver_entry[0]  
        driver_color = driver_entry[3]  
        driver_name = driver_entry[1]  

        # Check if speed data exists for this driver
        speed = speeds.get(driver_name, 0.5)  # Default to 0.5 if no data available

        #car object
        car = {
            "driver_no": driver_no,
            "driver_name": driver_name,
            "index": 0,
            "progress": 0.0,
            "speed": speed,
            "color": driver_color,
            "id": canvas.create_oval(0, 0, 0, 0, fill=driver_color),
            "label": canvas.create_text(0, 0, text=str(driver_no), fill="white")
        }
        cars.append(car)

# Update Car Animation
def animate():
    speeds = fetch_car_speeds()  # Fetch updated speeds from InfluxDB
    for car in cars:
        # Update speed if new data is available
        car["speed"] = speeds.get(car["driver_name"], car["speed"])

        # Current and next points on the track
        p1 = track_path[car["index"]]
        p2 = track_path[(car["index"] + 1) % len(track_path)]

        # Calculate direction vector
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Update progress along the segment
        car["progress"] += car["speed"] / distance
        if car["progress"] >= 1.0:
            car["progress"] = 0.0
            car["index"] = (car["index"] + 1) % len(track_path)

        # Calculate position
        x = p1[0] + dx * car["progress"]
        y = p1[1] + dy * car["progress"]

        # Update car's position on canvas
        canvas.coords(
            car["id"],
            x - car_radius, y - car_radius,
            x + car_radius, y + car_radius
        )
        # Update driver's label position
        canvas.coords(
            car["label"],
            x, y - 15
        )

    root.after(30, animate)

initialize_cars()
animate()

root.mainloop()