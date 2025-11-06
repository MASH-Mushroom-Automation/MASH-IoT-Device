# MASH IoT - AI Automation System Guide

## 🤖 Overview

The AI Automation System provides intelligent, autonomous control of your mushroom growing chamber based on real-time sensor data and pre-trained decision models.

### **Key Features:**
- ✅ **Lightweight**: ~10-20MB RAM usage (perfect for RPi3)
- ✅ **Pre-trained**: Uses statistical analysis, not heavy ML models
- ✅ **Rule-based**: Fast, predictable decisions
- ✅ **Mode-aware**: Different strategies for Spawning vs Fruiting
- ✅ **Manual override**: Can be disabled anytime
- ✅ **Decision logging**: Tracks all AI actions and reasoning

---

## 📊 How It Works

### **1. Data Collection**
The system continuously monitors:
- CO2 levels (ppm)
- Temperature (°C)
- Humidity (%)
- Current mode (Spawning/Fruiting)
- Actuator states

### **2. Decision Making**
Every 10 seconds, the AI:
1. Analyzes current conditions
2. Compares against optimal thresholds
3. Decides which actuators to control
4. Logs reasoning for transparency

### **3. Actuator Control**
The AI can control:
- **Exhaust Fan**: For CO2 management
- **Blower Fan**: For temperature control
- **Humidifier**: For humidity control
- **LED Lights**: (manual control recommended)

---

## 🎯 Automation Rules

### **Spawning Phase** (High CO2 needed)

**CO2 Management:**
- Target: 10,000-12,500 ppm
- If CO2 < 10,000 ppm → Turn OFF exhaust fan (accumulate CO2)
- If CO2 > 20,000 ppm → Turn ON exhaust fan (safety vent)
- Optimal: Keep exhaust fan OFF to maintain high CO2

**Temperature:**
- Target: 21-27°C
- If temp > 27°C → Turn ON blower fan
- If temp < 21°C → Turn OFF blower fan

**Humidity:**
- Target: 85-95%
- If humidity < 85% → Turn ON humidifier
- If humidity > 95% → Turn OFF humidifier

### **Fruiting Phase** (Fresh air needed)

**CO2 Management:**
- Target: 300-1000 ppm
- If CO2 > 1000 ppm → Turn ON exhaust fan
- If CO2 < 300 ppm → Turn OFF exhaust fan
- Optimal: 600 ppm

**Temperature:**
- Target: 18-24°C
- If temp > 24°C → Turn ON blower fan
- If temp < 18°C → Turn OFF blower fan

**Humidity:**
- Target: 85-95%
- If humidity < 85% → Turn ON humidifier
- If humidity > 95% → Turn OFF humidifier

---

## 🚀 Setup & Usage

### **1. Train the Model (Optional)**

If you have collected your own data:

```bash
cd /home/pi/mash_iot
python3 raspberry-pi/train_decision_model.py
```

This will:
- Analyze your `data/training_data.csv`
- Calculate optimal thresholds
- Save model to `models/decision_model.json`

**Note:** The system works with default thresholds if no model is trained.

### **2. Start the Server**

```bash
cd /home/pi/mash_iot
python3 integrated_server.py
```

The AI automation thread starts automatically but is **DISABLED** by default.

### **3. Enable AI Automation**

**Via API:**
```bash
curl -X POST http://raspberrypi.local:5000/api/automation/enable
```

**Via Mobile App:**
- Navigate to Chamber Detail screen
- Toggle "AI Automation" switch to ON

---

## 📡 API Endpoints

### **Get Automation Status**
```http
GET /api/automation/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "enabled": true,
    "model_loaded": "/home/pi/mash_iot/models/decision_model.json",
    "thresholds": {
      "spawning_co2_min": 10000,
      "fruiting_co2_max": 1000,
      ...
    },
    "decisions_made": 42,
    "last_decision": {
      "timestamp": "2025-11-06T07:50:00",
      "mode": "Spawning",
      "actions": {
        "exhaust_fan": false
      },
      "reasoning": ["CO2 optimal (12500ppm) - maintaining accumulation"]
    }
  }
}
```

### **Enable Automation**
```http
POST /api/automation/enable
```

### **Disable Automation**
```http
POST /api/automation/disable
```

### **Get Decision History**
```http
GET /api/automation/history?limit=10
```

---

## 🎮 Mobile App Integration

### **AI Automation Toggle**

Add to Chamber Detail screen:

```dart
// In chamber_detail_screen.dart
Switch(
  value: _aiAutomationEnabled,
  onChanged: (value) async {
    final endpoint = value ? 'enable' : 'disable';
    final success = await _deviceService.post('/api/automation/$endpoint');
    if (success) {
      setState(() => _aiAutomationEnabled = value);
    }
  },
)
```

### **Show AI Status**

Display current AI decisions:

