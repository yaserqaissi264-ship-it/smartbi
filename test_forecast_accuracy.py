#!/usr/bin/env python3
"""
Test script to demonstrate forecasting accuracy metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample time series data
def generate_sample_timeseries():
    """Generate sample data with trend and seasonality"""
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # Generate time series with trend and seasonality
    trend = np.linspace(100, 200, len(dates))
    seasonality = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
    noise = np.random.normal(0, 5, len(dates))
    sales = trend + seasonality + noise
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales
    })
    
    return df


def calculate_accuracy_metrics(actual, predicted):
    """Calculate key forecasting accuracy metrics"""
    
    # Filter to same length
    min_len = min(len(actual), len(predicted))
    actual = np.array(actual[:min_len])
    predicted = np.array(predicted[:min_len])
    
    # Mean Absolute Error
    mae = np.mean(np.abs(actual - predicted))
    
    # Root Mean Square Error
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    # Mean Absolute Percentage Error
    mape = np.mean(np.abs((actual - predicted) / (np.abs(actual) + 1e-10))) * 100
    
    # R-squared
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r_squared = 1 - (ss_res / (ss_tot + 1e-10))
    
    return {
        'MAE': mae,
        'RMSE': rmse,
        'MAPE': mape,
        'R²': r_squared
    }


def interpret_accuracy(metrics):
    """Provide interpretation of accuracy metrics"""
    
    print("\n" + "="*70)
    print("FORECAST ACCURACY ANALYSIS")
    print("="*70)
    
    print("\n📊 METRICS:")
    print(f"  • MAE (Mean Absolute Error):        {metrics['MAE']:.2f}")
    print(f"    └─ Lower is better. Average absolute difference between predicted and actual.")
    
    print(f"\n  • RMSE (Root Mean Square Error):    {metrics['RMSE']:.2f}")
    print(f"    └─ Lower is better. Penalizes larger errors more heavily.")
    
    print(f"\n  • MAPE (Mean Absolute % Error):    {metrics['MAPE']:.2f}%")
    print(f"    └─ Lower is better. % error relative to actual values.")
    
    print(f"\n  • R² (Coefficient of Determination): {metrics['R²']:.4f}")
    print(f"    └─ Closer to 1 is better. % of variance explained by model.")
    
    # Accuracy interpretation
    print("\n📈 ACCURACY LEVEL:")
    if metrics['MAPE'] < 5:
        print("  🟢 EXCELLENT - Very reliable forecast")
        print("     Use with confidence for planning")
    elif metrics['MAPE'] < 10:
        print("  🟡 GOOD - Reliable forecast")
        print("     Use for most planning purposes")
    elif metrics['MAPE'] < 20:
        print("  🟠 FAIR - Moderate accuracy")
        print("     Use with some caution")
    else:
        print("  🔴 POOR - Low accuracy")
        print("     Consider more data or adjusting parameters")
    
    # R² interpretation
    print("\n📊 MODEL FIT (R²):")
    if metrics['R²'] < 0:
        print("  🔴 POOR - Model performs worse than average")
    elif metrics['R²'] < 0.3:
        print("  🟠 WEAK - Explains < 30% of variance")
    elif metrics['R²'] < 0.7:
        print("  🟡 MODERATE - Explains 30-70% of variance")
    else:
        print("  🟢 STRONG - Explains > 70% of variance")
    
    print("\n" + "="*70)


def main():
    print("\n🔮 SmartBI Forecasting Accuracy Demo")
    print("="*70)
    
    # Generate sample data
    print("\n📥 Generating sample time series data...")
    df = generate_sample_timeseries()
    print(f"   Generated {len(df)} days of sales data (2023-2024)")
    
    # Simulate a forecast (using simple moving average for demo)
    print("\n🤖 Generating forecast predictions...")
    df['forecast'] = df['sales'].rolling(window=30, center=True).mean()
    df['forecast'] = df['forecast'].fillna(df['sales'].mean())
    
    # Remove NaN values
    df_clean = df.dropna()
    
    # Calculate metrics
    print("\n🧮 Calculating accuracy metrics...")
    metrics = calculate_accuracy_metrics(
        df_clean['sales'].values,
        df_clean['forecast'].values
    )
    
    # Display results
    interpret_accuracy(metrics)
    
    # Show sample data
    print("\n📋 Sample Data:")
    print(df.head(10).to_string())
    
    print("\n✅ Forecasting accuracy test complete!")
    print("\nThe SmartBI Forecasting page now includes:")
    print("  • Automatic accuracy metric calculation")
    print("  • MAE, RMSE, MAPE, and R² metrics")
    print("  • Automatic interpretation and recommendations")
    print("  • Visual indicators for forecast reliability")


if __name__ == "__main__":
    main()
