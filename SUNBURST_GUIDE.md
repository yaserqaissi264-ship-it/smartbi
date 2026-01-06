# Sunburst (Categorical) Chart - Fixed!
## Understanding Hierarchical Visualization

### ✅ **What Was Fixed**
The sunburst chart now has:
- ✅ Error handling to prevent crashes
- ✅ Proper hierarchical data structure
- ✅ Helpful tips when something goes wrong
- ✅ Clear column type requirements

---

## 📊 **How to Use Sunburst Charts**

### **The 3 Required Inputs**

#### 1️⃣ **Level 1** (First Category)
**What:** A categorical column (text/categories)
- Examples: Payment_Method, Customer_Status, Day_of_Week, Primary_Item_Category

#### 2️⃣ **Level 2** (Second Category)
**What:** Another categorical column (text/categories)
- Examples: Payment_Method, Day_of_Week, Customer_Status
- Must be different from Level 1

#### 3️⃣ **Values** (Numeric Aggregation)
**What:** A numeric column that will be SUMMED/AGGREGATED
- Examples: Total_Amount, Items, Revenue, Count
- This is what determines the size of each slice

---

## ❌ **Why Your Selection Failed**

You selected:
- **Level 1:** Transaction_ID (text)
- **Level 2:** Date (text) 
- **Values:** Year (text - this is the problem!)

### **The Issue**
Year is **categorical** (text), not numeric. Sunburst needs a number to sum up!

### **The Solution**
Select a **numeric column** for Values:
- ✅ Total_Amount_JOD (numbers: 100, 150, 200...)
- ✅ Items (numbers: 1, 2, 3, 4...)
- ✅ Customer_Age (numbers: 25, 30, 35...)

---

## ✅ **Correct Examples**

### Example 1: Payment Method by Day
```
Level 1:  Payment_Method
Level 2:  Day_of_Week
Values:   Total_Amount_JOD

Result: Sunburst showing:
├─ Credit Card
│  ├─ Monday (sum of amounts)
│  ├─ Tuesday (sum of amounts)
│  └─ ...
├─ Debit Card
│  ├─ Monday (sum of amounts)
│  └─ ...
└─ Mobile Wallet
   └─ ...
```

### Example 2: Category by Customer Status
```
Level 1:  Primary_Item_Category
Level 2:  Customer_Status
Values:   Items (count)

Result: Sunburst showing:
├─ Gaming PCs
│  ├─ New Customers (total items)
│  └─ Returning Customers (total items)
├─ Monitors
│  ├─ New Customers (total items)
│  └─ Returning Customers (total items)
└─ ...
```

### Example 3: Day by Customer Status
```
Level 1:  Day_of_Week
Level 2:  Customer_Status
Values:   Total_Amount_JOD

Result: Sunburst showing:
├─ Monday
│  ├─ New (total revenue)
│  └─ Returning (total revenue)
├─ Tuesday
│  ├─ New (total revenue)
│  └─ Returning (total revenue)
└─ ...
```

---

## 📋 **Column Type Reference**

### ✅ **Categorical Columns** (Text/Categories)
Can be used for **Level 1** or **Level 2**:
- Transaction_ID
- Date
- Day_of_Week
- Customer_Status
- Payment_Method
- Primary_Item_Category
- Time

### 🔢 **Numeric Columns** (Numbers)
Can be used for **Values**:
- Year
- Customer_ID (if it's numeric)
- Customer_Age
- Items
- Total_Amount_JOD

---

## 🎯 **How Sunburst Works**

### **The Hierarchy**
```
                    ROOT (Total)
                       |
                ┌───────┼───────┐
            Level 1A   Level 1B  Level 1C
              |          |         |
          ┌───┴───┐   ┌──┴──┐   ┌─┴─┐
        L2-A1   L2-A2 L2-B1 L2-B2 L2-C1 L2-C2
        
Each slice size = sum of numeric values
```

### **Example: Real Data**
```
Payment_Method (Level 1) → Day_of_Week (Level 2) → Total_Amount_JOD (Size)

                    Total Revenue
                      (5,000 JOD)
                         |
            ┌────────────┼────────────┐
        Credit Card    Debit Card   Mobile Wallet
        (2,000 JOD)    (2,000 JOD)   (1,000 JOD)
           |              |             |
        ┌──┴──┐        ┌──┴──┐      ┌──┴──┐
       Mon   Tue      Mon   Tue    Mon   Tue
      400   300      500   400     300   200
```

---

## 💡 **Tips for Using Sunburst**

### **1. Choose Meaningful Hierarchies**
✅ **Good:**
- Payment Method → Day of Week → Revenue
- Product Category → Customer Status → Items Sold
- Month → Day → Total Sales

❌ **Bad:**
- Transaction_ID → Date → Year (too granular, unclear relationship)
- Random categories → Random categories → Values

### **2. Use Aggregation Columns**
✅ **Good Values:**
- Total_Amount (sums up spending)
- Items (counts products)
- Revenue (financial metric)

❌ **Bad Values:**
- Transaction_ID (doesn't make sense to sum)
- Date (not numeric)
- Year (categorical, not numeric)

### **3. Consider the Data Volume**
- If you have too many unique Level 1 values, chart gets crowded
- Example: 100+ different products → hard to read
- Try limiting to top categories first

### **4. Interactive Features**
- 🔄 Click any slice to zoom in/out
- 👆 Hover to see exact values
- 🔙 Click center to go back up levels

---

## 📊 **Real-World Sunburst Examples**

### Retail Analysis
```
Level 1: Product_Category
Level 2: Store_Location
Values:  Sales_Amount

Insight: Which product categories sell best in which stores?
```

### Customer Analysis
```
Level 1: Customer_Segment
Level 2: Purchase_Channel
Values:  Total_Purchases

Insight: How different customer types buy through different channels?
```

### Time Analysis
```
Level 1: Month
Level 2: Product_Type
Values:  Revenue

Insight: Which products drive revenue in different months?
```

---

## ⚠️ **Error Messages & Solutions**

### Error: "Need at least 2 categorical columns"
**Solution:**
- Check your dataset has categorical columns
- Go to Data Overview to see column types
- Text columns are categorical ✓
- Numeric columns are not categorical ✗

### Error: "No numeric column for values"
**Solution:**
- Select a numeric column for Values
- Numbers like: 100, 150, 200
- Not text like: "High", "Low", "Medium"

### Error: "Invalid hierarchy"
**Solution:**
- Make sure Level 1 ≠ Level 2
- Both must be different categorical columns
- Values must be numeric

---

## **Summary Table**

| Component | Type | Example | Valid? |
|-----------|------|---------|--------|
| Level 1 | Categorical | Payment_Method | ✅ |
| Level 2 | Categorical | Day_of_Week | ✅ |
| Values | Numeric | Total_Amount | ✅ |
| Level 1 | Numeric | Year | ❌ |
| Level 2 | Numeric | Items | ❌ |
| Values | Categorical | Status | ❌ |

---

## **Your Data - Perfect Examples**

### ✅ **Good Combinations**
1. Payment_Method → Day_of_Week → Total_Amount_JOD
2. Primary_Item_Category → Customer_Status → Items
3. Customer_Status → Day_of_Week → Total_Amount_JOD
4. Primary_Item_Category → Payment_Method → Customer_Age (avg)

### ❌ **Bad Combinations**
1. Transaction_ID → Date → Year (all text, no numeric)
2. Date → Time → Year (no aggregation column)
3. Year → Month → Items (Year/Month aren't in your data)

---

**Your sunburst chart is now fixed and ready to use!** 📊