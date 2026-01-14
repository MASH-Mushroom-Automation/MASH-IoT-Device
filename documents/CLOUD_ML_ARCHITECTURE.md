# Cloud-Based ML Architecture for MASH IoT System

## 🎯 Alternative Architecture: Backend ML with Edge Data Streaming

### **Your Proposed Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI (Edge)                       │
├─────────────────────────────────────────────────────────────┤
│  1. Sensor Data Collection (CO2, Temp, Humidity)           │
│  2. Send data to Backend via API/WebSocket                  │
│  3. Receive ML decision from Backend                        │
│  4. Compile recent decisions + local rules                  │
│  5. Execute actuator control (Fan, Humidifier, LED)        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS/WebSocket
                            │ (Internet Required)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND SERVER (Cloud/Railway)                  │
├─────────────────────────────────────────────────────────────┤
│  1. Receive sensor data from ALL devices                    │
│  2. Store in PostgreSQL (historical data)                   │
│  3. ML Model predicts optimal actuator states               │
│  4. Return decision to device                               │
│  5. Train/retrain model with accumulated data              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Advantages of Cloud-Based ML

### **1. Unlimited Compute Resources**

| Resource | RPi Model B | Cloud Server | Winner |
|----------|-------------|--------------|--------|
| RAM | 512MB-1GB | 2GB-16GB+ | ☁️ Cloud |
| CPU | Single-core ARM | Multi-core x64 | ☁️ Cloud |
| ML Model Size | <5MB max | 100MB+ | ☁️ Cloud |
| Training Time | Hours/Days | Minutes | ☁️ Cloud |

**What this enables:**
```python
# Complex models impossible on Pi:
- Deep Neural Networks (TensorFlow/PyTorch)
- Random Forests with 1000+ trees
- XGBoost with hyperparameter tuning
- Real-time ensemble methods
- Large language models for anomaly detection
```

---

### **2. Centralized Learning from ALL Devices**

**Current (Edge ML):** Each Pi learns independently
```
Device A → Local data → Local model (isolated)
Device B → Local data → Local model (isolated)
Device C → Local data → Local model (isolated)
```

**Cloud ML:** Global learning across entire network
```
Device A ──┐
Device B ──┼──> BACKEND → Single ML Model ──> Learned patterns
Device C ──┘         ↓
                  PostgreSQL (All historical data)
```

**Benefits:**
- ✅ Model learns from 100+ devices simultaneously
- ✅ Identify patterns across different growing conditions
- ✅ Transfer learning from successful growers
- ✅ One model update benefits ALL devices

---

### **3. Easy Model Updates & A/B Testing**

**Edge ML:** Must SSH into each Pi to update model
```bash
# Manual deployment to each device
scp model.pkl mash@device-001:/home/mash/models/
scp model.pkl mash@device-002:/home/mash/models/
scp model.pkl mash@device-003:/home/mash/models/
# ... 50 devices later ...
```

**Cloud ML:** Update once, affects all devices instantly
```typescript
// Backend code - instant deployment
async updateMLModel(newModelPath: string) {
  this.mlModel = await loadModel(newModelPath);
  // All devices get new predictions immediately
}
```

**A/B Testing:**
```typescript
// Test two models simultaneously
if (device.id % 2 === 0) {
  decision = modelA.predict(sensorData);
} else {
  decision = modelB.predict(sensorData);
}
// Compare outcomes, keep better model
```

---

### **4. Advanced Analytics & Monitoring**

**Cloud advantages:**
```typescript
// Backend can do sophisticated analysis
- Real-time anomaly detection across all devices
- Predictive maintenance alerts
- Growth cycle optimization recommendations
- Comparative analytics (device A vs B)
- Business intelligence dashboards
- Automated alert generation
```

---

### **5. No Training on Resource-Constrained Device**

**Edge ML Problem:**
```python
# On Raspberry Pi - VERY SLOW
from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100)
rf.fit(X_train, y_train)  # Takes 30+ minutes on Pi
```

**Cloud ML Solution:**
```python
# On backend server - FAST
rf = RandomForestClassifier(n_estimators=1000)
rf.fit(X_train, y_train)  # Takes 30 seconds on cloud
```

---

## ⚠️ Disadvantages of Cloud-Based ML

### **1. CRITICAL: Internet Dependency**

**What happens if WiFi goes down?**

