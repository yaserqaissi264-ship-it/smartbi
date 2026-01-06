# Understanding Column Selection in SmartBI
## Why You Only See Some Columns in Analysis

### The Issue
When you use features like "Distribution Analysis" or various chart types, you see "Select Column" dropdowns that seem to show fewer columns than your dataset has. 

**Example:**
- Dataset has **13 total columns**
- Distribution Analysis only shows **2 columns** (like Year)

### Why This Happens
SmartBI intelligently filters columns based on their **data type**:

#### 📊 Numeric Columns (Analysis-Ready)
These columns contain numbers and can be used for:
- Distribution analysis
- Statistical calculations
- Correlations
- Box plots, histograms, etc.

**Examples:** Year, Customer_Age, Total_Amount, Items, Revenue

#### 🏷️ Categorical Columns (Text/Category Data)
These columns contain text/categories and are used for:
- Group by analysis
- Category breakdowns
- Pie charts, bar charts

**Examples:** Customer_Status, Payment_Method, Primary_Item_Category, Day_of_Week

#### 📅 DateTime Columns (Date/Time Data)
These columns contain dates/times and are used for:
- Time series analysis
- Trend analysis
- Time-based filtering

**Examples:** Date, Time, Transaction_Timestamp

---

## Example: POS Data Analysis

### Your Dataset Columns
```
Transaction_ID        → Text (ID)
Date                  → DateTime (Date)
Time                  → Text (Time String)
Day_of_Week          → Categorical (Text)
Year                 → Numeric ✓ (Can analyze)
Customer_ID          → Text (ID)
Customer_Age         → Numeric ✓ (Can analyze)
Customer_Status      → Categorical (Text)
Payment_Method       → Categorical (Text)
Primary_Item_Category → Categorical (Text)
Items                → Numeric ✓ (Can analyze)
Total_Amount_JOD     → Numeric ✓ (Can analyze)
```

**Numeric Columns Available for Distribution Analysis:** 4
- Year
- Customer_Age
- Items
- Total_Amount_JOD

---

## Where Different Column Types Are Used

### Distribution Analysis
**Shows:** Numeric columns only
- Why? Statistical analysis requires numbers
- Example: Histogram of Customer_Age distribution

### Dashboard → Distribution Chart
**Shows:** Numeric columns only
- Why? Can't create histograms from text
- Example: Distribution of Total_Amount_JOD

### Dashboard → Pie Chart
**Shows:** Categorical columns only
- Why? Need categories to create pie slices
- Example: Payment Methods breakdown

### Dashboard → Box Plot
**Shows:** 
- Numeric (Y-axis): All numeric columns
- Categorical (Group By): All categorical columns
- Example: Total_Amount by Payment_Method

### Correlation Analysis
**Shows:** Numeric columns only (2+)
- Why? Correlation measures numeric relationships
- Example: Correlation between Items count and Total_Amount

### Forecasting
**Shows:** 
- Date column: DateTime columns
- Value column: Numeric columns
- Example: Forecast Total_Amount over time using Date

---

## How to Check Your Dataset

### In Data Overview Tab
SmartBI shows you exactly what type each column is:

```
Column              Type           Non-Null  Unique Values
Year                int64          1000      8
Customer_Age        int64          1000      50
Customer_Status     object         1000      2
Payment_Method      object         1000      5
```

**Legend:**
- `int64`, `float64` → **Numeric** ✓
- `object` → **Categorical** (usually text)
- `datetime64` → **DateTime** (dates/times)

---

## What If I Need to Analyze Text Data?

### Convert Categorical to Numeric
Use the **Data Cleaning Tab**:
1. Go to "🧹 Data Cleaning"
2. Select "Categorical Encoding"
3. One-hot encode your categorical columns
4. Now you can analyze them numerically

**Example:** Encode "Payment_Method" into numeric columns:
```
Payment_Method_Debit Card    → 1 or 0
Payment_Method_Credit Card   → 1 or 0
Payment_Method_Mobile Wallet → 1 or 0
```

### Combine Multiple Values
Use **Feature Engineering**:
1. Create interaction features between numeric columns
2. Create polynomial features for non-linear relationships
3. Create statistical rolling features for time series

---

## Common Questions

### Q: Why can't I analyze Customer_Status in Distribution Analysis?
**A:** It's categorical (text). You can:
1. Count occurrences using Dashboard → Bar Chart
2. Visualize with Dashboard → Pie Chart
3. Analyze customer segments in POS Analysis tab

### Q: Year appears in Distribution Analysis but not my other columns?
**A:** Year is numeric (int). Other columns might be:
- **Text** (object type) - Use categorical charts
- **Dates** (datetime type) - Use time series analysis
- **IDs/Codes** - Treat as categorical

### Q: How do I see ALL available columns?
**A:** Go to "📊 Data Overview" tab:
- See all 13 columns
- Check their types
- See unique values and missing data
- Understand before analyzing

### Q: Can I force text analysis?
**A:** Yes! Use Data Cleaning to:
1. Encode categorical columns to numeric
2. Create dummy variables
3. Then analyze numerically

---

## Summary Table

| Feature | Numeric Cols | Categorical Cols | DateTime Cols |
|---------|:---:|:---:|:---:|
| Distribution | ✓ | ✗ | ✗ |
| Histogram | ✓ | ✗ | ✗ |
| Box Plot (Value) | ✓ | ✗ | ✗ |
| Box Plot (Group) | ✗ | ✓ | ✗ |
| Pie Chart | ✗ | ✓ | ✗ |
| Bar Chart | ✓ or ✗ | ✓ | ✗ |
| Correlation | ✓ | ✗ | ✗ |
| Time Series | ✓ | ✗ | ✓ |
| Scatter Plot | ✓ | ✗ | ✗ |

---

## Updates Made to SmartBI

✅ **Added clarity messages showing:**
- Number of available numeric columns
- Help text explaining why only numeric columns appear
- Guide on data type detection

These updates help you understand exactly why you see certain columns in different sections of the app!

---

**Still seeing fewer columns than expected?**

Check the Data Overview tab to verify:
1. Column data types are correct
2. No columns are being excluded by accident
3. Your data matches expectations

If a column should be numeric but isn't, you can convert it in the Data Cleaning tab!
