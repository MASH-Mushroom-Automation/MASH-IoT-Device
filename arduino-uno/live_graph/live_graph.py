import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import re
import time
import threading
from datetime import datetime, timedelta
import numpy as np
import msvcrt  # For Windows keyboard input

# Serial port configuration (change COM port as needed)
SERIAL_PORT = 'COM12'  # Change this to your Arduino's COM port
BAUD_RATE = 9600

# Presentation mode settings
PRESENTATION_MODE = True  # Set to True for presentation mode
MAX_DATA_POINTS = 100  # Limit data points for better performance

# Mushroom growing modes
MUSHROOM_MODES = {
    'SPAWNING': {'min_co2': 10000, 'max_co2': None, 'color': 'red'},
    'FRUITING': {'min_co2': 500, 'max_co2': 800, 'color': 'green'}
}

current_mode = 'SPAWNING'  # Default mode
alert_active = False

# Mode switching variables
mode_switch_pending = False
new_mode = None
ser = None  # Global serial connection

# Notifications system
notifications = []
max_notifications = 10  # Keep last 10 notifications

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
    global start_datetime, current_mode, ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        start_datetime = datetime.now()
        print(f"Session started at: {start_datetime.strftime('%Y-%m-%d %I:%M:%S %p')}")
        print("Commands: 's' for Spawning mode, 'f' for Fruiting mode")
        
        # Send initial mode to Arduino
        time.sleep(2)  # Wait for Arduino to be ready
        send_mode_to_arduino(current_mode)
        add_notification(f"System started in {current_mode} mode", "info")
        
        start_time = time.time()
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                # Check for mode switching commands
                if line == 's':
                    current_mode = 'SPAWNING'
                    print("Switched to SPAWNING mode (CO2 > 10,000 ppm)")
                    continue
                elif line == 'f':
                    current_mode = 'FRUITING'
                    print("Switched to FRUITING mode (CO2 500-800 ppm)")
                    continue
                
                # Try to parse sensor data with multiple patterns
                match = re.match(pattern, line)
                if not match:
                    # Try alternative pattern for different output formats
                    alt_pattern = r"CO2:\s*(\d+)\s*ppm.*Temperature:\s*([0-9.]+)\s*°C.*Humidity:\s*([0-9.]+)\s*%"
                    match = re.match(alt_pattern, line)
                
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
                        
                        # Limit data points for better performance in presentation mode
                        if PRESENTATION_MODE and len(times) > MAX_DATA_POINTS:
                            times.pop(0)
                            co2_values.pop(0)
                            temp_values.pop(0)
                            hum_values.pop(0)
                            
                    print(f"Time: {current_time:.1f}s, CO2: {co2} ppm, Temp: {temp}°C, Hum: {hum}%")
                    
                    # Add notification for significant CO2 changes
                    if len(co2_values) > 1:
                        co2_change = co2 - co2_values[-2] if len(co2_values) > 1 else 0
                        if abs(co2_change) > 100:  # Significant change
                            add_notification(f"CO2 changed by {co2_change:+.0f} ppm (now {co2} ppm)", "warning")
                else:
                    # Print any other output for debugging
                    if line and not line.startswith("=") and not line.startswith("Waiting"):
                        print(f"Arduino: {line}")
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

def add_notification(message, notification_type="info"):
    """Add a notification to the recent notifications list"""
    global notifications
    timestamp = datetime.now().strftime("%H:%M:%S")
    notification = {
        'time': timestamp,
        'message': message,
        'type': notification_type  # 'info', 'warning', 'alert', 'success'
    }
    notifications.append(notification)
    
    # Keep only the most recent notifications
    if len(notifications) > max_notifications:
        notifications.pop(0)

def check_co2_alert(co2_value):
    """Check if CO2 level triggers an alert based on current mode"""
    global alert_active
    
    mode_config = MUSHROOM_MODES[current_mode]
    should_alert = False
    alert_message = ""
    
    if current_mode == 'SPAWNING':
        if co2_value < mode_config['min_co2']:
            should_alert = True
            alert_message = f"SPAWNING ALERT: CO2 too low! Need > {mode_config['min_co2']} ppm"
    elif current_mode == 'FRUITING':
        if co2_value < mode_config['min_co2']:
            should_alert = True
            alert_message = f"FRUITING ALERT: CO2 too low! Need {mode_config['min_co2']}-{mode_config['max_co2']} ppm"
        elif co2_value > mode_config['max_co2']:
            should_alert = True
            alert_message = f"FRUITING ALERT: CO2 too high! Need {mode_config['min_co2']}-{mode_config['max_co2']} ppm"
    
    # Add notification if alert status changed
    if should_alert and not alert_active:
        add_notification(alert_message, "alert")
    elif not should_alert and alert_active:
        add_notification(f"CO2 levels back to normal for {current_mode} mode", "success")
    
    alert_active = should_alert
    return should_alert, alert_message