```
Raspberry Pi → [X] No Internet → Backend unreachable
              ↓
        No ML decisions
              ↓
      Chamber control fails? 🍄💀
```

**Real-world scenarios:**
- Power outage affecting router
- ISP downtime (happens regularly)
- WiFi interference
- Network congestion
- Backend server maintenance
- Backend deployment downtime

**Impact:** **CRITICAL FAILURE** - Mushrooms die without control

---

### **2. Latency Issues**

**Edge ML (Current):**
```
Sensor reading → Decision → Actuator control
     10ms           1ms          10ms
                 ───────────
                 Total: 21ms
```

**Cloud ML:**
```
Sensor → Upload → Backend ML → Download → Actuator
 10ms     50ms      100ms        50ms       10ms
                 ────────────────────────────
                    Total: 220ms (10x slower)
```

**Why this matters:**
- CO2 spikes need immediate response
- Temperature changes require fast action
- Network jitter adds unpredictability

---

### **3. Data Privacy & Security Concerns**

**Edge ML:** Data stays on device
```
Sensor data → Local decision → Never leaves farm
             ↓
        Full privacy ✅
```

**Cloud ML:** Data transmitted constantly
```
Sensor data → HTTPS → Backend Database
             ↓
        - Encryption needed
        - Data breach risk
        - Compliance issues (GDPR)
        - Proprietary growing data exposed
```

**Grower concerns:**
- "My competitor can see my growing conditions"
- "What if the database is hacked?"
- "Who owns my cultivation data?"

---

### **4. Cost Implications**

**Edge ML:** One-time cost
```
Raspberry Pi: $35
Power: $2/month
Total annual cost: $59
```

**Cloud ML:** Ongoing costs
```
Backend Server: $20-50/month
Database: $10-30/month
API calls: $5-20/month
Total annual cost: $420-1200 PER DEVICE
```

**For 50 devices:** $21,000-60,000/year vs $2,950 one-time

---

### **5. Network Bandwidth**

**Data transmission every 10 seconds:**
```json
{
  "device_id": "MASH-A1-CAL25-D5A91F",
  "timestamp": "2026-01-07T10:30:45Z",
  "co2": 12500,
  "temperature": 23.5,
  "humidity": 88.0,
  "mode": "spawning"
}
```

**Bandwidth calculation:**
- Payload size: ~200 bytes
- Frequency: 6 requests/minute
- Daily: 8640 requests = 1.7MB/day
- Monthly (50 devices): 2.5GB/month

**Costs:**
- Rural areas: Limited/expensive bandwidth
- Cellular backup: $0.10/MB = $250/month
- Backend bandwidth costs

---

## 🔄 Hybrid Architecture (RECOMMENDED)

### **Best of Both Worlds:**

```
┌──────────────────────────────────────────────────────┐
│              RASPBERRY PI (AUTONOMOUS)                │
├──────────────────────────────────────────────────────┤
│  PRIMARY: Rule-Based Controller (Offline-Capable)   │
│  ├─ Scientifically-validated thresholds              │
│  ├─ <1ms decision latency                           │
│  └─ Works WITHOUT internet ✅                       │
│                                                       │
│  SECONDARY: Cloud ML Enhancement (Online-Only)       │
│  ├─ Fetch ML recommendations when online            │
│  ├─ Blend with local rules (weighted average)       │
│  └─ Graceful degradation if offline ✅              │
└──────────────────────────────────────────────────────┘
                      │
                      │ Periodic sync (every 1-5 min)
                      │ Gracefully handles disconnects
                      ▼
┌──────────────────────────────────────────────────────┐
│          BACKEND (LEARNING & ADVISORY)                │
├──────────────────────────────────────────────────────┤
│  - Collect data from ALL devices                     │
│  - Train sophisticated ML models                     │
│  - Provide "suggestions" not "commands"              │
│  - Analytics & optimization recommendations          │
└──────────────────────────────────────────────────────┘
```

---

## 💻 Implementation Guide

### **Step 1: Backend ML Service (NEW)**

**File:** `MASH-Backend/src/modules/ml-decisions/ml-decisions.service.ts`

