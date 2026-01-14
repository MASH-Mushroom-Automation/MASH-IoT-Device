

M.A.S.H. IoT Device GUI Design Specifications

1. Physical Environment Constraints

Display: 7-inch Official Raspberry Pi Touchscreen (800x480 resolution).

Platform: Raspberry Pi 3B (Quad-core 1.2GHz, 1GB RAM).

Usage Context: High-humidity mushroom farm environment. Users may have wet or gloved hands.

2. Visual Language & Branding

Color Palette:

Background: #121212 (Deep Charcoal - reduces glare and saves power).

Primary: #4CAF50 (Growth Green - used for "Optimal" states).

Warning: #FFC107 (Amber - used for "Sub-optimal" states).

Critical: #F44336 (Red - used for sensor failures or high CO2).

Surface: #1E1E1E (Slightly lighter grey for cards and containers).

Typography: Roboto or Inter (Sans-Serif).

Header: 24sp (Bold).

Sub-header: 18sp.

Body: 14sp.

3. Page Architecture

3.1 Splash Screen (Boot)

Design: Full-screen background #121212. Centered SVG Logo.

Animation: Simple opacity fade (In: 1s, Wait: 2s).

Performance Note: Pre-load heavy assets (icons/fonts) during this phase.

3.2 Setup Wizard

Split Screen Pattern:

Top 60%: Active interaction (WiFi List, QR Code, Text).

Bottom 40%: Branding / Empty Space.

Reasoning: When the Raspberry Pi OSK (On-Screen Keyboard) triggers, it slides from the bottom. Keeping inputs in the top 60% prevents the keyboard from hiding what the user is typing.

3.3 Dashboard (The Hub)

Layout: 3-Column Grid for Metrics.

Metric Cards: Large digital readouts (CO2, Temp, Hum).

Status Badges: Small "Optimal" or "Check" text under each number.

Sidebar Navigation: Vertical bar on the left (Icons only: Home, Alerts, AI, Manual, Settings). Icons are 60x60px.

3.4 Manual Controls (Actuators)

Toggle Switch Design: Large physical-style toggles.

Safety Logic: Manual overrides persist for 30 minutes before the AI re-engages to prevent user error from killing the crop.

4. Developer Implementation Guidelines (Dev-Ready)

4.1 Kivy Configuration for RPi3

To ensure smooth 60FPS on the Pi 3B, developers must set the following environment variables before importing Kivy:

import os
os.environ['KIVY_WINDOW'] = 'egl_rpi'  # Optimize for Broadcom GPU
os.environ['KIVY_BCM_DISPMANX_ID'] = '2' # Match LCD layer


4.2 State Management Strategy

Use a Singleton "DataStore" class with Kivy Observable properties. This allows the UI to automatically update when background sensor threads (SCD41/Serial) receive new data.

Threads: Run Serial/I2C polling in a separate threading.Thread.

Bridge: Use Clock.schedule_once to push sensor data from the background thread to the Kivy main thread safely.

4.3 Standardized UI Component Patterns

To keep the codebase clean, follow these component patterns:

Touch Targets: Minimum size_hint_y: None and height: '80dp' for all interactive buttons.

Debouncing: Implement a 200ms debounce on all toggle switches to prevent the Relay module from "chattering" due to accidental double-taps.

Hardware Abstraction: Create an ActuatorManager class that abstracts Serial commands (e.g., manager.toggle_fan(True) sends FAN_ON\n to Arduino).

5. UI/UX "Golden Rules" for RPi3

No Transparency: Avoid opacity < 1.0 on moving elements; it kills the Pi 3 frame rate.