def send_mode_to_arduino(mode):
    """Send mode command to Arduino"""
    global ser
    if ser and ser.is_open:
        try:
            if mode == 'SPAWNING':
                ser.write(b's\n')
            elif mode == 'FRUITING':
                ser.write(b'f\n')
            print(f"📤 Sent '{mode}' command to Arduino")
        except Exception as e:
            print(f"❌ Error sending command to Arduino: {e}")

def check_keyboard_input():
    """Check for keyboard input to change modes"""
    global current_mode
    if msvcrt.kbhit():
        key = msvcrt.getch().decode('utf-8').lower()
        if key == 's':
            current_mode = 'SPAWNING'
            send_mode_to_arduino('SPAWNING')
            add_notification("Switched to SPAWNING mode (CO2 > 10,000 ppm)", "info")
            print(f"\n🔄 Switched to SPAWNING mode (CO2 > 10,000 ppm)")
        elif key == 'f':
            current_mode = 'FRUITING'
            send_mode_to_arduino('FRUITING')
            add_notification("Switched to FRUITING mode (CO2 500-800 ppm)", "info")
            print(f"\n🔄 Switched to FRUITING mode (CO2 500-800 ppm)")
        elif key == 'q':
            print("\n👋 Exiting...")
            sys.exit(0)