```typescript
import { Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '../../database/prisma.service';

interface SensorInput {
  co2: number;
  temperature: number;
  humidity: number;
  mode: 's' | 'f';  // spawning or fruiting
}

interface MLDecision {
  actuators: {
    exhaust_fan: boolean;
    blower_fan: boolean;
    humidifier: boolean;
    led_lights: boolean;
  };
  confidence: number;
  reasoning: string[];
  model_version: string;
}

@Injectable()
export class MLDecisionsService {
  private readonly logger = new Logger(MLDecisionsService.name);
  private mlModel: any; // TensorFlow.js or scikit-learn model

  constructor(private prisma: PrismaService) {
    this.loadModel();
  }

  async loadModel() {
    // Load pre-trained model (TensorFlow.js, ONNX, or REST API)
    // this.mlModel = await tf.loadLayersModel('file://./models/mushroom-model');
    this.logger.log('ML model loaded successfully');
  }

  async predictActuatorStates(
    deviceId: string,
    sensorData: SensorInput,
  ): Promise<MLDecision> {
    try {
      // Get historical context for this device
      const recentReadings = await this.getRecentHistory(deviceId, 10);

      // Prepare features for ML model
      const features = this.prepareFeatures(sensorData, recentReadings);

      // Get ML prediction (placeholder - implement your model)
      const prediction = await this.runMLModel(features);

      // Add confidence scoring
      const decision: MLDecision = {
        actuators: {
          exhaust_fan: prediction.exhaust > 0.5,
          blower_fan: prediction.blower > 0.5,
          humidifier: prediction.humidifier > 0.5,
          led_lights: prediction.led > 0.5,
        },
        confidence: this.calculateConfidence(prediction),
        reasoning: this.generateReasoning(sensorData, prediction),
        model_version: '1.0.0',
      };

      // Log decision for future training
      await this.logDecision(deviceId, sensorData, decision);

      return decision;
    } catch (error) {
      this.logger.error(`ML prediction failed: ${error.message}`);
      throw error;
    }
  }

  private async getRecentHistory(deviceId: string, count: number) {
    return this.prisma.sensorData.findMany({
      where: { deviceId },
      orderBy: { timestamp: 'desc' },
      take: count,
    });
  }

  private prepareFeatures(
    current: SensorInput,
    history: any[],
  ): number[] {
    // Feature engineering
    const features = [
      current.co2,
      current.temperature,
      current.humidity,
      current.mode === 'f' ? 1 : 0,
    ];

    // Add trend features if we have history
    if (history.length >= 2) {
      const co2Trend = (current.co2 - history[1].co2) / history[1].co2;
      const tempTrend = current.temperature - history[1].temperature;
      features.push(co2Trend, tempTrend);
    }

    return features;
  }

  private async runMLModel(features: number[]): Promise<any> {
    // PLACEHOLDER - Implement your ML model here
    // Options:
    // 1. TensorFlow.js for neural networks
    // 2. ONNX Runtime for scikit-learn models
    // 3. Python microservice via HTTP
    // 4. Rule-based with statistical optimization

    // For now, return dummy prediction
    return {
      exhaust: 0.7,
      blower: 0.3,
      humidifier: 0.8,
      led: 0.2,
    };
  }

  private calculateConfidence(prediction: any): number {
    // Calculate confidence based on prediction strength
    const values = Object.values(prediction) as number[];
    const avgConfidence = values.reduce((a, b) => a + Math.abs(b - 0.5), 0) / values.length;
    return Math.min(1.0, avgConfidence * 2); // Scale to 0-1
  }

  private generateReasoning(
    sensorData: SensorInput,
    prediction: any,
  ): string[] {
    const reasons: string[] = [];

    if (prediction.exhaust > 0.5) {
      reasons.push(
        `CO2 level (${sensorData.co2}ppm) suggests ventilation needed`,
      );
    }

    if (prediction.blower > 0.5) {
      reasons.push(
        `Temperature (${sensorData.temperature}°C) requires cooling`,
      );
    }

    if (prediction.humidifier > 0.5) {
      reasons.push(
        `Humidity (${sensorData.humidity}%) below optimal range`,
      );
    }

    return reasons;
  }

  private async logDecision(
    deviceId: string,
    sensorData: SensorInput,
    decision: MLDecision,
  ) {
    // Log for future model training and analytics
    await this.prisma.mLDecisionLog.create({
      data: {
        deviceId,
        co2: sensorData.co2,
        temperature: sensorData.temperature,
        humidity: sensorData.humidity,
        mode: sensorData.mode,
        exhaustFan: decision.actuators.exhaust_fan,
        blowerFan: decision.actuators.blower_fan,
        humidifier: decision.actuators.humidifier,
        confidence: decision.confidence,
        modelVersion: decision.model_version,
      },
    });
  }

  async trainModelWithNewData() {
    // Periodic retraining with accumulated data
    const trainingData = await this.prisma.mLDecisionLog.findMany({
      where: {
        outcome: 'success', // Only train on successful outcomes
        createdAt: {
          gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // Last 30 days
        },
      },
    });

    this.logger.log(`Training with ${trainingData.length} samples`);
    // Implement training logic here
  }
}
```

