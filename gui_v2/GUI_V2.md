M.A.S.H. IoT Device GUI Brainstorming

1. Splash Screen

The gateway of the device boot sequence.

Visuals:

Centered M.A.S.H. Logo.

Minimalist progress bar at the bottom-center.

Logic:

If _isFirstTimeLogin == true: Redirect to Setup Wizard.

If _isFirstTimeLogin == false: Redirect to Device Dashboard.

2. Setup Wizard (Device Onboarding)

Layout: Top-Half (Interactive UI) | Bottom-Half (Logo / OSK Safe Zone).

Step 1: IoT Overview (Onboarding)

Top-Half: "Welcome to M.A.S.H. Grow. Your intelligent partner in sustainable oyster mushroom cultivation."

Bottom-Half: M.A.S.H. Logo (Keyboard safe zone).

Step 2: WiFi Configuration

Top-Half: List of available 2.4GHz networks. Selecting a network prompts a password field.

Bottom-Half: Logo (Safe zone for the Raspberry Pi OSK to pop up without blocking the input field).

Modal: Shows "Connecting..." followed by a Success/Failure modal.

Step 3: App Link (Pairing)

Top-Half: "Sync with M.A.S.H. Grower. Scan the QR code below to download the mobile app and link your device."

Action Button: "Continue".

Final Action: Upon completion, flag _isFirstTimeLogin = false and redirect to Dashboard.

3. Device Dashboard (Main Page)

Real-time monitoring hub with built-in training logic.

Tutorial State Logic:

Triggered if _isTutorialDone == false.

Sequence:

Highlight Sensor Cards: Tooltip: "Monitor live levels of CO2, Temperature, and Humidity. Aim for the 'Optimal' indicator."

Highlight Actuators: Tooltip: "Toggle your fans and humidifier manually if the AI suggests an override."

Navigate Sub-pages: Tooltip: "Browse through Alerts for history, AI for growth insights, and Settings for device config."

Final Call to Action: Tooltip: "Need more help? Visit the Help page for maintenance tips and tutorials."

Completion: Flag _isTutorialDone = true.

Main View (Home):

Sensor Cards: * CO2 (PPM)

Temperature (°C)

Humidity (%)

System Health: Simple status indicator (Online/Offline).

4. Sub-Pages

Alerts: Vertical list of the most recent notifications.

AI: Text-based predictive insights.

Actuators: Control panel for manual toggling:

Exhaust Fan (Toggle)

Blower Fan (Toggle)

Humidifier (Toggle)

LED Lights (Toggle)

Help: Scrollable section for Tutorials, Maintenance Tips, and Support.

Settings: WiFi reset, screen brightness, system updates, and reboot/shutdown.

5. Detailed UI Copy & Content

5.1 Alert Message Definitions

Standardized strings for the Alerts sub-page:

Critical: "CRITICAL: High CO2 detected (>1200ppm). Fans activated."

Warning: "WARNING: Humidity below 75%. Humidifier suggested."

Info: "SYSTEM: Mobile App successfully synchronized."

Maintenance: "SERVICE: Please check water reservoir for the humidifier."

5.2 AI Insights Examples

Predictive suggestions based on mushroom growth stages:

Fruiting Prep: "AI Suggestion: Lowering temperature by 2°C to stimulate pinhead formation."

Air Quality: "AI Insight: CO2 rising slowly. Increasing blower pulse frequency to maintain air exchange."

Stress Alert: "AI Observation: Humidity fluctuations detected. Check for chamber leaks."

5.3 Help & Maintenance Content

Detailed Tutorials:

Starting a New Batch: 1. Fully harvest the previous batch and remove all spent substrate.

2. Clean the chamber walls and floor with 70% isopropyl alcohol.

3. Load new sterilized fruiting bags (ensure they are cool to the touch).

4. Reset the "Batch Start" date in your Mobile App or in the Inventory Page in the Device to restart the AI growth tracking.

Calibrating Manual Controls: - If the chamber feels too dry despite a 90% reading, manually pulse the Humidifier for 5 minutes.

If the chamber smells "stuffy," run the Exhaust Fan for 2 minutes regardless of CO2 readings.

Device Relocation: - Always shutdown via Settings before unplugging.

Keep the device away from direct sunlight to prevent "false" high-temperature readings from the sensors.

Maintenance Protocols:

Humidifier System: - Use ONLY distilled or purified water to prevent mineral buildup on the ultrasonic mist maker.

Clean the water tank weekly with a mild vinegar solution to prevent bacterial slime.

Air Filtration & Fans: - Inspect the Blower Fan intake daily for dust or stray mushroom spores.

Vacuum or replace the intake filter every 30 days to ensure high-volume air exchange.

Sensor Hygiene (SCD41): - DO NOT use liquids on sensors. Use a camera blower or a very soft, dry brush to remove dust from the vents.

Ensure the sensor module is positioned at the center-height of the chamber for the most accurate average reading.

Advanced Grower Insights (The "Science"):

The CO2 Threshold: During the "Pinning" stage, CO2 must stay below 800ppm. High CO2 at this stage results in "Long Stems" and "Small Caps."

Evaporative Cooling: If the temperature is too high, pulsing the humidifier while running the exhaust fan can help drop the temp by 1-2°C through evaporation.

