# SmartBI - Code Explanation Guide
**For explaining the code **

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Main Components](#architecture--main-components)
3. [Module Breakdown](#module-breakdown)
4. [Key Features Explained](#key-features-explained)
5. [How the Application Works](#how-the-application-works)

---

## Project Overview

### What is SmartBI?
**SmartBI** is a comprehensive Business Intelligence (BI) and Data Analytics application built with **Streamlit** (a Python web framework). It's designed to help users analyze their data without requiring deep technical knowledge.

### Core Purpose
The application provides:
- **Data Upload & Management**: Store and manage multiple datasets
- **Data Cleaning**: Handle missing values, duplicates, and outliers
- **Data Analysis**: Understand data quality and patterns
- **Feature Engineering**: Create new features from existing data
- **Market Basket Analysis**: Find products frequently bought together
- **Time Series Forecasting**: Predict future trends
- **Interactive Dashboards**: Visualize data in multiple ways
- **AI Assistant**: Get conversational help with data analysis

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly (interactive charts)
- **Machine Learning**: scikit-learn, Prophet
- **Database**: SQLite
- **AI**: OpenAI API (optional)

---

## Architecture & Main Components

### Overall Structure

```
smartbi_bundle.py
├── Imports & Dependency Checks
│   ├── scikit-learn (ML/imputation)
│   ├── Prophet (Forecasting)
│   └── OpenAI (AI Assistant)
│
├── Core Classes
│   ├── SmartBIDatabase (Data persistence)
│   ├── DataCleaner (Data quality handling)
│   ├── DataProfiler (Data analysis)
│   ├── InsightGenerator (Automated insights)
│   ├── FeatureExtractor (Feature engineering)
│   ├── TimeSeriesForecaster (Predictions)
│   ├── AIAssistant (Conversational AI)
│   └── Visualizer (Chart creation)
│
└── Streamlit Application
    ├── Session State Initialization
    └── UI Pages
        ├── Home
        ├── Data Upload
        ├── Data Overview
        ├── Data Cleaning
        ├── Dashboard
        ├── Market Basket Analysis
        ├── Feature Engineering
        ├── Forecasting
        ├── Data Analysis
        └── AI Chat
```

---

## Module Breakdown

### 1. **Imports & Dependency Management** (Lines 1-45)

```python
import streamlit as st          # Web framework
import pandas as pd             # Data manipulation
import numpy as np              # Numerical computing
import plotly.express as px     # Interactive charts
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3                  # Database
import json
from pathlib import Path
import warnings
```

**Purpose**: Import all required libraries with error handling for optional packages.

**Why it matters**: 
- Graceful degradation if some packages aren't installed
- Users can still use the app even without Prophet or OpenAI

---

### 2. **Database Layer (SmartBIDatabase class)** (Lines 50-155)

#### Purpose
Stores datasets and analysis history persistently using SQLite.

#### Key Methods

**`__init__()` & `init_database()`**
```python
def init_database(self):
    # Creates 3 tables:
    # 1. datasets - stores uploaded CSV files
    # 2. analysis_history - tracks what analysis was done
    # 3. chat_history - stores AI conversations
```

**`save_dataset(name, df)`**
- Converts DataFrame to JSON format
- Saves to SQLite database
- Returns dataset ID for later retrieval

**`load_dataset(dataset_id)`**
- Retrieves saved dataset by ID
- Converts JSON back to DataFrame

**`list_datasets()`**
- Shows all saved datasets with metadata

#### Real-World Example
```
User uploads "sales_data.csv" 
→ Saved to SQLite as dataset_id=5
→ User can load it anytime later
→ All analysis linked to dataset_id=5
```

---

### 3. **Data Cleaner (DataCleaner class)** (Lines 160-260)

#### Purpose
Handles messy data through multiple cleaning strategies.

#### Key Methods

**`analyze_missing_data(df)`**
```python
# Shows:
# - Which columns have missing values
# - How many are missing
# - Percentage of missing data
# - Data types
```

**`simple_imputation(df, strategy='mean')`**
```python
# Three strategies:
# 1. Mean: Fill with average value
# 2. Median: Fill with middle value  
# 3. Most frequent: Fill with most common value
```

**`knn_imputation(df, n_neighbors=5)`**
```python
# KNN = K-Nearest Neighbors
# Finds 5 similar rows and uses their values
# Better than simple strategies for complex patterns
```

**`iterative_imputation(df, max_iter=10)`**
```python
# MICE = Multivariate Imputation by Chained Equations
# Uses machine learning to predict missing values
# More sophisticated - treats it as a prediction problem
```

**`handle_outliers(df, method='iqr', threshold=1.5)`**
```python
# IQR Method: Caps values outside normal range
# Identifies extreme values and brings them back to normal
# Example: Cap prices above 10000 to 10000
```

#### Real-World Example
```
Original Data:          Missing: 50 values
Age: [25, 30, _, 28, _]   Purchase: [100, _, 200, _, 150]

After Mean Imputation:
Age: [25, 30, 27.67, 28, 27.67]  (filled with average 27.67)
Purchase: [100, 150, 200, 150, 150]  (filled with average 150)
```

---

### 4. **Data Profiler (DataProfiler class)** (Lines 265-380)

#### Purpose
Analyzes data quality and generates insights automatically.

#### Key Methods

**`generate_profile(df)`**
```python
# Creates summary:
# - Shape: rows and columns
# - Column names
# - Data types
# - Memory usage
```

**`identify_quality_issues(df)`**
```python
# Checks for:
# - High missing values (>50%)
# - Constant columns (only 1 unique value)
# - Very high cardinality (too many categories)
# - Outliers (potential data errors)
```

**`get_statistical_summary(df)`**
```python
# Standard statistics:
# - Count, Mean, Std Dev
# - Min, 25%, 50%, 75%, Max
# Similar to df.describe()
```

#### Real-World Example
```
Issues Found:
1. "Age" has 45% missing values → Suggest imputation
2. "Status" has only "Active" value → Constant column!
3. "Product_ID" has 10,000 unique values → High cardinality
4. "Price" has 8% outliers → Consider capping
```

---

### 5. **Insight Generator (InsightGenerator class)** (Lines 385-500)

#### Purpose
Automatically generates business insights from data.

#### Key Methods

**`analyze_product_associations(df, transaction_column, separator=',')`**
```python
# Finds which products are bought together
# Calculates:
# - Co-occurrence: How often products appear together
# - Support: % of transactions with both products
# - Confidence: If they buy A, what's chance they buy B?
# - Lift: How much more likely to buy together than separately?

# Example:
# If 100 transactions, 30 have Beer, 20 have Chips, 15 have both:
# - Co-occurrence: 15
# - Support: 15/100 = 15%
# - Confidence(Beer→Chips): 15/30 = 50%
# - Lift: (15/100) / (30/100 * 20/100) = 2.5x likely
```

**`analyze_pos_data(df)`**
```python
# POS = Point of Sale (cash register data)
# Calculates:
# - Total revenue
# - Average transaction size
# - Customer retention
# - Payment method breakdown
# - Category performance
```

---

### 6. **Feature Extractor (FeatureExtractor class)** (Lines 505-580)

#### Purpose
Creates new features from existing data to improve ML models.

#### Key Methods

**`create_polynomial_features(df, columns, degree=2)`**
```python
# Transforms features by raising to power
# Original: price = [10, 20, 30]
# Power 2: price² = [100, 400, 900]
# Power 3: price³ = [1000, 8000, 27000]

# Why? Some models work better with non-linear relationships
```

**`create_interaction_features(df, columns)`**
```python
# Multiplies columns together
# If price = [10, 20] and quantity = [2, 5]
# Interaction = [20, 100]  (10*2, 20*5)

# Why? Captures combined effect of two variables
# Example: Price × Quantity = Total Revenue
```

**`create_statistical_features(df, columns, window=7)`**
```python
# Rolling window statistics over time
# Rolling Mean: Average over last 7 days
# Rolling Std: Standard deviation over last 7 days
# Lag 1: Previous day's value
# Lag 3: Value from 3 days ago

# Why? Captures trends and patterns
```

**`feature_importance_analysis(df, target_col)`**
```python
# Measures correlation of each feature with target
# Which features predict the target best?
# Returns sorted list from most to least important
```

#### Real-World Example
```
Original Features:        New Features Created:
Price: 100              Price_power_2: 10000
Days: 5                 Days_power_2: 25
                        Price_x_Days: 500
                        Price_rolling_mean_7: 98.5
                        Price_lag_1: 95
```

---

### 7. **Time Series Forecaster (TimeSeriesForecaster class)** (Lines 585-680)

#### Purpose
Predicts future values based on historical patterns using **Prophet**.

#### Prophet Overview
- **Facebook's Time Series Library**
- Handles seasonality (patterns that repeat)
- Detects trends (going up/down)
- Manages holidays and special events
- Works with non-linear trends

#### Key Methods

**`prepare_prophet_data(df, date_col, value_col)`**
```python
# Prophet requires specific format:
# ds (date) | y (value)
# 2024-01-01 | 100
# 2024-01-02 | 105
# 2024-01-03 | 110
```

**`forecast_with_prophet(df, periods=30)`**
```python
# Fits Prophet model to historical data
# Predicts next 30 periods (days/weeks/etc)
# Returns forecast with confidence intervals
# Example:
#   ds: 2024-02-01, yhat: 120, yhat_lower: 110, yhat_upper: 130
```

**`calculate_accuracy_metrics(actual_df, forecast)`**
```python
# Measures forecast quality:
# - MAE (Mean Absolute Error): Average prediction error
# - RMSE (Root Mean Squared Error): Penalizes large errors
# - MAPE (Mean Absolute Percentage Error): % error
# - R² (R-squared): How well model explains variation
```

#### Real-World Example
```
Historical Sales:      Forecast (Next 7 days):
Jan 1:  100           Feb 1: 120 ± 10 (110-130)
Jan 2:  105           Feb 2: 125 ± 12 (113-137)
Jan 3:  110           Feb 3: 130 ± 14 (116-144)
Jan 4:  115           ...
Jan 5:  120
```

---

### 8. **AI Assistant (AIAssistant class)** (Lines 685-750)

#### Purpose
Conversational AI to help users understand their data.

#### Key Methods

**`chat(message, context="")`**
```python
# Sends message to OpenAI's GPT API
# System prompt: "You're SmartBI Assistant, expert in BI"
# User message: "How do I clean missing data?"
# Response: Generated by GPT model

# Without API key → Falls back to predefined responses
```

**`_fallback_response(message)`**
```python
# When OpenAI not available, provides basic help
# Matches keywords like "clean", "forecast", "dashboard"
# Gives canned but relevant responses
```

---

### 9. **Visualizer (Visualizer class)** (Lines 755-920)

#### Purpose
Creates interactive charts using Plotly.

#### Key Methods

**`plot_correlation_matrix(df)`**
```python
# Heatmap showing correlations between all numeric columns
# -1 (negative) ← → +1 (positive)
# Red = positive correlation
# Blue = negative correlation
# Usage: Find related features
```

**`plot_distribution(df, column)`**
```python
# Histogram showing distribution shape
# With box plot on side
# Usage: Check if data is normal, bimodal, skewed
```

**`plot_time_series(df, date_col, value_col)`**
```python
# Line chart over time
# Usage: See trends and patterns
```

**`plot_product_association_network(associations)`**
```python
# Network graph of product relationships
# Products as nodes (circles)
# Connections show co-purchases
# Usage: Visualize which products go together
```

---

## Key Features Explained

### Feature 1: Data Upload & Automatic Type Detection

```python
def data_upload_page():
    # User uploads CSV
    # Automatically detects numeric columns (has "amount", "price", etc.)
    # Automatically converts to datetime (has "date", "time", etc.)
    # Shows preview and column info
    # Option to save to database
```

**Why it matters**: Users don't need to manually specify column types.

---

### Feature 2: Multi-Method Data Imputation

```python
Imputation Methods (ranked by sophistication):
1. Simple Mean       - Fills with average
2. Simple Median     - Fills with middle value
3. KNN Imputation    - Uses 5 similar rows
4. MICE/Iterative    - Uses ML to predict values
```

**Why multiple methods?**
- Different datasets need different approaches
- Users can try and compare results

---

### Feature 3: Market Basket Analysis

```python
Input: Transaction data with product lists
"Transaction_1: Apple + Banana + Orange"
"Transaction_2: Banana + Grape"
"Transaction_3: Apple + Banana"

Output:
- Apple + Banana: 2 co-occurrences, 66% confidence, 1.5x lift
- Shows which products to bundle
```

**Business Application**: 
- Create "Apple + Banana" bundle
- Put them near each other in store
- Recommend together at checkout

---

### Feature 4: Interactive Dashboards

```python
Available Chart Types:
1. Correlation Matrix - Find related features
2. Distribution - Check data shape
3. Box Plot - See quartiles and outliers
4. Time Series - Track trends
5. Scatter Plot - Find patterns between 2 variables
6. Bar Chart - Compare categories
7. Pie Chart - Show proportions
8. Sunburst - Hierarchical categories
9. Heatmap - 2D correlation
```

**Why Plotly?** Interactive - zoom, hover for details, export as PNG.

---

### Feature 5: Session State Management

```python
# Streamlit apps reset on each interaction
# Session state keeps data in memory
st.session_state.current_df     # Current dataset
st.session_state.cleaned_df     # Cleaned version
st.session_state.engineered_df  # With new features
st.session_state.chat_history   # AI conversations
```

**Why it matters**: Users don't re-upload data after each action.

---

## How the Application Works

### Application Flow Diagram

```
1. User opens smartbi_bundle.py
         ↓
2. Streamlit loads the app
         ↓
3. init_session_state() initializes database and variables
         ↓
4. Sidebar displays page navigation
         ↓
5. User selects a page (e.g., "Data Upload")
         ↓
6. Page function executes (e.g., data_upload_page())
         ↓
7. User interacts with widgets (buttons, sliders, etc.)
         ↓
8. Streamlit detects change
         ↓
9. Relevant data processing classes run
         ↓
10. Results displayed in UI
         ↓
11. Results saved to session_state (stays in memory)
```

### Execution Example: Data Cleaning Page

```
User clicks "Apply Imputation" button
            ↓
data_cleaning_page() detects button click
            ↓
Gets selected method (e.g., "KNN Imputation")
            ↓
Calls DataCleaner.knn_imputation(df, n_neighbors=5)
            ↓
Inside knn_imputation():
    - Selects numeric columns
    - Creates KNNImputer from scikit-learn
    - Fits on current data
    - Transforms and returns cleaned data
            ↓
Result stored in st.session_state.cleaned_df
            ↓
Shows "✅ Data cleaned successfully!"
            ↓
Displays before/after missing value counts
            ↓
User clicks "Apply Cleaned Data"
            ↓
st.session_state.current_df = st.session_state.cleaned_df
            ↓
All subsequent analyses use cleaned data
```

### Execution Example: Forecasting

```
User selects date column, value column, and periods=30
            ↓
Clicks "Generate Forecast"
            ↓
forecast_page() detects button
            ↓
Calls TimeSeriesForecaster.prepare_prophet_data()
    - Creates ds, y format required by Prophet
            ↓
Calls TimeSeriesForecaster.forecast_with_prophet()
    - Initializes Prophet model
    - Fits to historical data
    - Creates future DataFrame for next 30 periods
    - Predicts values and confidence intervals
            ↓
Calls calculate_accuracy_metrics()
    - Merges actual and forecast data
    - Calculates MAE, RMSE, MAPE, R²
            ↓
Displays:
    - Metrics (accuracy numbers)
    - Interactive Plotly chart
    - Forecast table with future values
            ↓
Results saved to st.session_state.forecast_*
```

### Execution Example: Market Basket Analysis

```
User selects transaction column and separator
            ↓
Clicks "Analyze Associations"
            ↓
Calls InsightGenerator.analyze_product_associations()
            ↓
Inside function:
    1. Parse transactions by separator
       "Apple+Banana+Orange" → [Apple, Banana, Orange]
    
    2. Count product frequencies
       {Apple: 50, Banana: 45, Orange: 30}
    
    3. Find pairs (all combinations)
       (Apple, Banana): 25 co-occurrences
       (Apple, Orange): 10 co-occurrences
       (Banana, Orange): 15 co-occurrences
    
    4. Calculate metrics
       Support = co-occurrence / total_transactions
       Confidence_AB = co-occurrence / frequency_A
       Lift = (co-occurrence / total) / (freq_A * freq_B / total²)
            ↓
Returns:
    - associations list (all pairs with metrics)
    - product_freq list (most popular products)
    - triplets (3-way combinations)
            ↓
Visualizer.plot_product_association_network()
    - Creates network graph
    - Nodes = products
    - Edges = co-purchases
            ↓
Displays:
    - Summary metrics
    - Association rules table
    - Network visualization
    - Product frequency chart
    - Strength ranking
```

---

## Summary of Key Concepts to Explain 

### 1. **Architecture**
- **Modular Design**: Separate classes for each functionality (cleaning, forecasting, etc.)
- **Database Layer**: SQLite persists user data between sessions
- **Session State**: Streamlit's mechanism to keep data in memory during user interaction

### 2. **Data Processing**
- **Multiple Imputation Methods**: From simple (mean) to advanced (MICE)
- **Outlier Detection**: IQR and Z-score methods
- **Automated Profiling**: Identifies data quality issues without user input

### 3. **Machine Learning**
- **Prophet for Forecasting**: Handles seasonality and trends automatically
- **Scikit-learn Integration**: Imputation, feature engineering, ML algorithms
- **Feature Engineering**: Creates new features from existing data

### 4. **User Interface**
- **Streamlit Framework**: Rapid web app development with Python
- **Interactive Visualizations**: Plotly provides zoom, hover, export capabilities
- **Multi-page Application**: Navigation sidebar with different analysis pages

### 5. **Business Logic**
- **Market Basket Analysis**: Association rules (support, confidence, lift)
- **POS Analytics**: Transaction analysis, customer insights
- **Time Series Forecasting**: Predicting future values with confidence intervals

### 6. **Code Quality**
- **Error Handling**: Graceful degradation if packages missing
- **Type Checking**: Optional parameters with defaults
- **Comments & Docstrings**: Clear explanation of each class/method

---

## Key Metrics & Formulas Reference

### Market Basket Analysis
```
Support(A→B) = Count(A and B) / Total Transactions
Confidence(A→B) = Count(A and B) / Count(A)
Lift(A→B) = Confidence(A→B) / Support(B)
```

### Forecasting Accuracy
```
MAE = Average(|actual - predicted|)
RMSE = √(Average((actual - predicted)²))
MAPE = Average(|actual - predicted| / |actual|) × 100
R² = 1 - (Sum of Squares Residual) / (Total Sum of Squares)
```

### Outlier Detection (IQR Method)
```
IQR = Q3 - Q1
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
Values outside bounds = Outliers
```

---

## Common Interview Questions (For Your Professor)

**Q1: Why use SQLite instead of just storing DataFrames in memory?**
A: SQLite allows data to persist between sessions. When user closes and reopens the app, their datasets are still available.

**Q2: Why multiple imputation methods?**
A: Different datasets have different characteristics. KNN works well for pattern-based missing data, MICE for complex relationships. Users can try multiple and compare.

**Q3: How does market basket analysis help businesses?**
A: Identifies products frequently bought together, enabling:
- Strategic product bundling
- Cross-selling recommendations
- Store layout optimization
- Targeted marketing

**Q4: Why is session state necessary?**
A: Streamlit reruns the entire script on each interaction. Without session state, data would be lost and need to be reloaded every time.

**Q5: How does Prophet handle forecasting better than simple methods?**
A: Prophet explicitly models:
- Trend (going up/down)
- Seasonality (weekly, yearly patterns)
- Holiday effects
- Confidence intervals (not just point predictions)

---

## Quick Reference: File Sizes & Complexity

| Component | Lines | Complexity | Purpose |
|-----------|-------|-----------|---------|
| SmartBIDatabase | ~100 | Low | Data persistence |
| DataCleaner | ~100 | Medium | Data quality |
| DataProfiler | ~120 | Low | Analysis & insights |
| InsightGenerator | ~150 | Medium | Business logic |
| FeatureExtractor | ~80 | Low | Feature creation |
| TimeSeriesForecaster | ~100 | High | ML forecasting |
| AIAssistant | ~60 | Medium | Conversational AI |
| Visualizer | ~150 | Low | Chart creation |
| **Total UI Pages** | ~1700 | High | User interaction |
| **TOTAL** | ~2868 | Medium-High | Full application |

---

## Final Notes for Presentation

1. **Start Simple**: Explain database → then explain data cleaning → then visualization
2. **Use Examples**: "If user uploads sales data..." helps make it concrete
3. **Highlight Innovation**: Market basket analysis, multiple imputation methods, AI integration
4. **Discuss Tradeoffs**: Why multiple methods? Why SQLite? Why Streamlit?
5. **Show Real Value**: Business applications (bundling, forecasting, customer insights)
6. **Code Quality**: Modular design, error handling, documentation

Good luck with your presentation! 🚀