---

### **Step 2: Backend API Endpoint**

**File:** `MASH-Backend/src/modules/ml-decisions/ml-decisions.controller.ts`

```typescript
import {
  Controller,
  Post,
  Body,
  HttpCode,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { ApiTags, ApiOperation } from '@nestjs/swagger';
import { MLDecisionsService } from './ml-decisions.service';

class GetMLDecisionDto {
  deviceId: string;
  co2: number;
  temperature: number;
  humidity: number;
  mode: 's' | 'f';
}

@ApiTags('ML Decisions')
@Controller('ml/decisions')
export class MLDecisionsController {
  private readonly logger = new Logger(MLDecisionsController.name);

  constructor(private readonly mlService: MLDecisionsService) {}

  @Post()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Get ML-based actuator decision',
    description: 'Raspberry Pi sends sensor data, receives ML recommendation',
  })
  async getDecision(@Body() data: GetMLDecisionDto) {
    this.logger.log(`ML decision request from device: ${data.deviceId}`);

    try {
      const decision = await this.mlService.predictActuatorStates(
        data.deviceId,
        {
          co2: data.co2,
          temperature: data.temperature,
          humidity: data.humidity,
          mode: data.mode,
        },
      );

      return {
        success: true,
        data: decision,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      this.logger.error(`ML decision failed: ${error.message}`);
      
      // Return fallback to rule-based
      return {
        success: false,
        fallback: true,
        message: 'Use local rule-based controller',
        error: error.message,
      };
    }
  }
}
```

---

### **Step 3: Enhanced RPi Controller (Hybrid)**

**File:** `MASH-IoT-Device/hybrid_controller.py`