Darkness Period: White Oyster mycelium colonizes faster in total darkness. Minimize opening the chamber during the first 7 days.

Troubleshooting & Error Codes:

Code 404 (No Sensor): The Raspberry Pi cannot detect the I2C bus. Check the 4-pin connector on the M5Stack sensor unit.

Code 503 (Cloud Offline): The device is connected to WiFi but cannot reach the NestJS server. Check your ISP or server status.

Laggy Interface: If the screen becomes slow, clear the "Alerts" history in Settings to free up local SQLite memory.

Unstable Humidity: Check if the Humidifier "wicks" or atomizing sheet is clogged. Replace the atomizer disc if mist production is weak.

Support & Documentation:

Research Team: UCC Caloocan BSCS 4B - Project M.A.S.H.

Documentation: Scan the QR code in the "About" section to view the full IMRAD documentation and hardware schematics.

Technical Lead: Contact via the project's Discord/GitHub for firmware bug reports.

6. Hardware Component List (System Architecture)

1. Control Hierarchy (Pi 3B & Arduino Uno)

Raspberry Pi 3B (The Brain):

Task: Runs the Python-based GUI, manages the SCD41 (I2C), logs data to a database, and calculates target setpoints (e.g., "AI" logic for growth phases).

Comm: Sends high-level commands to Arduino via Serial (USB) or I2C (e.g., SET_HUMIDITY:95).

Arduino Uno (The Brawn):

Task: Real-time relay switching, DHT22 reading, and hardware safety interrupts.

Advantage: If the Pi's GUI freezes, the Arduino continues running the "last known good" environment settings to prevent crop loss.

2. Sensor Integration (SCD41 & DHT22)

M5Stack SCD41 (Primary):

Interface: I2C (Address 0x62).

Logic: Requires a "warm-up" period. Should be sampled every 5 seconds.

Critical Note: CO2 readings are barometrically pressure-dependent. Use the RPi to fetch local weather pressure and calibrate the SCD41 for maximum accuracy.

DHT22 (Redundancy):

Interface: Digital Pin on Arduino.

Logic: Used to "sanity check" the SCD41. If the SCD41 reads 100% RH but the DHT22 reads 40%, the system should trigger a "Sensor Failure" alert on the LCD.

3. Actuator Control Logic

3.1 12V Blower (Circulation)

Function: Moves air internally to prevent "pockets" of high CO2 or stagnant humidity.

Logic: Should run at a low duty cycle (PWM) constantly, or ramp up to 100% whenever the Mist Maker is active to carry the fog.

3.2 12V Exhaust Fan (CO2 Management)

Trigger: CO2 > 800ppm (adjustable).

Interlock: When Exhaust is ON, the Mist Maker should be OFF (to prevent sucking out expensive humidity) unless RH drops below 70%.

3.3 Humidity Control (Alternative Options)

Option A: 48V 10-Head Ultrasonic Mist Maker (Industrial)

Specs: 7KG / H output. 48V @ ~5A.

Best For: Large chambers or rapid humidity spikes.

Logic: Requires heavy-duty relays and aggressive pulsing to avoid overshooting 95%.

Option B: DC5V Four-Spray Humidifier Module (Prototyping/Small Scale)

Specs: 5V (Type-C), 6W, 108KHZ frequency.

Driver Current: 300mA (requires 2A source).

Logic: Much gentler output. Can be run for longer durations.

Integration: Can be powered via the MB102 5V rail (if sourced by 2A+) or a separate USB-C cable controlled by a relay or MOSFET.

3.4 LED Light Strip

Logic: 12/12 or 9/15 Light cycle.

Dimming: Use PWM from the Arduino to simulate sunrise/sunset, reducing "thermal shock" to the organisms.

4. Modules & Power Distribution

4-Channel Relay Module:

Wiring: Use "Active Low" triggering.

Isolation: If using the 48V Mist Maker, keep high-voltage lines physically separated from the 5V sensor lines to prevent EMI.

MB102 & 9V 2A Adapter:

Load Balancing: The 9V adapter powers the Arduino and the MB102.

Note: If using the 5V Four-Spray Module, ensure the MB102 power source is at least 2A, as the module alone draws significant current for the 5V rail.

RPi Power: The Raspberry Pi MUST have its own dedicated 5V 3A supply via the Micro-USB port.

5. Display Strategy

7-inch Touchscreen (Main GUI):

Framework: Kivy or PyQt5.

Visuals: Real-time graphs for Humidity/CO2 and toggle buttons for Manual/Auto mode.

20x4 I2C LCD (Exterior Status):

Row 1: T: 24.5C H: 94.2%

Row 2: CO2: 650ppm

Row 3: MIST: ACTIVE | FAN: ON

Row 4: SYSTEM: NOMINAL

6. Summary of Consumption (Estimated)

Industrial Mode (48V): High power, low duty cycle. 5L-15L water/day.

Prototyping Mode (5V): Low power, high duty cycle. Ideal for desktop-sized fruiting chambers.

7. Visual Design Guidelines (Minimalist)

Theme: Dark Mode (#121212) for RPi3 performance and farm environments.

Typography: Sans-serif (Inter/Roboto), high legibility, single weight.

Layout Rule: All interactive elements for setup must stay in the top 50% of the viewport.

Interaction: Large touch targets (min 50px height) to prevent mis-taps on the small touchscreen.