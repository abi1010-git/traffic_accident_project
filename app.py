from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DATASET = DATA_DIR / "nyc_motor_vehicle_collisions_sample.csv"


st.set_page_config(
    page_title="Traffic Accident Dashboard",
    page_icon="car",
    layout="wide",
)


def prepare_data(df):
    df.columns = df.columns.str.strip().str.lower()

    if "crash_date" in df.columns:
        df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")

    if "crash_time" in df.columns:
        df["hour"] = pd.to_datetime(df["crash_time"], format="%H:%M", errors="coerce").dt.hour

    numeric_columns = [
        "number_of_persons_injured",
        "number_of_persons_killed",
        "number_of_pedestrians_injured",
        "number_of_pedestrians_killed",
        "number_of_cyclist_injured",
        "number_of_cyclist_killed",
        "number_of_motorist_injured",
        "number_of_motorist_killed",
        "latitude",
        "longitude",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return prepare_data(df)


@st.cache_data
def load_uploaded_data(file_name, file_bytes):
    df = pd.read_csv(BytesIO(file_bytes))
    return prepare_data(df)


def value_counts_chart(df, column, title, top_n=10):
    if column not in df.columns:
        st.info(f"No `{column}` column found.")
        return

    counts = (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .replace({"nan": "Unknown", "NaN": "Unknown"})
        .value_counts()
        .head(top_n)
    )

    st.subheader(title)
    st.bar_chart(counts)


def filter_data(df):
    filtered = df.copy()

    st.sidebar.header("Filters")

    if "crash_date" in filtered.columns and filtered["crash_date"].notna().any():
        min_date = filtered["crash_date"].min().date()
        max_date = filtered["crash_date"].max().date()
        selected_dates = st.sidebar.date_input(
            "Crash date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            filtered = filtered[
                filtered["crash_date"].dt.date.between(start_date, end_date)
            ]

    if "borough" in filtered.columns:
        boroughs = sorted(filtered["borough"].dropna().unique())
        selected_boroughs = st.sidebar.multiselect(
            "Borough",
            options=boroughs,
            default=boroughs,
        )

        if selected_boroughs:
            filtered = filtered[filtered["borough"].isin(selected_boroughs)]

    if "contributing_factor_vehicle_1" in filtered.columns:
        factors = sorted(filtered["contributing_factor_vehicle_1"].dropna().unique())
        selected_factors = st.sidebar.multiselect(
            "Contributing factor",
            options=factors,
        )

        if selected_factors:
            filtered = filtered[
                filtered["contributing_factor_vehicle_1"].isin(selected_factors)
            ]

    return filtered


st.title("Traffic Accident Dashboard")

st.sidebar.header("Data")
uploaded_file = st.sidebar.file_uploader("Upload accident CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = load_uploaded_data(uploaded_file.name, uploaded_file.getvalue())
        dataset_name = uploaded_file.name
    except Exception as error:
        st.error(f"Could not load the uploaded CSV: {error}")
        st.stop()
else:
    if not DEFAULT_DATASET.exists():
        st.error(
            "No accident CSV found. Add `nyc_motor_vehicle_collisions_sample.csv` "
            "to the `data` folder, or update `DEFAULT_DATASET` in app.py."
        )
        st.stop()

    df = load_data(DEFAULT_DATASET)
    dataset_name = DEFAULT_DATASET.name

filtered_df = filter_data(df)

st.caption(f"Loaded `{dataset_name}` with {len(df):,} total records.")

metric_columns = st.columns(4)
metric_columns[0].metric("Crashes", f"{len(filtered_df):,}")
metric_columns[1].metric(
    "People Injured",
    f"{filtered_df.get('number_of_persons_injured', pd.Series(dtype=float)).sum():,.0f}",
)
metric_columns[2].metric(
    "People Killed",
    f"{filtered_df.get('number_of_persons_killed', pd.Series(dtype=float)).sum():,.0f}",
)
metric_columns[3].metric(
    "Boroughs",
    f"{filtered_df.get('borough', pd.Series(dtype=object)).nunique():,}",
)

tab_overview, tab_location, tab_details = st.tabs(["Overview", "Location", "Data"])

with tab_overview:
    left, right = st.columns(2)

    with left:
        if "hour" in filtered_df.columns:
            st.subheader("Crashes By Hour")
            hourly = filtered_df["hour"].dropna().astype(int).value_counts().sort_index()
            st.bar_chart(hourly)
        else:
            st.info("No crash time column found.")

    with right:
        value_counts_chart(
            filtered_df,
            "contributing_factor_vehicle_1",
            "Top Contributing Factors",
            top_n=10,
        )

    left, right = st.columns(2)

    with left:
        value_counts_chart(filtered_df, "borough", "Crashes By Borough", top_n=10)

    with right:
        value_counts_chart(
            filtered_df,
            "vehicle_type_code1",
            "Top Vehicle Types",
            top_n=10,
        )

with tab_location:
    st.subheader("Crash Map")

    if {"latitude", "longitude"}.issubset(filtered_df.columns):
        map_df = filtered_df[["latitude", "longitude"]].dropna()
        map_df = map_df[
            map_df["latitude"].between(-90, 90)
            & map_df["longitude"].between(-180, 180)
        ]

        if map_df.empty:
            st.info("No valid latitude/longitude values for the current filters.")
        else:
            st.map(map_df, latitude="latitude", longitude="longitude", size=8)
    else:
        st.info("This dataset does not include latitude and longitude columns.")

with tab_details:
    st.subheader("Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv,
        file_name="filtered_accidents.csv",
        mime="text/csv",
    )