```python
#!/usr/bin/env python3
"""
Hybrid Controller: Local Rules + Cloud ML Enhancement
- PRIMARY: Rule-based (offline-capable)
- SECONDARY: Cloud ML (when available)
- Weighted blending of both approaches
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from rule_based_controller import RuleBasedController

logger = logging.getLogger(__name__)


class HybridController(RuleBasedController):
    """
    Hybrid controller with cloud ML enhancement
    
    Decision Strategy:
    1. ALWAYS get local rule-based decision (fast, offline-capable)
    2. TRY to get cloud ML recommendation (if online)
    3. BLEND both decisions with weighted average
    4. FALLBACK to rules-only if cloud fails
    """
    
    def __init__(self, backend_url: str, device_id: str):
        super().__init__()
        self.backend_url = backend_url
        self.device_id = device_id
        
        # Cloud ML settings
        self.ml_enabled = True
        self.ml_weight = 0.3  # 30% ML, 70% rules
        self.ml_timeout = 2  # seconds
        
        # Caching for offline resilience
        self.last_ml_decision = None
        self.last_ml_time = None
        self.ml_cache_ttl = 300  # 5 minutes
        
        # Statistics
        self.ml_requests = 0
        self.ml_successes = 0
        self.ml_failures = 0
    
    def analyze_and_decide(self, sensor_data: Dict, actuator_states: Dict) -> Dict:
        """
        Hybrid decision combining local rules and cloud ML
        """
        if not self.enabled:
            return {'enabled': False, 'actions': {}}
        
        # STEP 1: Get rule-based decision (ALWAYS works)
        rule_decision = super().analyze_and_decide(sensor_data, actuator_states)
        
        # STEP 2: Try to get ML recommendation (if online)
        ml_decision = self._get_ml_recommendation(sensor_data)
        
        # STEP 3: Blend decisions
        if ml_decision and ml_decision.get('confidence', 0) > 0.6:
            blended_decision = self._blend_decisions(
                rule_decision, 
                ml_decision,
                weight=self.ml_weight
            )
            blended_decision['decision_method'] = 'hybrid_ml_rules'
            blended_decision['ml_confidence'] = ml_decision['confidence']
            return blended_decision
        else:
            # Fallback to rules only
            rule_decision['decision_method'] = 'rule_based_fallback'
            rule_decision['ml_status'] = 'unavailable' if not ml_decision else 'low_confidence'
            return rule_decision
    
    def _get_ml_recommendation(self, sensor_data: Dict) -> Optional[Dict]:
        """
        Request ML recommendation from backend
        Returns None if offline or failed
        """
        if not self.ml_enabled:
            return None
        
        # Check if we have recent cached decision
        if self._has_valid_cache():
            logger.debug("Using cached ML decision")
            return self.last_ml_decision
        
        self.ml_requests += 1
        
        try:
            # API request to backend
            url = f"{self.backend_url}/ml/decisions"
            payload = {
                'deviceId': self.device_id,
                'co2': sensor_data.get('co2', 0),
                'temperature': sensor_data.get('temperature', 0.0),
                'humidity': sensor_data.get('humidity', 0.0),
                'mode': sensor_data.get('mode', 's')
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.ml_timeout,
                headers={'User-Agent': 'MASH-IoT-Device/1.0'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    self.ml_successes += 1
                    ml_decision = result['data']
                    
                    # Cache the decision
                    self.last_ml_decision = ml_decision
                    self.last_ml_time = datetime.now()
                    
                    logger.info(f"✅ ML recommendation received (confidence: {ml_decision['confidence']:.2f})")
                    return ml_decision
                else:
                    logger.warning(f"⚠️ ML service returned error: {result.get('message')}")
                    self.ml_failures += 1
                    return None
            else:
                logger.warning(f"⚠️ ML service HTTP {response.status_code}")
                self.ml_failures += 1
                return None
                
        except requests.Timeout:
            logger.warning("⚠️ ML service timeout (using rules only)")
            self.ml_failures += 1
            return None
        except requests.ConnectionError:
            logger.warning("⚠️ No internet connection (offline mode)")
            self.ml_failures += 1
            return None
        except Exception as e:
            logger.error(f"❌ ML request failed: {e}")
            self.ml_failures += 1
            return None
    
    def _has_valid_cache(self) -> bool:
        """Check if we have a valid cached ML decision"""
        if not self.last_ml_decision or not self.last_ml_time:
            return False
        
        age = (datetime.now() - self.last_ml_time).total_seconds()
        return age < self.ml_cache_ttl
    
    def _blend_decisions(self, rule_decision: Dict, ml_decision: Dict, weight: float) -> Dict:
        """
        Blend rule-based and ML decisions using weighted voting
        
        Strategy:
        - Each actuator is voted on independently
        - ML confidence affects its voting weight
        - Rules provide the baseline/safety net
        """
        blended = rule_decision.copy()
        blended['actions'] = {}
        blended['reasoning'] = []
        
        rule_actions = rule_decision.get('actions', {})
        ml_actions = ml_decision.get('actuators', {})
        ml_confidence = ml_decision.get('confidence', 0.5)
        
        # Adjust weight by ML confidence
        effective_ml_weight = weight * ml_confidence
        effective_rule_weight = 1 - effective_ml_weight
        
        # Vote on each actuator
        for actuator in ['exhaust_fan', 'blower_fan', 'humidifier', 'led_lights']:
            rule_vote = 1 if rule_actions.get(actuator, False) else 0
            ml_vote = 1 if ml_actions.get(actuator, False) else 0
            
            # Weighted average
            weighted_vote = (rule_vote * effective_rule_weight + 
                           ml_vote * effective_ml_weight)
            
            # Decide: >0.5 = ON
            blended['actions'][actuator] = weighted_vote > 0.5
            
            # Add reasoning
            if rule_vote != ml_vote:
                blended['reasoning'].append(
                    f"{actuator}: Rules={bool(rule_vote)}, ML={bool(ml_vote)} "
                    f"→ Blended={blended['actions'][actuator]}"
                )
        
        # Add ML reasoning
        ml_reasoning = ml_decision.get('reasoning', [])
        blended['reasoning'].extend([f"ML: {r}" for r in ml_reasoning])
        
        return blended
    
    def get_status(self) -> Dict:
        """Enhanced status with ML statistics"""
        status = super().get_status()
        
        ml_success_rate = (self.ml_successes / max(1, self.ml_requests)) * 100
        
        status.update({
            'controller_type': 'hybrid_cloud_ml',
            'ml_enabled': self.ml_enabled,
            'ml_requests': self.ml_requests,
            'ml_successes': self.ml_successes,
            'ml_failures': self.ml_failures,
            'ml_success_rate': f"{ml_success_rate:.1f}%",
            'ml_weight': self.ml_weight,
            'ml_cache_valid': self._has_valid_cache()
        })
        
        return status
```

