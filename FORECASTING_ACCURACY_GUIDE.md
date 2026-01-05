# 🔮 SmartBI Forecasting Accuracy Guide

## Overview

Your SmartBI forecasting feature now includes **comprehensive accuracy metrics** to help you understand how reliable your forecasts are. When you generate a time series forecast, the system automatically calculates 4 key accuracy metrics and provides interpretations.

---

## 📊 The 4 Accuracy Metrics

### 1. **MAE (Mean Absolute Error)**
- **What it measures:** Average absolute difference between predicted and actual values
- **Formula:** MAE = Σ|actual - predicted| / n
- **Interpretation:**
  - Lower is better
  - In the same units as your data (e.g., if forecasting sales in dollars, MAE is in dollars)
  - Tells you: "On average, my forecast is off by X units"

**Example:** MAE = 5.54 means your forecast is off by ~$5.54 on average

---

### 2. **RMSE (Root Mean Square Error)**
- **What it measures:** Penalizes larger errors more heavily than small ones
- **Formula:** RMSE = √(Σ(actual - predicted)² / n)
- **Interpretation:**
  - Lower is better
  - Always ≥ MAE (can be equal)
  - Useful for detecting if you have a few very bad predictions
  - Larger RMSE relative to MAE indicates inconsistent forecast quality

**Example:** RMSE = 10.39 vs MAE = 5.54 means you have some outlier errors

---

### 3. **MAPE (Mean Absolute Percentage Error)**
- **What it measures:** Average percentage error relative to actual values
- **Formula:** MAPE = Σ|actual - predicted| / |actual| × 100 / n
- **Interpretation:**
  - Lower is better
  - Shows error as a percentage (easier to compare across different scales)
  - **Accuracy Levels:**
    - **< 5%:** 🟢 Excellent
    - **5-10%:** 🟡 Good
    - **10-20%:** 🟠 Fair
    - **> 20%:** 🔴 Poor

**Example:** MAPE = 3.91% means forecast is typically off by 3.91% compared to actual values

---

### 4. **R² (R-Squared / Coefficient of Determination)**
- **What it measures:** How much variation in data the model explains
- **Formula:** R² = 1 - (SS_residual / SS_total)
- **Range:** -∞ to 1
- **Interpretation:**
  - Closer to 1 is better
  - 0.7+ = Strong fit
  - 0.3-0.7 = Moderate fit
  - < 0.3 = Weak fit
  - < 0 = Model worse than just using the average

**Example:** R² = 0.85 means the model explains 85% of the variation in sales

---

## 🎯 How to Interpret Your Results

### Scenario 1: Excellent Forecast
```
MAE: 2.5    RMSE: 4.1    MAPE: 2.3%    R²: 0.92

🟢 EXCELLENT - Very reliable forecast
Use with confidence for planning and decision-making
```

**Action:** Use this forecast for budgeting, inventory planning, and strategy

---

### Scenario 2: Good Forecast
```
MAE: 5.5    RMSE: 10.4    MAPE: 5.2%    R²: 0.75

🟡 GOOD - Reliable forecast
Use for most planning purposes with minor caveats
```

**Action:** Use for planning but with some buffer for uncertainty

---

### Scenario 3: Fair Forecast
```
MAE: 15.0   RMSE: 22.3    MAPE: 15.4%   R²: 0.50

🟠 FAIR - Moderate accuracy
Use with caution, consider additional analysis
```

**Action:** Use for general trends but don't rely on exact numbers

---

### Scenario 4: Poor Forecast
```
MAE: 35.0   RMSE: 45.1    MAPE: 35.7%   R²: 0.15

🔴 POOR - Low accuracy
Do not use for critical decisions without additional analysis
```

**Action:** Collect more data, check for missing values, or adjust parameters

---

## 🚀 How to Improve Forecast Accuracy

### 1. **More Data** (Most Important)
- Prophet (what we use) works better with more historical data
- Minimum: 100 days
- Recommended: 1+ years of data
- Better: 2+ years of data

**Action:** Extend your historical data range if possible

---

