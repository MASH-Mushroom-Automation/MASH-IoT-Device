# Plan: GUI Implementation for MASH IoT Device

The MASH IoT Device already has a robust Flask backend with sensor reading, actuator control, automation logic, and data logging. A Kivy-based touchscreen UI exists with basic screens (dashboard, controls, WiFi setup, settings). The plan focuses on **expanding and polishing the GUI** to match the design specifications in [gui_v2/GUI_V2.md](gui_v2/GUI_V2.md) and [gui_v2/GUI_PAGES.md](gui_v2/GUI_PAGES.md), while **reusing all existing backend logic** from [integrated_server.py](integrated_server.py) and supporting modules.

## Steps

1. **Audit and refactor existing Kivy UI** - Review [touchscreen_ui/](touchscreen_ui/) directory, identify gaps against design specs (splash screen, setup wizard, tutorial system, AI insights page, alerts center, help/maintenance pages), and create a screen mapping document linking design specs to implementation files.

2. **Implement missing core screens** - Create [touchscreen_ui/screens/splash.py](touchscreen_ui/screens/splash.py) with boot logic checking `isFirstTimeLogin` flag, [touchscreen_ui/screens/setup_wizard.py](touchscreen_ui/screens/setup_wizard.py) with 3-step onboarding (welcome, WiFi, app pairing), [touchscreen_ui/screens/alerts.py](touchscreen_ui/screens/alerts.py) displaying [DataLogger.get_alerts()](data_logger.py) with color-coded severity, [touchscreen_ui/screens/ai_insights.py](touchscreen_ui/screens/ai_insights.py) showing [RuleBasedController.get_decision_history()](rule_based_controller.py) reasoning, and [touchscreen_ui/screens/help.py](touchscreen_ui/screens/help.py) with tutorials/maintenance content from design docs.

3. **Add interactive tutorial system** - Implement overlay tutorial in [touchscreen_ui/widgets/tutorial_overlay.py](touchscreen_ui/widgets/tutorial_overlay.py) triggered by `isTutorialDone` flag, create sequential tooltips highlighting sensor cards → actuators → navigation → help page as specified in [gui_v2/GUI_V2.md](gui_v2/GUI_V2.md#device-dashboard-main-page), and store tutorial completion state in SQLite or local JSON config.

4. **Enhance dashboard with real-time graphs** - Integrate Kivy Garden Graph or matplotlib to visualize [sensor_data history](integrated_server.py) from `READING_HISTORY` deque or `GET /api/sensor/history`, create 30-minute rolling graphs for CO2/Temperature/Humidity with threshold lines from [device_config.yaml](config/device_config.yaml), and add toggle between numeric cards view and graph view.

5. **Optimize threading and state management** - Ensure Kivy main thread only handles UI updates, move all API calls from [touchscreen_ui/api_client.py](touchscreen_ui/api_client.py) to background threads with `threading.Thread`, implement MQTT-based real-time updates using [touchscreen_ui/mqtt_client.py](touchscreen_ui/mqtt_client.py) to replace polling on dashboard/controls screens, and use Kivy `ObjectProperty` and `Clock.schedule_once` for safe cross-thread UI updates.

6. **Apply performance optimizations for RPi3** - Set `KIVY_WINDOW='egl_rpi'` and `KIVY_BCM_DISPMANX_ID='2'` in [touchscreen_ui/main.py](touchscreen_ui/main.py) initialization, disable transparency and shadows per [gui_v2/GUI_PAGES.md](gui_v2/GUI_PAGES.md#ui-ux-golden-rules) guidelines, pre-render all icons at exact display size (60x60px), limit dashboard updates to 2-second intervals, and use `FadeTransition(duration=0.2)` for all screen changes.

## Further Considerations

1. **WiFi keyboard positioning conflict** - Design specs require inputs in top 60% of screen to avoid Raspberry Pi OSK overlap. Should we validate existing [touchscreen_ui/screens/wifi_setup.py](touchscreen_ui/screens/wifi_setup.py) layout against this requirement, or accept current implementation?

2. **Historical data export feature** - Users may want CSV exports of sensor logs. Add export button in settings screen calling `DataLogger.get_sensor_readings(hours=24*7)` and writing to USB drive, or defer as future enhancement?

3. **Manual override timeout safety** - Design specifies 30-minute manual control timeout before AI re-engages. Should this be implemented in GUI timer + visual countdown, or as backend logic in [RuleBasedController](rule_based_controller.py) tracking last manual interaction timestamp?