Shadows: Do not use software shadows. Use simple borders (#333333) to separate layers.

Raster Images: Keep images exactly at the size they will be displayed (no 4K assets scaled down).

Feedback: Every button press must have a visual "Active" state (brief color change) so the user knows the touch was registered.

M.A.S.H. Detailed Page Architecture

This document serves as the high-fidelity blueprint for developers to implement the Kivy GUI, ensuring optimal performance on the Raspberry Pi 3 and a seamless 7" touchscreen experience.

1. Global Navigation Sidebar

Position: Left-hand side (Fixed).

Dimensions: 80px width (Approx 10% of screen).

Design: Vertical icon-only bar.

Icons:

Home: Dashboard View.

Notifications: Alerts/Logs.

Brain: AI Insights.

Toggles: Manual Actuators.

Help: Maintenance/Tutorials.

Gear: System Settings.

2. Splash Screen (Boot)

Visuals:

Background: #121212.

Center: Large white M.A.S.H. Logo (SVG).

Bottom Center: Subtle "Loading..." text in Roboto 14sp.

Logic:

Initialize I2C Bus (SCD41) and Serial (Arduino).

Check for config.json presence.

Branch: * If isFirstTimeLogin == true $\rightarrow$ Transition to Setup Wizard.

Else $\rightarrow$ Transition to Dashboard.

3. Setup Wizard (3-Step Onboarding)

Layout Rule: All interactive inputs must reside in the Top 60% (288px height) of the screen to clear the On-Screen Keyboard.

3.1 Step 1: Welcome

Top-Half: Large header "Welcome to M.A.S.H." with two lines of body text regarding oyster mushroom sustainability.

Bottom-Half: "Next" button (Primary Green, 80px height).

3.2 Step 2: WiFi Config

Top-Half: Scrollable list of SSID strings. Selecting one opens a text input field at the very top.

Logic: Clicking input triggers the OSK. Because the input is in the top 20%, the user can see what they type above the keyboard.

Validation: Spinner animation (Max 15s) $\rightarrow$ Success/Fail Modal.

3.3 Step 3: Mobile Sync

Top-Half: Instructions + Large QR Code (Generated using device UUID).

Bottom-Half: "Complete Setup" button. Sets isFirstTimeLogin = false.

4. Main Dashboard (The Hub)

Layout: 3-Column Grid + Status Footer.

Metric Cards (CO2, Temp, Hum):

Large numeric readout centered in card.

Small "Badge" at the bottom of the card:

Green: "OPTIMAL"

Amber: "SUB-OPTIMAL"

Red: "CRITICAL"

Interactive Tutorial (First Run Only):

Overlay dimming with high-contrast tooltips pointing to the Sidebar and Metric Cards.

Dismiss button in the bottom right.

5. Sub-Pages (Main Content)

5.1 Alerts (Logs)

Design: Vertical scrollable list of high-contrast labels.

Color Coding: * Critical issues in #F44336 (Red).

AI suggestions in #4CAF50 (Green).

Action: "Clear Logs" button in the Top Right.

5.2 AI Insights

Visuals: Large text area using Inter 18sp for readability.

Content: Dynamic strings generated from current sensor data trends (e.g., "Mushroom caps appear small? CO2 levels have been high for 4 hours. Increasing fan speed.").

5.3 Manual Actuators (The Control Room)

Design: 2x2 Grid of Large Toggle Switches.

Components:

Exhaust Fan: Toggle (On/Off).

Blower Fan: Toggle (On/Off).

Mist Maker: Toggle (On/Off).

LED Lights: Slider (0-100% PWM).

Logic: Manual toggles trigger a 30-minute "Override Timer." After 30 minutes, the system reverts to AI Auto-Mode to prevent human error.

5.4 Help & Maintenance

Design: Tabbed view.

Tabs: [Tutorials] [Maintenance] [Support].

Content: Rich text with bullet points. Maintenance section highlights the use of Distilled Water Only for the Mist Maker.

5.5 Settings

Options:

Screen Brightness (Slider).

WiFi Reset (Button).

System Update (Button).

System Controls: Reboot / Shutdown (Red buttons with "Confirm" modal).

6. Performance Optimization for RPi3

Scene Transitions: Use FadeTransition with a duration of 0.2s. Complex slide animations will stutter on the Pi 3B.

Texture Management: All icons should be pre-rendered as PNGs at the exact display size (e.g., 60x60px) to avoid real-time scaling overhead.

Sensor Updates: Update dashboard numbers every 2 seconds via Clock.schedule_interval. Faster updates cause unnecessary CPU spikes.