# 🚀 Quick Start: Forecasting Accuracy

## In 5 Minutes

### 1. Open SmartBI
```
Launch the app and navigate to Forecasting page (🔮)
```

### 2. Select Your Data
```
Date Column: Select your date/timestamp column
Value Column: Select what you want to forecast (sales, visitors, etc.)
```

### 3. Configure Settings
```
Forecast Periods: 30 (days to predict into future)
Yearly Seasonality: ✓ (if you have yearly patterns)
Weekly Seasonality: ✓ (if you have weekly patterns)
```

### 4. Generate Forecast
```
Click: 🚀 Generate Forecast
Wait: ~5-30 seconds depending on data size
```

### 5. View Accuracy Metrics
```
You'll see 4 numbers:
- MAE (5.54)      → Typical error size
- RMSE (10.39)    → Largest errors penalty
- MAPE (3.91%)    → Percentage error
- R² (0.8526)     → Model quality

Plus: 🟢 EXCELLENT interpretation
```

---

## 📊 What Each Metric Means (Simple Version)

| Metric | What It Means | Good Range |
|--------|---------------|-----------|
| **MAPE** | % error rate | < 10% |
| **MAE** | Avg difference | Low as possible |
| **RMSE** | Penalizes big errors | Low as possible |
| **R²** | Explains variance | > 0.7 |

---

## 🟢 Good Forecast = Use It!

```
MAPE < 10% → Use for planning
Colors show: 🟢 Excellent/🟡 Good → Proceed
```

## 🔴 Poor Forecast = Get More Data

```
MAPE > 20% → Don't use for critical decisions
Colors show: 🟠 Fair/🔴 Poor → Need improvement
```

---

## 💡 One-Liners

- **MAE 5.54** = "Forecast is off by ~$5.54 on average"
- **RMSE 10.39** = "Biggest errors are ~$10 (ouch!)"
- **MAPE 3.91%** = "96% accurate on average"
- **R² 0.8526** = "Explains 85% of the variation"

---

## 🎯 Decision Guide

```
MAPE < 5%:    🟢 Excellent  → Use with full confidence
MAPE 5-10%:   🟡 Good       → Use normally
MAPE 10-20%:  🟠 Fair       → Use with caution
MAPE > 20%:   🔴 Poor       → Collect more data
```

---

## 📈 Example Output

```
📊 Forecast Accuracy Metrics

┌─────────────┬──────────────┬────────────┬───────────────┐
│ MAE         │ RMSE         │ MAPE       │ R²            │
│ 5.54        │ 10.39        │ 3.91%      │ 0.8526        │
└─────────────┴──────────────┴────────────┴───────────────┘

🟢 EXCELLENT - Very reliable forecast
✅ Model captures most of the data variation
✅ Use with confidence for planning
```

---

## ❓ Quick FAQ

**Q: Is MAPE 5% good?**
A: Yes! Less than 10% is considered good.

**Q: What's the difference between MAPE and MAE?**
A: MAPE is %, MAE is actual numbers. Use MAPE to compare.

**Q: R² of 0.8 - is that good?**
A: Yes! 0.8 means 80% variance explained. Anything > 0.7 is strong.

**Q: My MAPE is 25% - what do I do?**
A: Collect more data (minimum 1 year recommended).

**Q: How many days of data do I need?**
A: Minimum 100, recommended 365+, ideal 730+ days.

---

## 🚀 Done!

You now understand forecasting accuracy. See the full guide for deeper details:
- **FORECASTING_ACCURACY_GUIDE.md** - Everything explained
- **test_forecast_accuracy.py** - See it working

Enjoy your forecasts! 📊✨
