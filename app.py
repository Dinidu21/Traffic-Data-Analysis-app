import os
import re
from flask import Flask, render_template, request, send_from_directory
import csv

# Initialize the Flask application
app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'

# Ensure the upload folder exists
def ensure_upload_folder_exists():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created new folder: {UPLOAD_FOLDER}")
    else:
        print(f"Using existing folder: {UPLOAD_FOLDER}")

ensure_upload_folder_exists()

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# In the submit route, add a function to check the CSV structure
def validate_csv(file):
    try:
        with open(file, mode='r') as f:
            reader = csv.DictReader(f)
            return list(reader)[:5]  # return the first 5 rows for preview
    except Exception as e:
        return None

# Function to process the CSV file
def process_csv_data(file_name, day, month, year):
    print(f"Processing {file_name}")
    # Initialize metrics dictionary
    outcomes = {
        "Total Vehicles": 0,
        "Total Trucks": 0,
        "Total Electric Vehicles": 0,
        "Two-Wheeled Vehicles": 0,
        "Buses North": 0,
        "Straight Through": 0,
        "Truck Percentage": 0,
        "Over Speed Limit": 0,
        "Elm Ave Rabbit Road": 0,
        "Hanley Highway Westway": 0,
        "Scooter Percentage": 0,
        "Highest Hourly Count": 0,
        "Most Vehicles Hour": "",
        "Rain Hours": 0,
        "Date": f"{day:02d}{month:02d}{year}",
        "Data File": os.path.basename(file_name)
    }

    if not os.path.exists(file_name):
        print(f"File {file_name} does not exist.")
        return None

    total_vehicles = 0
    total_trucks = 0
    total_electric_vehicles = 0
    two_wheeled_vehicles = 0
    buses_north = 0
    straight_through = 0
    over_speed_limit = 0
    elm_ave_vehicles = 0
    hanley_highway_vehicles = 0
    scooters = 0
    rainy_hours = set()
    hanley_hourly_counts = {}
    total_bicycle_count = 0

    try:
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                vehicle_type = row["VehicleType"]
                time_of_day = row["timeOfDay"]
                speed_limit = int(row["JunctionSpeedLimit"])
                vehicle_speed = int(row["VehicleSpeed"])
                is_electric = row["electricHybrid"] == "True"
                junction_name = row["JunctionName"]
                weather_conditions = row["Weather_Conditions"]
                travel_in = row["travel_Direction_in"]
                travel_out = row["travel_Direction_out"]

                total_vehicles += 1

                if junction_name == "Elm Avenue/Rabbit Road":
                    elm_ave_vehicles += 1
                if junction_name == "Hanley Highway/Westway":
                    hanley_highway_vehicles += 1

                if vehicle_type == "Truck":
                    total_trucks += 1
                if is_electric:
                    total_electric_vehicles += 1
                if vehicle_type in ["Bicycle", "Motorcycle", "Scooter"]:
                    two_wheeled_vehicles += 1

                if junction_name == "Elm Avenue/Rabbit Road" and vehicle_type == "Bus" and travel_out == "N":
                    buses_north += 1

                if travel_in == travel_out:
                    straight_through += 1

                if vehicle_speed > speed_limit:
                    over_speed_limit += 1

                if vehicle_type == "Scooter" and junction_name == "Elm Avenue/Rabbit Road":
                    scooters += 1

                if junction_name == "Hanley Highway/Westway":
                    hour = time_of_day.split(":")[0]
                    if hour not in hanley_hourly_counts:
                        hanley_hourly_counts[hour] = 0
                    hanley_hourly_counts[hour] += 1

                if vehicle_type == "Bicycle":
                    hour = time_of_day.split(":")[0]
                    total_bicycle_count += 1

                if weather_conditions in ["Light Rain", "Heavy Rain"]:
                    hour = time_of_day.split(":")[0]
                    rainy_hours.add((row["Date"], hour))

        total_rainy_hours = len(rainy_hours)

        outcomes.update({
            "Total Vehicles": total_vehicles,
            "Total Trucks": total_trucks,
            "Total Electric Vehicles": total_electric_vehicles,
            "Two-Wheeled Vehicles": two_wheeled_vehicles,
            "Buses North": buses_north,
            "Straight Through": straight_through,
            "Over Speed Limit": over_speed_limit,
            "Elm Ave Rabbit Road": elm_ave_vehicles,
            "Hanley Highway Westway": hanley_highway_vehicles,
            "Truck Percentage": round((total_trucks / total_vehicles) * 100) if total_vehicles else 0,
            "Rain Hours": total_rainy_hours,
        })

        unique_hours_in_day = len(set(range(0, 24)))  # 24 hours in a day
        average_bicycles_per_hour = round(total_bicycle_count / unique_hours_in_day) if unique_hours_in_day > 0 else 0
        outcomes["Average Bicycles Per Hour"] = average_bicycles_per_hour

        if elm_ave_vehicles > 0:
            scooter_percentage = (scooters / elm_ave_vehicles) * 100
            outcomes["Scooter Percentage"] = int(scooter_percentage)
        else:
            outcomes["Scooter Percentage"] = 0

        if hanley_hourly_counts:
            highest_hourly_count = max(hanley_hourly_counts.values())
            outcomes["Highest Hourly Count"] = highest_hourly_count
            most_vehicles_hours = [hour for hour, count in hanley_hourly_counts.items() if count == highest_hourly_count]
            outcomes["Most Vehicles Hour"] = " and ".join([f"Between {hour}:00 and {int(hour) + 1}:00" for hour in most_vehicles_hours])

    except Exception as e:
        print(f"Error processing file: {e}")
        return None

    return outcomes

# Route to render the form
@app.route('/')
def home():
    return render_template('form.html')


# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        file = request.files['file']

        if file:
            ensure_upload_folder_exists()
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Extract day, month, and year from the filename (e.g., traffic_data15062024.csv)
            filename = file.filename
            date_match = re.search(r'(\d{2})(\d{2})(\d{4})', filename)

            if date_match:
                day = int(date_match.group(1))  # Extract day
                month = int(date_match.group(2))  # Extract month
                year = int(date_match.group(3))  # Extract year
            else:
                print("Date not found in filename, using default values.")
                day, month, year = 1, 1, 2024

            # Process CSV and get outcomes
            outcomes = process_csv_data(file_path, day, month, year)

            if outcomes:
                return render_template('results.html', outcomes=outcomes)
            else:
                return "Error processing the file", 400
        else:
            return "No file selected", 400

# Route to render results
@app.route('/results')
def results():
    return render_template('results.html')

# For serverless deployment
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def create_app():
    return app

if __name__ == '__main__':
    app.run()