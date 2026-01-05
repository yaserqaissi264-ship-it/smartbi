# SmartBI - Intelligent Data Analytics Platform

A comprehensive, production-ready data analytics and business intelligence application built with Streamlit. SmartBI provides end-to-end data analysis, cleaning, feature engineering, forecasting, and AI-powered insights for SMBs and researchers.

## 🚀 Key Features

### 1. **🔬 Smart Data Profiling & Quality Analysis**
   - Comprehensive data profiling with automated insights
   - Real-time quality issue detection and severity assessment
   - Missing value analysis and correlation discovery
   - Actionable recommendations for data improvement

### 2. **🧪 Intelligent Data Preparation & Cleansing**
   - Advanced imputation methods (KNN, Iterative, Statistical)
   - Duplicate and outlier detection and removal
   - Before/after comparison with quality metrics
   - Automated data type optimization

### 3. **⚡ Powerful Feature Engineering**
   - Create polynomial and interaction features instantly
   - Generate statistical rolling window features and lags
   - Automatic categorical encoding and one-hot conversion
   - AI-powered feature importance ranking

### 4. **📊 Interactive Business Intelligence Dashboards**
   - Real-time interactive visualizations powered by Plotly
   - 11+ chart types: Correlation, Distribution, Box Plot, Violin Plot, Scatter, Bar, Histogram, Pie, Heatmap, Sunburst, Time Series
   - Deep correlation analysis and relationship mapping
   - Distribution and trend analysis across dimensions
   - Export-ready custom charts and reports

### 5. **🎯 Predictive Time Series Forecasting with Accuracy Metrics**
   - Prophet-based forecasting with trend and seasonality detection
   - **NEW:** Automatic accuracy metrics (MAE, RMSE, MAPE, R²)
   - Instant reliability assessment with color-coded indicators
   - Automatic confidence interval calculations
   - Long-term predictions with actionable guidance
   - Seasonal decomposition and anomaly detection

### 6. **🤖 AI-Powered Insights & Assistance**
   - Natural language interface with conversation history
   - Context-aware data analysis and recommendations
   - Smart insights generation from your data
   - Personalized guidance throughout your analysis journey

## 📋 Application Pages

| Page | Icon | Function |
|------|------|----------|
| Home | 🏠 | Landing page with quick start guide |
| Data Upload | 📤 | Upload CSV/Excel files |
| Data Overview | 📊 | Quick data inspection |
| **Data Analysis** | 🔬 | **NEW** - Comprehensive profiling & insights |
| Data Cleaning | 🧹 | Clean and prepare data |
| Feature Engineering | 🔧 | Create new features |
| Dashboard | 📈 | Interactive visualizations (11+ charts) |
| Forecasting | 🔮 | Time series predictions |
| AI Assistant | 🤖 | Conversational AI help |

## 🛠️ Tech Stack

**Frontend:**
- Streamlit - Web app framework
- Plotly Express & Graph Objects - Interactive visualizations

**Backend:**
- Python 3.11
- Pandas - Data manipulation
- NumPy - Numerical computing
- Scikit-learn - Machine learning & preprocessing
- Prophet - Time series forecasting
- SQLite3 - Data persistence

**Deployment:**
- Streamlit Cloud (Production)
- GitHub - Version control

**Optional:**
- OpenAI API - AI Assistant (graceful fallback if not configured)

## 📊 Chart Types (Dashboard)

The enhanced dashboard now supports **11 interactive chart types**:

1. **Correlation Matrix** - Feature correlations with heatmap
2. **Distribution** - Histogram with box plot
3. **Box Plot** - Statistical distribution with outliers
4. **Violin Plot** - Distribution density visualization
5. **Time Series** - Temporal trend analysis
6. **Scatter Plot** - 2D relationship with color coding
7. **Bar Chart** - Category-value comparisons
8. **Histogram** - Frequency distribution (configurable bins)
9. **Pie Chart** - Categorical proportion breakdown
10. **Heatmap** - Multi-column correlation matrix
11. **Sunburst** - Hierarchical categorical breakdown

All charts feature:
- 🎨 Professional styling with Plotly white template
- 📈 Enhanced hover information
- 🔍 Zoom and pan capabilities
- 📏 Responsive layouts
- 🎯 Export-ready quality

## 🏗️ Architecture

### Core Classes

**DataProfiler** (Lines 283-377)
```python
- generate_profile(df) - Basic metrics
- analyze_missing_values(df) - Missing data patterns
- detect_duplicates(df) - Duplicate analysis
- detect_data_types(df) - Column categorization
- identify_quality_issues(df) - Quality problems
- get_statistical_summary(df) - Numeric statistics
```

**InsightGenerator** (Lines 378-450)
```python
- analyze_features(df) - Feature characteristics
- analyze_correlations(df) - Relationship detection
- generate_recommendations(df, issues) - Action items
```

**FeatureExtractor** (Lines ~200+)
```python
- create_polynomial_features(df, columns, degree)
- create_interaction_features(df, columns)
- create_statistical_features(df, columns, window)
- create_categorical_features(df, column)
- feature_importance_analysis(df, target_col)
```

