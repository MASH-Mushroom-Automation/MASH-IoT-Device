import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import re
import time
import threading
from datetime import datetime, timedelta
import numpy as np

# Serial port configuration (change COM port as needed)
SERIAL_PORT = 'COM12'  # Change this to your Arduino's COM port
BAUD_RATE = 9600

# Data storage
times = []
co2_values = []
temp_values = []
hum_values = []
data_lock = threading.Lock()
start_datetime = None

# Regex to parse the serial output
pattern = r"CO2: (\d+) ppm\tTemperature: ([0-9.]+) °C\tHumidity: ([0-9.]+) %"

def read_serial():
    global start_datetime
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        start_datetime = datetime.now()
        print(f"Session started at: {start_datetime.strftime('%Y-%m-%d %I:%M:%S %p')}")
        start_time = time.time()
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                match = re.match(pattern, line)
                if match:
                    co2 = int(match.group(1))
                    temp = float(match.group(2))
                    hum = float(match.group(3))
                    current_time = time.time() - start_time
                    with data_lock:
                        times.append(current_time)
                        co2_values.append(co2)
                        temp_values.append(temp)
                        hum_values.append(hum)
                    print(f"Time: {current_time:.1f}s, CO2: {co2} ppm, Temp: {temp}°C, Hum: {hum}%")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Stopped reading serial data")

def format_duration(seconds):
    """Convert seconds to readable duration format"""
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    if td.days > 0:
        return f"{td.days}d {hours}h {minutes}m {secs}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def get_statistics(values):
    """Calculate statistics for a data series"""
    if len(values) == 0:
        return {'min': 0, 'max': 0, 'avg': 0, 'current': 0}
    return {
        'min': np.min(values),
        'max': np.max(values),
        'avg': np.mean(values),
        'current': values[-1]
    }

def update_plot(frame):
    with data_lock:
        if len(times) > 0:
            plt.clf()
            
            # Create grid layout: 3 rows for graphs, 1 for stats
            gs = plt.GridSpec(4, 3, height_ratios=[3, 3, 3, 1.5], hspace=0.4, wspace=0.3)
            
            # CO2 plot
            ax1 = plt.subplot(gs[0, :])
            ax1.plot(times, co2_values, 'r-', linewidth=1.5)
            co2_stats = get_statistics(co2_values)
            ax1.set_title(f'CO2 Levels | Current: {co2_stats["current"]:.0f} ppm | Avg: {co2_stats["avg"]:.0f} ppm', fontsize=10)
            ax1.set_ylabel('CO2 (ppm)')
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=co2_stats['avg'], color='r', linestyle='--', alpha=0.5, label=f'Avg: {co2_stats["avg"]:.0f}')
            
            # Temperature plot
            ax2 = plt.subplot(gs[1, :])
            ax2.plot(times, temp_values, 'b-', linewidth=1.5)
            temp_stats = get_statistics(temp_values)
            ax2.set_title(f'Temperature | Current: {temp_stats["current"]:.1f}°C | Avg: {temp_stats["avg"]:.1f}°C', fontsize=10)
            ax2.set_ylabel('Temp (°C)')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=temp_stats['avg'], color='b', linestyle='--', alpha=0.5, label=f'Avg: {temp_stats["avg"]:.1f}')
            
            # Humidity plot
            ax3 = plt.subplot(gs[2, :])
            ax3.plot(times, hum_values, 'g-', linewidth=1.5)
            hum_stats = get_statistics(hum_values)
            ax3.set_title(f'Humidity | Current: {hum_stats["current"]:.1f}% | Avg: {hum_stats["avg"]:.1f}%', fontsize=10)
            ax3.set_ylabel('Humidity (%)')
            ax3.set_xlabel('Time (s)')
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=hum_stats['avg'], color='g', linestyle='--', alpha=0.5, label=f'Avg: {hum_stats["avg"]:.1f}')
            
            # Statistics panel
            ax_stats = plt.subplot(gs[3, :])
            ax_stats.axis('off')
            
            duration = times[-1]
            duration_str = format_duration(duration)
            
            if start_datetime:
                current_time = start_datetime + timedelta(seconds=duration)
                time_info = f"Start: {start_datetime.strftime('%I:%M:%S %p')} | Current: {current_time.strftime('%I:%M:%S %p')} | Duration: {duration_str}"
            else:
                time_info = f"Duration: {duration_str}"
            
            stats_text = f"""SESSION STATISTICS
{time_info}
Samples: {len(times)}

CO2: Min={co2_stats['min']:.0f} ppm | Max={co2_stats['max']:.0f} ppm | Avg={co2_stats['avg']:.0f} ppm | Range={co2_stats['max']-co2_stats['min']:.0f} ppm
Temp: Min={temp_stats['min']:.1f}°C | Max={temp_stats['max']:.1f}°C | Avg={temp_stats['avg']:.1f}°C | Range={temp_stats['max']-temp_stats['min']:.1f}°C
Humidity: Min={hum_stats['min']:.1f}% | Max={hum_stats['max']:.1f}% | Avg={hum_stats['avg']:.1f}% | Range={hum_stats['max']-hum_stats['min']:.1f}%"""
            
            ax_stats.text(0.05, 0.5, stats_text, transform=ax_stats.transAxes,
                         fontsize=8, verticalalignment='center', family='monospace',
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

if __name__ == "__main__":
    # Start serial reading thread
    serial_thread = threading.Thread(target=read_serial, daemon=True)
    serial_thread.start()

    # Set up the plot
    fig = plt.figure(figsize=(12, 10))
    plt.suptitle('SCD41 Sensor Live Monitoring', fontsize=14, fontweight='bold')
    ani = FuncAnimation(fig, update_plot, interval=1000, cache_frame_data=False)  # Update every 1 second

    plt.show()