### 2. **Adjust Seasonality Settings**
- ✅ Enable "Yearly Seasonality" if you have year-over-year patterns
- ✅ Enable "Weekly Seasonality" if you have weekly patterns (e.g., weekend vs weekday)
- ✅ Enable "Daily Seasonality" only if you have intra-day patterns

**Action:** Match seasonality settings to your business cycle

---

### 3. **Check Data Quality**
- Remove outliers (extreme values from special events)
- Handle missing values before forecasting
- Use "Data Cleaning" page to prepare your data
- Ensure no data entry errors

**Action:** Go to "Data Cleaning" and prepare your data first

---

### 4. **Right Forecast Horizon**
- Shorter forecasts are more accurate (1-7 days vs 30-365 days)
- Every day into future reduces accuracy slightly
- Use confidence intervals to understand uncertainty

**Action:** Start with shorter forecasts and expand gradually

---

### 5. **Look for Anomalies**
- Major discrepancies between predicted and actual?
- Check for one-time events (sales, promotions, outages)
- These create noise that reduces model accuracy

**Action:** Filter out known anomalies from training data

---

## 📈 Example Interpretation

**Your forecasting results:**
```
📊 METRICS:
  • MAE: 5.54
  • RMSE: 10.39
  • MAPE: 3.91%
  • R²: 0.8526

🟢 EXCELLENT - Very reliable forecast
📊 STRONG R² - Explains > 70% of variance
```

**What this means:**
- ✅ On average, forecast is off by $5.54
- ✅ Only 3.91% error rate
- ✅ Model explains 85% of sales variation
- ✅ Safe to use for planning

**Recommendations:**
- Proceed with confidence
- Use forecast for budget planning
- Monitor actual vs forecast quarterly

---

## 🔍 When Metrics Conflict

Sometimes metrics tell different stories:

| Metric | Value | Status |
|--------|-------|--------|
| MAE | 5.54 | ✅ Low |
| MAPE | 3.91% | ✅ Low |
| R² | 0.85 | ✅ High |
| RMSE | 10.39 | ⚠️ Moderate |

**Interpretation:** 
- Model is generally accurate (low MAE, low MAPE, high R²)
- But has some outlier predictions (higher RMSE)
- **Action:** Still good to use, but watch for unusual data points

---

## 💡 Key Takeaways

1. **MAPE is most intuitive** - Shows error as a percentage
2. **R² tells the whole story** - How well does model fit?
3. **RMSE catches outliers** - Detects inconsistent quality
4. **MAE in data units** - Easy to understand business impact
5. **More data = Better accuracy** - Most important factor

---

## 🛠️ Using Forecasts in SmartBI

### Step 1: Generate Forecast
1. Go to **Forecasting** page
2. Select date column and value column
3. Adjust seasonality parameters
4. Click **Generate Forecast**

### Step 2: Review Accuracy Metrics
- Check the 4 metrics
- Read the interpretation
- Assess confidence level

### Step 3: Make Decisions
- ✅ MAPE < 10% → Use with confidence
- ⚠️ MAPE 10-20% → Use with caution
- ❌ MAPE > 20% → Collect more data first

### Step 4: Download & Share
- Download CSV with forecast values
- Share confidence intervals with stakeholders
- Update quarterly with new data

---

## ❓ FAQ

**Q: What if R² is negative?**  
A: Model is worse than just using average. More data needed or different approach required.

**Q: Should I trust MAPE or R²?**  
A: Both, but for different reasons. MAPE shows practical % error. R² shows variance explained.

**Q: Why is my RMSE so much higher than MAE?**  
A: You have outlier predictions. Some forecasts are very far off while most are close.

**Q: How many data points do I need?**  
A: Minimum 50-100, recommended 365+, ideal 730+ for yearly seasonality.

**Q: Can I forecast beyond 365 days?**  
A: Yes, but accuracy drops. Every day into future reduces confidence.

---

## 📚 Next Steps

1. **Try the demo** - Use sample data to explore forecasting
2. **Upload your data** - Test with real business data
3. **Interpret results** - Use this guide to understand metrics
4. **Improve data** - Clean and prepare your data first
5. **Monitor performance** - Update forecast monthly and track accuracy

---

**Happy Forecasting! 🚀**
