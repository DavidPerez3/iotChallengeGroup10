from flask import Flask, render_template
from influxdb_client import InfluxDBClient
import pandas as pd
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import pytz
from datetime import datetime

# InfluxDB
INFLUXDB_URL = "http://192.168.247.95:8086"
INFLUXDB_TOKEN = "U-19LssMKH4z6jiDwysJ9jPvfgLenIYRMRsUtfPDalr_HcYm4_5OrQulGEw-5N4FGJFAtzbATPiiL7nwN2p3CA=="
INFLUXDB_ORG = "iot_group_10"
INFLUXDB_BUCKET = "temp&Hum"

# Flask initialization
app = Flask(__name__)

# InfluxDB client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

@app.route('/')
def index():
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -7d)
      |> filter(fn: (r) => r._measurement == "environment_data")
      |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
    '''

    # Execute the query and transform the data into a dataframe
    result = client.query_api().query_data_frame(org=INFLUXDB_ORG, query=query)

    if result.empty:
        return "No hay datos disponibles en la base de datos."

    result["_time"] = pd.to_datetime(result["_time"])
    result = result.rename(columns={"temperature": "Temperatura", "humidity": "Humedad"})

    # Time zone
    madrid_tz = pytz.timezone("Europe/Madrid")
    result["_time"] = result["_time"].dt.tz_convert(madrid_tz)

    # Extract values
    current_data = result.sort_values(by="_time", ascending=False).iloc[0]
    current_time = current_data["_time"]

    # Parse date and time
    formatted_current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    
    current_temp = current_data["Temperatura"]
    current_humidity = current_data["Humedad"]

    # Create graphs
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=result["_time"], y=result["Temperatura"], mode='lines', name='Temperatura'))
    fig_temp.update_layout(title="Temperatura en los últimos 7 días", xaxis_title="Tiempo", yaxis_title="Temperatura (°C)")

    fig_hum = go.Figure()
    fig_hum.add_trace(go.Scatter(x=result["_time"], y=result["Humedad"], mode='lines', name='Humedad'))
    fig_hum.update_layout(title="Humedad en los últimos 7 días", xaxis_title="Tiempo", yaxis_title="Humedad (%)")

    # Convert graphs to JSON
    temp_graph = json.dumps(fig_temp, cls=PlotlyJSONEncoder)
    hum_graph = json.dumps(fig_hum, cls=PlotlyJSONEncoder)

    # Render the template
    return render_template("index.html", 
                           current_time=formatted_current_time, 
                           current_temp=current_temp, 
                           current_humidity=current_humidity,
                           temp_graph=temp_graph, 
                           hum_graph=hum_graph)


@app.route('/graphs')
def graphs():
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -7d)
      |> filter(fn: (r) => r._measurement == "environment_data")
      |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
    '''
    
    # Execute the query and transform the data into a dataframe
    result = client.query_api().query_data_frame(org=INFLUXDB_ORG, query=query)

    if result.empty:
        return "No data found."

    result["_time"] = pd.to_datetime(result["_time"])
    result = result.rename(columns={"temperature": "Temperatura", "humidity": "Humedad"})

    # Convert the time zone
    madrid_tz = pytz.timezone("Europe/Madrid")
    result["_time"] = result["_time"].dt.tz_convert(madrid_tz)

    # Create graphs
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(x=result["_time"], y=result["Temperatura"], mode='lines', name='Temperatura'))
    fig_temp.update_layout(title="Temperature in last 7 days", xaxis_title="Time", yaxis_title="Temperature (°C)")

    fig_hum = go.Figure()
    fig_hum.add_trace(go.Scatter(x=result["_time"], y=result["Humedad"], mode='lines', name='Humedad'))
    fig_hum.update_layout(title="Humidity in last 7 days", xaxis_title="Time", yaxis_title="Humidity (%)")

    # Convert graphs to JSON
    temp_graph = json.dumps(fig_temp, cls=PlotlyJSONEncoder)
    hum_graph = json.dumps(fig_hum, cls=PlotlyJSONEncoder)

    return render_template("graphs.html", temp_graph=temp_graph, hum_graph=hum_graph)

if __name__ == '__main__':
    app.run(debug=True)