```dart
// Show last AI action
Text('AI: ${lastDecision.reasoning.join(", ")}')
```

---

## 🔍 Monitoring & Debugging

### **Check AI Status**
```bash
curl http://raspberrypi.local:5000/api/automation/status
```

### **View Decision History**
```bash
curl http://raspberrypi.local:5000/api/automation/history?limit=20
```

### **Server Logs**
```bash
# View real-time logs
tail -f /var/log/mash_iot.log

# Look for AI decisions
grep "🤖 AI Action" /var/log/mash_iot.log
```

---

## ⚠️ Safety Features

### **1. Hysteresis**
Prevents rapid on/off cycling:
- CO2: ±500 ppm buffer
- Temperature: ±1°C buffer
- Humidity: ±3% buffer

### **2. Manual Override**
You can always:
- Disable AI automation
- Manually control any actuator
- AI will resume when re-enabled

### **3. Fail-Safe**
If AI encounters errors:
- Logs error and continues
- Doesn't crash the system
- Retries on next cycle (10 seconds)

---

## 📈 Performance

### **Resource Usage (RPi3):**
- **RAM**: ~10-20MB for AI engine
- **CPU**: <5% average (spikes to 10% during decisions)
- **Decision Time**: <100ms per cycle
- **Frequency**: Every 10 seconds

### **Battery Impact:**
- Minimal - decisions are lightweight
- No continuous ML inference
- Rule-based logic is very efficient

---

## 🔧 Customization

### **Adjust Decision Frequency**

In `integrated_server.py`:
```python
time.sleep(10)  # Change to 5, 15, 30, etc.
```

### **Modify Thresholds**

Edit `ai_automation.py`:
```python
'spawning_co2_min': 10000,  # Change as needed
'fruiting_co2_max': 1000,   # Adjust for your mushrooms
```

### **Add Custom Rules**

In `ai_automation.py`, add to `_decide_spawning_mode()` or `_decide_fruiting_mode()`:
```python
# Example: Turn on LED during day hours
if 6 <= datetime.now().hour <= 18:
    actions['led_lights'] = True
    reasoning.append("Daytime - LED on")
```

---

## 📚 Training Your Own Model

### **1. Collect Data**

Record observations in `data/training_data.csv`:
```csv
timestamp,co2,temperature,humidity,mode,exhaust_fan,intake_fan,humidifier,outcome,notes
2025-11-06 08:00:00,12500,22.5,85.0,SPAWNING,0,0,1,success,Good growth
```

### **2. Label Outcomes**
- **success**: Mushrooms growing well
- **warning**: Borderline conditions
- **failure**: Poor growth or contamination

### **3. Train Model**
```bash
python3 raspberry-pi/train_decision_model.py
```

### **4. Restart Server**
```bash
sudo systemctl restart mash-iot
```

The AI will now use your trained thresholds!

---

## 🐛 Troubleshooting

### **AI Not Making Decisions**

**Check if enabled:**
```bash
curl http://raspberrypi.local:5000/api/automation/status
```

**Enable it:**
```bash
curl -X POST http://raspberrypi.local:5000/api/automation/enable
```

### **Actuators Not Responding**

1. Check GPIO connections
2. Verify relays are working
3. Check server logs for errors
4. Test manual control first

### **Decisions Seem Wrong**

1. Check sensor readings are accurate
2. Verify mode is correct (Spawning vs Fruiting)
3. Review thresholds in `/api/automation/status`
4. Check decision history for reasoning

---

## 🎓 Best Practices

### **1. Start with Observation**
- Run AI for a few days in test mode
- Monitor decisions without acting on them
- Verify logic makes sense

### **2. Gradual Rollout**
- Enable AI for one actuator at a time
- Start with humidifier (safest)
- Add exhaust fan once confident
- Keep LED manual

### **3. Regular Monitoring**
- Check decision history daily
- Review sensor trends weekly
- Retrain model monthly with new data

### **4. Backup Plan**
- Always have manual override ready
- Keep phone app accessible
- Monitor chamber visually

---

## 📞 Support

### **Common Questions:**

**Q: Will AI work without training data?**  
A: Yes! It uses default thresholds based on mushroom growing best practices.

**Q: Can I override AI decisions?**  
A: Absolutely! Manual control always takes priority.

**Q: How much RAM does it use?**  
A: ~10-20MB, leaving plenty for other RPi3 processes.

**Q: What if sensors fail?**  
A: AI will use last known good values and log warnings.

**Q: Can I use this for other mushroom species?**  
A: Yes, but train a separate model with species-specific data.

---

## 🚀 Next Steps

1. ✅ Enable AI automation
2. ✅ Monitor for 24 hours
3. ✅ Review decision history
4. ✅ Collect training data
5. ✅ Retrain model monthly
6. ✅ Fine-tune thresholds

**Happy autonomous growing!** 🍄🤖
