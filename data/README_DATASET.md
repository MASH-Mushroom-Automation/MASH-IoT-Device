# MASH IoT Training Dataset Guide

## Purpose

This dataset is used to train the ML decision engine to optimize actuator control based on historical mushroom growing data.

## Data Collection

### Manual Data Collection

Record observations during your mushroom growing cycles:

1. **Timestamp**: When the reading was taken
2. **Sensor readings**: CO2, temperature, humidity from Arduino
3. **Actuator states**: Which devices were on/off
4. **Outcome**: How well the mushrooms grew
5. **Notes**: Any observations about mushroom health

### Automated Data Collection

The Raspberry Pi can log data automatically:

```python
# Add to actuator_controller.py
import csv
from datetime import datetime

def log_data(reading, actuator_states, outcome='unknown'):
    with open('/home/pi/mash_iot/data/collected_data.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            reading['co2'],
            reading['temperature'],
            reading['humidity'],
            reading['mode'],
            1 if actuator_states['exhaust_fan'] else 0,
            1 if actuator_states['intake_fan'] else 0,
            1 if actuator_states['humidifier'] else 0,
            outcome,
            ''  # notes
        ])
```

## Dataset Structure

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| timestamp | datetime | When reading was taken | 2024-01-01 10:00:00 |
| co2 | integer | CO2 level in ppm | 12500 |
| temperature | float | Temperature in °C | 22.5 |
| humidity | float | Relative humidity % | 85.0 |
| mode | string | SPAWNING or FRUITING | SPAWNING |
| exhaust_fan | integer | 0=off, 1=on | 0 |
| intake_fan | integer | 0=off, 1=on | 0 |
| humidifier | integer | 0=off, 1=on | 1 |
| outcome | string | success/failure/warning | success |
| notes | string | Optional observations | "Pins forming" |

## Outcome Labels

### Success
- Mushrooms growing as expected
- Healthy mycelium colonization (spawning)
- Good pin formation and fruiting body development (fruiting)
- No contamination or stress signs

### Failure
- Poor or no growth
- Contamination appeared
- Mushrooms aborted or died
- Mycelium stopped spreading

### Warning
- Growth slower than expected
- Minor stress signs (yellowing, thin stems)
- Conditions borderline but recoverable
- Preventive action taken

## Data Quality Guidelines

### Minimum Dataset Size
- **Initial training**: At least 100 samples per mode (200 total)
- **Better results**: 500+ samples per mode
- **Optimal**: 1000+ samples covering various conditions

### Data Balance
Try to include:
- ✅ 60% success cases (what works well)
- ✅ 30% warning cases (borderline conditions)
- ✅ 10% failure cases (what to avoid)

### Coverage
Ensure data covers:
- Different CO2 levels (low, optimal, high)
- Temperature variations (18-28°C)
- Humidity variations (80-95%)
- Both spawning and fruiting modes
- Different actuator combinations

## Example Scenarios to Record

### Spawning Mode Examples

**Optimal Conditions:**
```csv
2024-01-01 10:00:00,12500,22.5,85.0,SPAWNING,0,0,1,success,"Healthy white mycelium"
2024-01-01 10:05:00,13000,22.8,86.0,SPAWNING,0,0,1,success,"Rapid colonization"
```

**Too Low CO2:**
```csv
2024-01-01 11:00:00,8000,22.0,84.0,SPAWNING,0,1,0,failure,"Slow growth, ventilation error"
```

**Recovery:**
```csv
2024-01-01 11:05:00,9500,22.2,85.0,SPAWNING,0,0,1,warning,"Recovering from low CO2"
```

### Fruiting Mode Examples

**Optimal Conditions:**
```csv
2024-01-02 08:00:00,650,20.5,91.0,FRUITING,0,0,1,success,"Perfect pins forming"
2024-01-02 08:05:00,720,20.8,92.0,FRUITING,0,0,1,success,"Fruiting bodies developing"
```

**High CO2 Correction:**
```csv
2024-01-02 09:00:00,1100,21.5,89.0,FRUITING,1,1,0,warning,"CO2 too high, venting"
2024-01-02 09:05:00,800,21.2,90.0,FRUITING,0,0,1,success,"Corrected to optimal range"
```

**Low Humidity:**
```csv
2024-01-02 10:00:00,700,21.0,78.0,FRUITING,0,0,1,warning,"Humidity low, mushrooms drying"
2024-01-02 10:05:00,720,21.0,85.0,FRUITING,0,0,1,success,"Humidity restored"
```

## Data Validation

Before training, validate your dataset:

```python
import pandas as pd

df = pd.read_csv('training_data.csv')

# Check for missing values
print("Missing values:")
print(df.isnull().sum())

# Check value ranges
print("\nValue ranges:")
print(f"CO2: {df['co2'].min()} - {df['co2'].max()} ppm")
print(f"Temp: {df['temperature'].min()} - {df['temperature'].max()} °C")
print(f"Humidity: {df['humidity'].min()} - {df['humidity'].max()} %")

# Check outcome distribution
print("\nOutcome distribution:")
print(df['outcome'].value_counts())

# Check mode distribution
print("\nMode distribution:")
print(df['mode'].value_counts())
```

## Using the Template

1. Copy `training_data_template.csv` to `training_data.csv`
2. Add your own observations
3. Keep the same column structure
4. Save as CSV (UTF-8 encoding)
5. Run training script when you have 100+ samples

## Continuous Improvement

As you collect more data:

1. **Weekly**: Add new observations to dataset
2. **Monthly**: Retrain model with updated data
3. **Quarterly**: Review and clean dataset (remove outliers)

## Privacy & Storage

- Data is stored locally on Raspberry Pi
- No cloud upload required
- Backup recommended: `scp pi@raspberrypi:/home/pi/mash_iot/data/*.csv ./backup/`

## Questions?

Common questions:

**Q: How often should I record data?**
A: Every 5-10 minutes during active growing, or whenever you make observations.

**Q: What if I don't know the outcome yet?**
A: Use "unknown" and update later when you see results.

**Q: Can I use data from different mushroom species?**
A: Keep separate datasets per species, as requirements differ.

**Q: How do I handle contamination?**
A: Mark as "failure" and note in comments. This helps the model learn warning signs.