def update_plot(frame):
    # Check for keyboard input
    check_keyboard_input()
    
    with data_lock:
        if len(times) > 0:
            plt.clf()
            
            # Create grid layout: 3 rows for graphs, 1 for stats, 1 for notifications
            if PRESENTATION_MODE:
                gs = plt.GridSpec(5, 3, height_ratios=[3, 3, 3, 1.2, 1.5], hspace=0.3, wspace=0.2)
            else:
                gs = plt.GridSpec(5, 3, height_ratios=[3, 3, 3, 1.5, 1.5], hspace=0.4, wspace=0.3)
            
            # CO2 plot
            ax1 = plt.subplot(gs[0, :])
            ax1.plot(times, co2_values, 'r-', linewidth=2 if PRESENTATION_MODE else 1.5)
            co2_stats = get_statistics(co2_values)
            
            # Check for alerts
            should_alert, alert_message = check_co2_alert(co2_stats['current'])
            
            # Set dynamic Y-axis limits based on mode and data
            mode_config = MUSHROOM_MODES[current_mode]
            if current_mode == 'SPAWNING':
                # For spawning, use a wider range since we need high CO2
                y_min = 0
                y_max = max(15000, co2_stats['max'] * 1.2)  # At least 15000, or 20% above max data
                ax1.set_ylim(y_min, y_max)
                ax1.axhspan(0, mode_config['min_co2'], color='red', alpha=0.2, label='Spawning Alert Zone')
                ax1.axhspan(mode_config['min_co2'], y_max, color='green', alpha=0.2, label='Spawning OK Zone')
            elif current_mode == 'FRUITING':
                # For fruiting, use a much smaller range for better visibility
                data_min = min(co2_stats['min'], mode_config['min_co2'] - 200)  # 200 ppm below threshold
                data_max = max(co2_stats['max'], mode_config['max_co2'] + 200)  # 200 ppm above threshold
                y_min = max(0, data_min - 100)  # At least 0, with 100 ppm buffer below
                y_max = data_max + 100  # 100 ppm buffer above
                ax1.set_ylim(y_min, y_max)
                ax1.axhspan(y_min, mode_config['min_co2'], color='red', alpha=0.2, label='Too Low for Fruiting')
                ax1.axhspan(mode_config['min_co2'], mode_config['max_co2'], color='green', alpha=0.2, label='Fruiting OK Zone')
                ax1.axhspan(mode_config['max_co2'], y_max, color='red', alpha=0.2, label='Too High for Fruiting')
            
            # Add alert indicator to title
            alert_indicator = " [ALERT!]" if should_alert else " [OK]"
            title_fontsize = 12 if PRESENTATION_MODE else 10
            ax1.set_title(f'CO2 Levels - {current_mode} Mode{alert_indicator} | Current: {co2_stats["current"]:.0f} ppm | Avg: {co2_stats["avg"]:.0f} ppm', 
                         fontsize=title_fontsize, fontweight='bold' if PRESENTATION_MODE else 'normal',
                         color='red' if should_alert else 'black')
            ax1.set_ylabel('CO2 (ppm)', fontsize=11 if PRESENTATION_MODE else 10)
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=co2_stats['avg'], color='r', linestyle='--', alpha=0.7, linewidth=2, label=f'Avg: {co2_stats["avg"]:.0f}')
            
            # Temperature plot
            ax2 = plt.subplot(gs[1, :])
            ax2.plot(times, temp_values, 'b-', linewidth=2 if PRESENTATION_MODE else 1.5)
            temp_stats = get_statistics(temp_values)
            
            # Add comfort zone indicators
            ax2.axhspan(18, 24, color='green', alpha=0.1, label='Comfort Zone')
            ax2.axhspan(24, 28, color='yellow', alpha=0.1, label='Warm')
            ax2.axhspan(28, 35, color='orange', alpha=0.1, label='Hot')
            
            ax2.set_title(f'Temperature | Current: {temp_stats["current"]:.1f}°C | Avg: {temp_stats["avg"]:.1f}°C', fontsize=title_fontsize, fontweight='bold' if PRESENTATION_MODE else 'normal')
            ax2.set_ylabel('Temp (°C)', fontsize=11 if PRESENTATION_MODE else 10)
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=temp_stats['avg'], color='b', linestyle='--', alpha=0.7, linewidth=2, label=f'Avg: {temp_stats["avg"]:.1f}')
            
            # Humidity plot
            ax3 = plt.subplot(gs[2, :])
            ax3.plot(times, hum_values, 'g-', linewidth=2 if PRESENTATION_MODE else 1.5)
            hum_stats = get_statistics(hum_values)
            
            # Add humidity comfort zones
            ax3.axhspan(30, 60, color='green', alpha=0.1, label='Comfort Zone')
            ax3.axhspan(60, 80, color='yellow', alpha=0.1, label='High Humidity')
            ax3.axhspan(80, 100, color='orange', alpha=0.1, label='Very High')
            
            ax3.set_title(f'Humidity | Current: {hum_stats["current"]:.1f}% | Avg: {hum_stats["avg"]:.1f}%', fontsize=title_fontsize, fontweight='bold' if PRESENTATION_MODE else 'normal')
            ax3.set_ylabel('Humidity (%)', fontsize=11 if PRESENTATION_MODE else 10)
            ax3.set_xlabel('Time (s)', fontsize=11 if PRESENTATION_MODE else 10)
            ax3.grid(True, alpha=0.3)
            ax3.axhline(y=hum_stats['avg'], color='g', linestyle='--', alpha=0.7, linewidth=2, label=f'Avg: {hum_stats["avg"]:.1f}')
            
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
            
            # Add alert information
            alert_info = ""
            if should_alert:
                alert_info = f"\n[ALERT] {alert_message}"
            
            stats_text = f"""MUSHROOM GROWING MONITOR - {current_mode} MODE
{time_info}
Samples: {len(times)}{alert_info}

CO2: Min={co2_stats['min']:.0f} ppm | Max={co2_stats['max']:.0f} ppm | Avg={co2_stats['avg']:.0f} ppm | Range={co2_stats['max']-co2_stats['min']:.0f} ppm
Temp: Min={temp_stats['min']:.1f}°C | Max={temp_stats['max']:.1f}°C | Avg={temp_stats['avg']:.1f}°C | Range={temp_stats['max']-temp_stats['min']:.1f}°C
Humidity: Min={hum_stats['min']:.1f}% | Max={hum_stats['max']:.1f}% | Avg={hum_stats['avg']:.1f}% | Range={hum_stats['max']-hum_stats['min']:.1f}%"""
            
            # Change background color based on alert status
            bg_color = 'lightcoral' if should_alert else 'wheat'
            ax_stats.text(0.05, 0.5, stats_text, transform=ax_stats.transAxes,
                         fontsize=8, verticalalignment='center', family='monospace',
                         bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.3))
            
            # Notifications panel
            ax_notifications = plt.subplot(gs[4, :])
            ax_notifications.axis('off')
            
            # Format notifications
            if notifications:
                notifications_text = "RECENT NOTIFICATIONS\n"
                for i, notif in enumerate(reversed(notifications[-5:])):  # Show last 5 notifications
                    # Use text symbols instead of emojis for better compatibility
                    if notif['type'] == 'alert':
                        color = 'red'
                        icon = '[ALERT]'
                    elif notif['type'] == 'warning':
                        color = 'orange'
                        icon = '[WARN]'
                    elif notif['type'] == 'success':
                        color = 'green'
                        icon = '[OK]'
                    else:  # info
                        color = 'blue'
                        icon = '[INFO]'
                    
                    notifications_text += f"{icon} [{notif['time']}] {notif['message']}\n"
            else:
                notifications_text = "RECENT NOTIFICATIONS\nNo notifications yet..."
            
            ax_notifications.text(0.05, 0.5, notifications_text, transform=ax_notifications.transAxes,
                                fontsize=7, verticalalignment='center', family='monospace',
                                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

if __name__ == "__main__":
    print("🍄 MASH IoT Device - Mushroom Growing Monitor")
    print("=" * 50)
    print("Commands:")
    print("  's' - Switch to Spawning mode (CO2 > 10,000 ppm)")
    print("  'f' - Switch to Fruiting mode (CO2 500-800 ppm)")
    print("  'q' - Quit application")
    print("=" * 50)
    
    # Start serial reading thread
    serial_thread = threading.Thread(target=read_serial, daemon=True)
    serial_thread.start()

    # Set up the plot
    if PRESENTATION_MODE:
        fig = plt.figure(figsize=(14, 10))
        plt.suptitle('MASH IoT Device - Mushroom Growing Monitor', fontsize=16, fontweight='bold')
    else:
        fig = plt.figure(figsize=(12, 10))
        plt.suptitle('SCD41 Sensor Live Monitoring', fontsize=14, fontweight='bold')
    
    ani = FuncAnimation(fig, update_plot, interval=1000, cache_frame_data=False)  # Update every 1 second

    plt.show()
