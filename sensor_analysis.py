# === Portfolio: Engineering Sensor Data Analysis ===
# This script:
# 1) Uploads an Excel file with sensor data
# 2) Reads and validates the data
# 3) Generates stats + exports a summary CSV
# 4) Creates 3 time-series plots (Temp, Pressure, Flow) and saves them as PNG
# 5) Adds moving average + anomaly plot for temperature
# 6) Exports a short engineering summary text file
# 7) Downloads all generated outputs

import pandas as pd
import matplotlib.pyplot as plt
from google.colab import files

# -----------------------------
# 1) Upload input file
# -----------------------------
print("Upload your Excel file (sensor_measurements.xlsx)")
uploaded = files.upload()

# If user uploaded with a different filename, pick the first uploaded file:
input_filename = list(uploaded.keys())[0]
print("Using file:", input_filename)

# -----------------------------
# 2) Read and validate data
# -----------------------------
df = pd.read_excel(input_filename)

required_cols = ["time_s", "temperature_C", "pressure_bar", "flow_lpm"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}\nFound columns: {list(df.columns)}")

# Sort by time just in case
df = df.sort_values("time_s").reset_index(drop=True)

print("Rows:", len(df))
display(df.head())

# -----------------------------
# 3) Statistics summary (export to CSV)
# -----------------------------
summary = df.describe()
display(summary)
summary.to_csv("summary.csv", index=True)

# -----------------------------
# Standard plot styling
# -----------------------------
def save_timeseries_plot(x, y, title, xlabel, ylabel, out_png):
    """
    Create a clean time-series plot and save as high-res PNG.
    """
    plt.figure(figsize=(8, 4))
    plt.plot(x, y, marker="o")
    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=300)
    plt.show()

# -----------------------------
# 4) Basic plots (Temp / Pressure / Flow)
# -----------------------------
save_timeseries_plot(
    x=df["time_s"],
    y=df["temperature_C"],
    title="Temperature over time",
    xlabel="Time (s)",
    ylabel="Temperature (°C)",
    out_png="temperature_plot.png"
)

save_timeseries_plot(
    x=df["time_s"],
    y=df["pressure_bar"],
    title="Pressure over time",
    xlabel="Time (s)",
    ylabel="Pressure (bar)",
    out_png="pressure_plot.png"
)

save_timeseries_plot(
    x=df["time_s"],
    y=df["flow_lpm"],
    title="Flow over time",
    xlabel="Time (s)",
    ylabel="Flow (L/min)",
    out_png="flow_plot.png"
)

# -----------------------------
# 5) Moving average + anomaly marking (temperature)
# -----------------------------

# Rolling mean (window=5 samples).
window = 5
df["temp_ma"] = df["temperature_C"].rolling(window=window, min_periods=1).mean()

# Simple anomaly rule: points where deviation from moving average is > threshold
# (This is a practical heuristic, not a statistical guarantee.)
threshold_C = 1.5
df["temp_dev"] = (df["temperature_C"] - df["temp_ma"]).abs()
df["temp_anomaly"] = df["temp_dev"] > threshold_C

plt.figure(figsize=(8, 4))
plt.plot(df["time_s"], df["temperature_C"], marker="o", label="Temperature")
plt.plot(df["time_s"], df["temp_ma"], linewidth=2, label=f"Moving average (window={window})")

# Highlight anomalies with a scatter overlay
anoms = df[df["temp_anomaly"]]
plt.scatter(anoms["time_s"], anoms["temperature_C"], s=80, label=f"Anomaly (>{threshold_C}°C dev)")

plt.grid(True)
plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature with Moving Average and Simple Anomaly Detection")
plt.legend()
plt.tight_layout()
plt.savefig("temperature_ma_anomaly.png", dpi=300)
plt.show()

# -----------------------------
# 6) Engineering summary text file
# -----------------------------
report_lines = [
    "Engineering Summary",
    "------------------",
    f"Samples: {len(df)}",
    f"Time range (s): {df['time_s'].min()} to {df['time_s'].max()}",
    "",
    f"Temperature (°C): avg={df['temperature_C'].mean():.2f}, min={df['temperature_C'].min():.2f}, max={df['temperature_C'].max():.2f}",
    f"Pressure (bar):   avg={df['pressure_bar'].mean():.3f}, min={df['pressure_bar'].min():.3f}, max={df['pressure_bar'].max():.3f}",
    f"Flow (L/min):     avg={df['flow_lpm'].mean():.2f}, min={df['flow_lpm'].min()}, max={df['flow_lpm'].max()}",
    "",
    f"Moving average window: {window} samples",
    f"Anomaly rule: abs(temp - moving_average) > {threshold_C} °C",
    f"Detected anomalies: {int(df['temp_anomaly'].sum())}",
]

with open("engineering_summary.txt", "w") as f:
    f.write("\n".join(report_lines))

print("\n".join(report_lines))

# -----------------------------
# 7) Download outputs
# -----------------------------
outputs = [
    "summary.csv",
    "engineering_summary.txt",
    "temperature_plot.png",
    "pressure_plot.png",
    "flow_plot.png",
    "temperature_ma_anomaly.png",
]
for fn in outputs:
    files.download(fn)

print("\nDone. Insert the PNG plots + summary into your Word portfolio case study.")

