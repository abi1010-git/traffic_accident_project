# Traffic Accident Analysis Dashboard

This project analyzes traffic accident data with Python and presents the results in an interactive Streamlit dashboard. It includes both a Jupyter notebook for exploration and a web app for filtering, charting, mapping, and downloading accident records.

## Features

- Load the included NYC traffic accident sample dataset.
- Upload a custom accident CSV from the app sidebar.
- Filter crashes by date range, borough, and contributing factor.
- View summary metrics for crashes, injuries, fatalities, and borough count.
- Explore charts for crashes by hour, borough, contributing factor, and vehicle type.
- View crash locations on a map when latitude and longitude columns are available.
- Download the filtered dataset as a CSV.
- Run locally with Python or in Docker.

## Project Structure

```text
traffic_accident_project/
  app.py                         Streamlit dashboard
  Dockerfile                     Docker image setup
  requirements.txt               Python dependencies
  README.md                      Project instructions
  data/
    nyc_motor_vehicle_collisions_sample.csv
  notebooks/
    analysis.ipynb               Exploratory analysis notebook
  src/
    traffic_analysis.py          Notebook helper functions
```

## Dataset

The included sample comes from NYC Open Data's Motor Vehicle Collisions crash dataset. The app works best with CSV files that include columns such as:

- `crash_date`
- `crash_time`
- `borough`
- `latitude`
- `longitude`
- `number_of_persons_injured`
- `number_of_persons_killed`
- `contributing_factor_vehicle_1`
- `vehicle_type_code1`

If an uploaded CSV is missing some of those columns, the app still loads the data table and skips charts that cannot be created.

## Run The Streamlit App Locally

From the project folder:

```powershell
cd C:\Users\abhia\Desktop\project_2\traffic_accident_project
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL Streamlit prints:

```text
http://localhost:8501
```

## Upload A CSV

1. Open the Streamlit app.
2. Use the left sidebar.
3. Under `Data`, click `Upload accident CSV`.
4. Choose a `.csv` file from your computer.
5. The dashboard will update using the uploaded file.

If no file is uploaded, the app uses the included NYC sample dataset.

## Run With Docker

Make sure Docker Desktop is running first.

Build the Docker image:

```powershell
docker build -t traffic-accident-dashboard .
```

Run the app:

```powershell
docker run --rm -p 8501:8501 traffic-accident-dashboard
```

Open:

```text
http://localhost:8501
```

If you already have a container named `traffic-accident-dashboard`, stop and remove it before starting a new one:

```powershell
docker stop traffic-accident-dashboard
docker rm traffic-accident-dashboard
docker run -d --name traffic-accident-dashboard -p 8501:8501 traffic-accident-dashboard
```

## Run The Notebook

1. Open `notebooks/analysis.ipynb` in VS Code.
2. Select the project virtual environment as the notebook kernel.
3. Run the notebook cells from top to bottom.

The notebook loads the first `.csv`, `.xlsx`, or `.xls` file it finds in `data/`.

## Save Changes To GitHub

```powershell
git add .
git commit -m "Update traffic accident dashboard"
git push
```