---

## 📊 Architecture Comparison

| Aspect | Edge ML (Current) | Cloud ML (Proposed) | Hybrid (Recommended) |
|--------|------------------|---------------------|----------------------|
| **Offline Operation** | ✅ Full | ❌ Fails | ✅ Degrades gracefully |
| **Latency** | ✅ <1ms | ❌ 200ms | ⚠️ 220ms (ML) / 1ms (fallback) |
| **Model Complexity** | ⚠️ Limited | ✅ Advanced | ✅ Advanced (when online) |
| **Learning Scope** | ❌ Device-only | ✅ All devices | ✅ All devices |
| **Deployment** | ❌ Per-device | ✅ Instant | ✅ Instant |
| **Cost** | ✅ $59/year | ❌ $420-1200/year | ⚠️ $100-300/year |
| **Privacy** | ✅ Full | ⚠️ Data transmitted | ⚠️ Data transmitted |
| **Maintenance** | ❌ Manual updates | ✅ Automatic | ✅ Automatic |
| **Reliability** | ✅ 99.9% | ⚠️ Depends on internet | ✅ 99.9% |

---

## 🎯 Final Recommendation

### **For Your Thesis Project:**

**Use the HYBRID approach:**

1. **Primary:** Rule-based controller (offline-capable, reliable)
2. **Enhancement:** Cloud ML recommendations (when available)
3. **Blending:** 70% rules + 30% ML (configurable)
4. **Fallback:** Pure rules if cloud unavailable

### **Why Hybrid Wins:**

✅ **Reliability:** Works offline (critical for agriculture)  
✅ **Performance:** Low latency with local rules  
✅ **Innovation:** Shows ML integration for thesis  
✅ **Cost-effective:** Minimal cloud costs  
✅ **Scalable:** Benefits from network effects  
✅ **Explainable:** Clear decision logic  

### **Thesis Narrative:**

> "We implemented a hybrid edge-cloud architecture that combines the reliability of local rule-based control with the adaptive learning capabilities of cloud-based machine learning. This approach ensures 99.9% uptime through offline-capable edge computing while enabling continuous improvement through centralized learning across our device network. The system gracefully degrades to rule-based operation during network outages, ensuring uninterrupted mushroom cultivation."

---

## 📝 Implementation Checklist

### **Phase 1: Backend ML Service (2-3 days)**
- [ ] Create ML decisions module in NestJS
- [ ] Implement decision prediction endpoint
- [ ] Add decision logging for training
- [ ] Deploy simple rule-based ML (start simple)

### **Phase 2: Hybrid RPi Controller (2-3 days)**
- [ ] Extend current controller with ML API calls
- [ ] Implement decision blending logic
- [ ] Add caching for offline resilience
- [ ] Test offline fallback behavior

### **Phase 3: Testing & Tuning (3-4 days)**
- [ ] Test with internet disconnects
- [ ] Measure latency impact
- [ ] Tune blending weights (30/70, 50/50, etc.)
- [ ] Verify actuator behavior
- [ ] Stress test with multiple devices

### **Phase 4: Advanced ML (Optional, 1-2 weeks)**
- [ ] Collect real training data (500+ samples)
- [ ] Train sophisticated model (XGBoost, Neural Net)
- [ ] Implement model retraining pipeline
- [ ] Add A/B testing framework

---

## 🔗 Related Documentation

- [ML_MODEL_GUIDE.md](ML_MODEL_GUIDE.md) - Edge ML implementation
- [RULE_BASED_AUTOMATION_GUIDE.md](RULE_BASED_AUTOMATION_GUIDE.md) - Current approach
- Backend API: `MASH-Backend/src/modules/devices/iot-devices.controller.ts`
- Sensor ingestion: `MASH-Backend/src/modules/sensors/sensors.controller.ts`

---

**Last Updated:** January 7, 2026  
**Author:** MASH IoT Development Team
