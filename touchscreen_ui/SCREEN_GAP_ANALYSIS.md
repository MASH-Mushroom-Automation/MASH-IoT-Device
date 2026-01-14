# Touchscreen UI Gap Analysis

## Existing Implementation Status

### ✅ Implemented Screens
- **Dashboard** (`screens/dashboard.py`) - Sensor monitoring with CO2, Temperature, Humidity cards
- **Controls** (`screens/controls.py`) - Manual actuator toggles
- **Settings** (`screens/settings.py`) - System settings
- **WiFi Setup** (`screens/wifi_setup.py`) - Network configuration

### ✅ Existing Widgets
- **SensorCard** (`widgets/sensor_card.py`) - Display sensor readings with status
- **StatusBar** (`widgets/status_bar.py`) - Top bar with connectivity status
- **ToggleButton** (`widgets/toggle_button.py`) - Actuator control buttons

### ✅ Infrastructure
- **API Client** (`api_client.py`) - Flask backend communication
- **MQTT Client** (`mqtt_client.py`) - Real-time updates
- **Config** (`config.py`) - Responsive design config
- **Main App** (`main.py`) - Screen manager and app lifecycle

---

## 🔴 Missing Features (Per Design Specs)

### Priority 1: Core Navigation & Boot Flow

#### 1. Splash Screen (Missing)
**Design Spec**: [gui_v2/GUI_PAGES.md#splash-screen-boot](../../gui_v2/GUI_PAGES.md)
- **Required**: Boot animation with logo fade-in
- **Logic**: Check `isFirstTimeLogin` flag → route to Setup Wizard or Dashboard
- **Assets Needed**: M.A.S.H. Logo SVG/PNG
- **File to Create**: `screens/splash.py`

#### 2. Setup Wizard (Missing)
**Design Spec**: [gui_v2/GUI_V2.md#setup-wizard](../../gui_v2/GUI_V2.md)
- **Step 1**: Welcome message with sustainability intro
- **Step 2**: WiFi configuration (reuse existing `wifi_setup.py` logic)
- **Step 3**: App pairing with QR code
- **Top 60% Layout Rule**: All inputs in top 60% to avoid OSK overlap
- **File to Create**: `screens/setup_wizard.py`
- **Flag Storage**: Store `isFirstTimeLogin` in local JSON config

#### 3. Global Navigation Sidebar (Missing)
**Design Spec**: [gui_v2/GUI_PAGES.md#global-navigation-sidebar](../../gui_v2/GUI_PAGES.md)
- **Position**: Left-hand side, 80px width, fixed
- **Icons** (60x60px):
  - Home (Dashboard)
  - Notifications (Alerts)
  - Brain (AI Insights)
  - Toggles (Manual Actuators)
  - Help (Maintenance)
  - Gear (Settings)
- **File to Create**: `widgets/navigation_sidebar.py`
- **Assets Needed**: 6 icon PNGs at 60x60px

---

### Priority 2: New Content Screens

#### 4. Alerts/Logs Screen (Missing)
**Design Spec**: [gui_v2/GUI_PAGES.md#51-alerts-logs](../../gui_v2/GUI_PAGES.md)
- **Data Source**: `GET /api/logs/alerts` from integrated_server.py
- **Display**: Vertical scrollable list with color-coded severity
  - 🔴 Critical: #F44336 (Red)
  - 🟡 Warning: #FFC107 (Amber)
  - 🟢 Info/AI: #4CAF50 (Green)
- **Action**: "Clear Logs" button (top right)
- **File to Create**: `screens/alerts.py`

#### 5. AI Insights Screen (Missing)
**Design Spec**: [gui_v2/GUI_PAGES.md#52-ai-insights](../../gui_v2/GUI_PAGES.md)
- **Data Source**: `GET /api/automation/history` from RuleBasedController
- **Display**: Large text area with reasoning strings
- **Examples**: "AI Suggestion: Lowering temperature by 2°C to stimulate pinhead formation."
- **Font**: Inter 18sp for readability
- **File to Create**: `screens/ai_insights.py`

#### 6. Help & Maintenance Screen (Missing)
**Design Spec**: [gui_v2/GUI_V2.md#help-maintenance-content](../../gui_v2/GUI_V2.md)
- **Tabs**: [Tutorials] [Maintenance] [Support]
- **Content**: Rich text from design doc
  - Starting a New Batch
  - Calibrating Manual Controls
  - Maintenance Protocols (Humidifier, Fans, Sensors)
  - Troubleshooting & Error Codes
- **File to Create**: `screens/help.py`

---

### Priority 3: Enhanced Features

#### 7. Interactive Tutorial System (Missing)
**Design Spec**: [gui_v2/GUI_V2.md#device-dashboard-main-page](../../gui_v2/GUI_V2.md)
- **Trigger**: `isTutorialDone == false` on first dashboard visit
- **Sequence**:
  1. Highlight Sensor Cards with tooltip
  2. Highlight Actuators with tooltip
  3. Navigate Sub-pages tooltip
  4. Final Call to Action (Help page)
- **Dismiss**: Set `isTutorialDone = true` in local config
- **File to Create**: `widgets/tutorial_overlay.py`

#### 8. Real-time Graphs (Missing)
**Design Spec**: [gui_v2/GUI_V2.md#7-inch-touchscreen-main-gui](../../gui_v2/GUI_V2.md)
- **Data Source**: `GET /api/sensor/history` (30-minute window)
- **Library**: Kivy Garden Graph or matplotlib
- **Charts**: CO2, Temperature, Humidity with threshold lines
- **Toggle**: Switch between card view and graph view on dashboard
- **Enhancement to**: `screens/dashboard.py`

#### 9. Manual Override Timer (Missing)
**Design Spec**: [gui_v2/GUI_PAGES.md#34-manual-controls-actuators](../../gui_v2/GUI_PAGES.md)
- **Logic**: Manual toggles persist for 30 minutes before AI re-engages
- **Display**: Countdown timer on controls screen
- **Implementation**: Backend logic in `RuleBasedController` + GUI timer display
- **Enhancement to**: `screens/controls.py`

---

## ⚠️ Needs Validation

### WiFi Setup Layout (Existing)
**Design Requirement**: Inputs must be in top 60% to avoid OSK overlap
**Current Status**: Unknown - requires testing on Pi 3 with OSK
**Action**: Review `screens/wifi_setup.py` layout positioning

---

## 🔧 Optimizations Needed

### Performance (RPi3 Specific)

#### 1. Kivy GPU Configuration (Missing)
**Design Spec**: [gui_v2/GUI_PAGES.md#41-kivy-configuration-for-rpi3](../../gui_v2/GUI_PAGES.md)
```python
import os
os.environ['KIVY_WINDOW'] = 'egl_rpi'
os.environ['KIVY_BCM_DISPMANX_ID'] = '2'
```
**File to Update**: `main.py` (before Kivy imports)

#### 2. Threading Optimization (Partial)
**Current**: API polling in main thread via `Clock.schedule_interval`
**Needed**: Move API calls to background threads with `threading.Thread`
**Needed**: Use MQTT push instead of HTTP polling for real-time updates
**Files to Update**: `screens/dashboard.py`, `screens/controls.py`

#### 3. Transition Performance (Needs Update)
**Current**: `SlideTransition` in `main.py`
**Design Spec**: Use `FadeTransition(duration=0.2)` for better performance
**File to Update**: `main.py`

#### 4. UI/UX Rules (Needs Validation)
**Design Spec**: [gui_v2/GUI_PAGES.md#5-uiux-golden-rules-for-rpi3](../../gui_v2/GUI_PAGES.md)
- ❓ No transparency (opacity < 1.0 on moving elements)
- ❓ No software shadows (use borders #333333)
- ❓ Pre-rendered icons at exact display size (60x60px)
- ❓ 200ms debounce on toggle switches
**Files to Audit**: All screens and widgets

---

## 📊 Summary Statistics

| Category | Implemented | Missing | Total |
|----------|------------|---------|-------|
| **Screens** | 4 | 5 | 9 |
| **Widgets** | 3 | 2 | 5 |
| **Performance Optimizations** | 1 | 4 | 5 |
| **Total Features** | 8 | 11 | 19 |

**Completion**: ~42% (8/19)

---

## 🎯 Implementation Priority

### Phase 1: Core Navigation (2-3 days)
1. ✅ Splash Screen with routing logic
2. ✅ Setup Wizard (3 steps)
3. ✅ Global Navigation Sidebar

### Phase 2: Content Screens (2-3 days)
4. ✅ Alerts Screen
5. ✅ AI Insights Screen
6. ✅ Help & Maintenance Screen

### Phase 3: Enhancement (2-3 days)
7. ✅ Tutorial Overlay System
8. ✅ Real-time Graphs on Dashboard
9. ✅ Manual Override Timer

### Phase 4: Optimization (1-2 days)
10. ✅ RPi3 GPU Configuration
11. ✅ Threading & MQTT Integration
12. ✅ Performance Tuning & Testing

**Total Estimated Time**: 7-11 days

---

## 🔗 Related Files

- Design Specs: `gui_v2/GUI_V2.md`, `gui_v2/GUI_PAGES.md`
- Backend API: `integrated_server.py`
- Automation: `rule_based_controller.py`
- Data Logging: `data_logger.py`
- Config: `config/device_config.yaml`
- Assets: `touchscreen_ui/assets/` (to be created)