**Visualizer**
```python
- plot_correlation_matrix(df)
- plot_distribution(df, column)
- plot_time_series(df, date_col, value_col)
- plot_scatter(df, x_col, y_col)
```

### File Structure
```
/workspaces/smartbi/
├── smartbi_bundle.py          # Main app (1,639 lines)
├── smartbi.db                 # SQLite database
├── requirements.txt           # Dependencies
├── test_import.py             # Testing
└── README.md                  # This file
```

## 🚀 Getting Started

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yaserqaissi264-ship-it/smartbi.git
cd smartbi
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run locally:**
```bash
streamlit run smartbi_bundle.py
```

4. **(Optional) Configure OpenAI API:**
   - Create `.streamlit/secrets.toml`:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```
   - The app works without it (fallback mode)

### Deployment to Streamlit Cloud

1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. App auto-deploys on every push
4. Add secrets in Streamlit Cloud settings if needed

**Production URL:**
https://my-app-app-h9cr23bqyczmkde6yglsnp.streamlit.app/

## 📝 Usage Guide

### 1. **Data Upload**
   - Upload CSV or Excel files
   - Automatic schema detection
   - Data stored in SQLite for persistence

### 2. **Data Overview**
   - Quick inspection of loaded data
   - Column info and data types
   - Basic statistics

### 3. **Data Analysis** (NEW)
   - 7 interactive sections:
     - Data Understanding & Profiling
     - Data Quality Report
     - Feature Analysis
     - Correlation & Relationships
     - Distribution Analysis
     - Automated Recommendations
     - Before & After Cleaning

### 4. **Data Cleaning**
   - Handle missing values with multiple imputation methods
   - Remove duplicates and outliers
   - Compare before/after metrics

### 5. **Feature Engineering**
   - Create polynomial features (x², x³)
   - Generate interaction features (x*y)
   - Add statistical features (rolling, lags)
   - Encode categorical variables
   - Analyze feature importance

### 6. **Dashboard**
   - Select from 11+ chart types
   - Customize axis and grouping
   - Interactive exploration
   - Export visualizations

### 7. **Forecasting**
   - Time series predictions with Prophet
   - Seasonality detection
   - Confidence intervals
   - Accuracy metrics

### 8. **AI Assistant**
   - Chat with your data
   - Get insights and recommendations
   - Natural language queries

## 🔄 Recent Enhancements (Dec 17, 2025)

### Session 1: Core Features Implementation
- ✅ Added FeatureExtractor class with 5 feature engineering methods
- ✅ Implemented DataProfiler class with 6 analysis methods
- ✅ Created InsightGenerator for automated insights
- ✅ Integrated into navigation menu

### Session 2: Data Analysis Page
- ✅ Built comprehensive 7-section analysis page
- ✅ Added interactive visualizations
- ✅ Implemented automated recommendations

### Session 3: Error Resolution
- ✅ Fixed StreamlitSecretNotFoundError with fallback
- ✅ Resolved StreamlitDuplicateElementId
- ✅ Fixed StreamlitDuplicateElementKey (main() duplication)
- ✅ Deployed successfully to Streamlit Cloud

### Session 4: Chart Enhancements
- ✅ Updated home page Key Features (reordered, enhanced)
- ✅ Added 6 new chart types (Box, Violin, Histogram, Pie, Heatmap, Sunburst)
- ✅ Improved all visualizations with:
  - Professional styling (Plotly white template)
  - Better color schemes (Viridis, RdBu, custom)
  - Enhanced hover information
  - Optimized layouts
- ✅ Dual pie/bar chart view for categorical distributions
- ✅ Side-by-side histogram + box plot in Distribution Analysis

## 🐛 Known Issues & Fixes Applied

| Issue | Status | Fix |
|-------|--------|-----|
| Missing OpenAI API key | ✅ Fixed | Try/except fallback |
| Duplicate widget IDs | ✅ Fixed | Removed old backup file |
| Duplicate main() calls | ✅ Fixed | Removed second call |
| Chart styling | ✅ Enhanced | Added templates & colors |

## 📈 Performance Features

- **Lazy loading:** Charts render only on demand
- **Session state:** Efficient data caching
- **SQLite persistence:** Fast data retrieval
- **Optimized imputation:** Handles large datasets
- **Vectorized operations:** NumPy/Pandas for speed

## 🔐 Security

- No sensitive data stored in code
- Secrets managed through Streamlit Cloud
- SQLite for local data persistence
- OpenAI API optional (doesn't break without it)

## 📦 Dependencies

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
scikit-learn>=1.3.0
prophet>=1.1.4
sqlalchemy>=2.0.0
openpyxl>=3.1.0
```

## 🤝 Contributing

To contribute:
1. Create a feature branch
2. Make changes
3. Push to GitHub
4. Changes auto-deploy to Streamlit Cloud

## 📄 License

Private project - All rights reserved

## 👨‍💻 Author

Built by [Your Name] - SmartBI Team

## 📞 Support

For issues or feature requests, open an issue on GitHub.

---

**Last Updated:** December 17, 2025
**Version:** 1.0.0 (Production)
**Status:** ✅ Active & Deployed
