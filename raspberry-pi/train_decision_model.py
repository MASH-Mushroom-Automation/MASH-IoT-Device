#!/usr/bin/env python3
"""
MASH IoT - Training Script for Decision Model
Analyzes historical data to optimize thresholds and decision rules
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_training_data(csv_path):
    """Load training dataset from CSV"""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} training samples from {csv_path}")
        return df
    except Exception as e:
        logger.error(f"Failed to load training data: {e}")
        return None


def analyze_optimal_thresholds(df):
    """
    Analyze historical data to find optimal thresholds
    This is a simple statistical approach suitable for 1GB RAM
    """
    thresholds = {}
    
    # Analyze spawning mode data
    spawning_data = df[df['mode'] == 'SPAWNING']
    if len(spawning_data) > 0:
        # Find CO2 levels where mushrooms grew successfully
        successful_spawning = spawning_data[spawning_data['outcome'] == 'success']
        if len(successful_spawning) > 0:
            thresholds['spawning_co2_min'] = int(successful_spawning['co2'].quantile(0.25))
            logger.info(f"Optimal spawning CO2 minimum: {thresholds['spawning_co2_min']} ppm")
    
    # Analyze fruiting mode data
    fruiting_data = df[df['mode'] == 'FRUITING']
    if len(fruiting_data) > 0:
        successful_fruiting = fruiting_data[fruiting_data['outcome'] == 'success']
        if len(successful_fruiting) > 0:
            thresholds['fruiting_co2_min'] = int(successful_fruiting['co2'].quantile(0.10))
            thresholds['fruiting_co2_max'] = int(successful_fruiting['co2'].quantile(0.90))
            logger.info(f"Optimal fruiting CO2 range: {thresholds['fruiting_co2_min']}-{thresholds['fruiting_co2_max']} ppm")
    
    # Temperature analysis
    successful_data = df[df['outcome'] == 'success']
    if len(successful_data) > 0:
        thresholds['temp_min'] = float(successful_data['temperature'].quantile(0.05))
        thresholds['temp_max'] = float(successful_data['temperature'].quantile(0.95))
        logger.info(f"Optimal temperature range: {thresholds['temp_min']:.1f}-{thresholds['temp_max']:.1f}°C")
        
        # Humidity analysis
        thresholds['humidity_min'] = float(successful_data['humidity'].quantile(0.10))
        thresholds['humidity_max'] = float(successful_data['humidity'].quantile(0.90))
        logger.info(f"Optimal humidity range: {thresholds['humidity_min']:.1f}-{thresholds['humidity_max']:.1f}%")
    
    return thresholds


def analyze_actuator_effectiveness(df):
    """
    Analyze how effective each actuator was at correcting conditions
    Returns effectiveness scores
    """
    effectiveness = {}
    
    # Group by actuator state changes
    for actuator in ['exhaust_fan', 'intake_fan', 'humidifier']:
        if actuator in df.columns:
            # Find periods when actuator was activated
            activated = df[df[actuator] == 1]
            
            if len(activated) > 10:
                # Measure average improvement in conditions after activation
                # This is a simplified analysis
                effectiveness[actuator] = {
                    'usage_count': len(activated),
                    'avg_co2_after': float(activated['co2'].mean()),
                    'avg_temp_after': float(activated['temperature'].mean()),
                    'avg_humidity_after': float(activated['humidity'].mean())
                }
                logger.info(f"{actuator} effectiveness: used {len(activated)} times")
    
    return effectiveness


def save_model(thresholds, effectiveness, output_path):
    """Save trained model parameters to JSON"""
    model = {
        'version': '1.0',
        'trained_date': datetime.now().isoformat(),
        'thresholds': thresholds,
        'actuator_effectiveness': effectiveness
    }
    
    try:
        with open(output_path, 'w') as f:
            json.dump(model, f, indent=2)
        logger.info(f"Model saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save model: {e}")


def main():
    """Main training pipeline"""
    logger.info("=== MASH IoT Decision Model Training ===")
    
    # Load training data
    training_data_path = '/home/pi/mash_iot/data/training_data.csv'
    df = load_training_data(training_data_path)
    
    if df is None or len(df) == 0:
        logger.error("No training data available")
        return
    
    # Analyze data
    logger.info("Analyzing optimal thresholds...")
    thresholds = analyze_optimal_thresholds(df)
    
    logger.info("Analyzing actuator effectiveness...")
    effectiveness = analyze_actuator_effectiveness(df)
    
    # Save model
    output_path = '/home/pi/mash_iot/models/decision_model.json'
    save_model(thresholds, effectiveness, output_path)
    
    logger.info("=== Training Complete ===")


if __name__ == '__main__':
    main()
