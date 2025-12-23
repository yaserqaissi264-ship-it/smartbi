# Market Basket Analysis - Quick Start Guide

## What is Market Basket Analysis?

Market Basket Analysis is a technique that identifies which products are frequently purchased together. Instead of analyzing individual columns, it analyzes **relationships between products within each transaction**.

For example:
- 🛒 "Customers who buy Laptop often also buy Mouse and Keyboard"
- 🍔 "People ordering Burger and Fries together 80% of the time"
- 📺 "Netflix and Prime Video subscribers overlap significantly"

## Your Data Format

Your data should have a column with **all products in one cell**, separated by a delimiter:

### ✅ Correct Format
```
Transaction ID | Products
1              | Laptop,Mouse,Keyboard
2              | Monitor,Keyboard
3              | Laptop,Mouse,Monitor
```

### ❌ Incorrect Format (Don't use this)
```
Transaction ID | Product 1  | Product 2  | Product 3
1              | Laptop     | Mouse      | Keyboard
```
(This would just calculate correlations between columns)

## How to Use in SmartBI

### Step 1: Prepare Your Data
- Create a CSV file with a column containing transaction data
- Products in each row should be separated consistently (comma, pipe, semicolon, etc.)
- Ensure product names are consistent (no typos or case differences)

### Step 2: Upload to SmartBI
1. Click **📤 Data Upload**
2. Upload your CSV file
3. Verify the data preview

### Step 3: Run Market Basket Analysis
1. Click **🛒 Market Basket** in the sidebar
2. Select the transaction column (the one with product lists)
3. Enter the product separator (e.g., `,` for comma)
4. Set minimum support (default: 10%)
   - **Lower %** = More associations found (more detailed)
   - **Higher %** = Only strongest associations (summary view)
5. Click **🔍 Analyze Product Associations**

### Step 4: Interpret Results
You'll get 4 different views:

#### 📊 Association Table
Shows all product pairs with metrics:
- **Bought Together**: How many times
- **Support**: % of all transactions
- **Confidence**: If product A bought, how likely is B?
- **Lift**: How much more likely together than random?

#### 🔗 Network View
Visual graph where:
- Nodes = Products
- Lines = Associations
- Thicker lines = Stronger relationships

#### 📈 Product Frequency
Bar chart showing most popular products

#### 💪 Association Strength
Top product pairs ranked by how often bought together

## Understanding the Metrics

| Metric | What It Means | Example |
|--------|---------------|---------|
| **Co-occurrence** | Times products appear together | "A+B: 45 times" |
| **Support** | % of transactions with both | "20% of all transactions" |
| **Confidence A→B** | When A bought, likelihood B bought | "80% confidence: if Laptop, then Mouse" |
| **Lift** | Strength of association | "Lift 2.5: 2.5x more likely together" |

## Real-World Examples

### E-commerce
```
Input: Computer peripherals in shopping carts
Output: Laptop, Mouse, Keyboard are frequently bought together
Action: Create a bundle deal: "Complete PC Setup - Save 15%"
```

### Grocery Store
```
Input: Shopping baskets
Output: Bread, Milk, Butter are bought together
Action: Place these items near each other; Create "Breakfast Bundle"
```

### Streaming Services
```
Input: User subscriptions
Output: Netflix, Prime Video, Disney+ overlap significantly
Action: Recommend bundle offers to users
```

### Restaurant Menu
```
Input: Food orders
Output: Burgers, Fries, Beer are frequently ordered together
Action: Create combo meals; promote add-ons
```

## Tips for Success

### ✅ Good Data
- "Laptop,Mouse,Keyboard" ← Consistent, clean product names
- "Red Shirt,Blue Jeans,White Socks" ← Clear items
- "Apple,Orange,Banana" ← Simple categories

### ❌ Bad Data
- "laptop , mouse , keyboard" ← Extra spaces
- "laptop123,MOUSE,keyboard" ← Inconsistent naming
- "Item 1,Item 2,Item 3" ← No actual product info
- Missing values or empty cells

### 📊 Minimum Support Guide
| % | Use Case | Sample Size |
|---|----------|------------|
| 2% | Exploratory, small dataset | 100-500 transactions |
| 5% | Standard analysis | 500-2000 transactions |
| 10% | Focus on strong patterns | 2000+ transactions |
| 20% | Only major associations | Large dataset (10000+) |

### 💾 Data Preparation Checklist
- [ ] Products are consistently named
- [ ] No extra spaces or special characters
- [ ] Delimiter is consistent throughout
- [ ] At least 100 transactions for reliable results
- [ ] No missing values in the transaction column
- [ ] Product names are meaningful

## Interpreting Results

### High Support + High Confidence = Strong Association
**Example:** Laptop + Mouse: Support 15%, Confidence 90%
- **Meaning**: 15% of customers buy both; When buying Laptop, 90% also buy Mouse
- **Action**: Bundle them; Market together

### High Confidence but Low Support = Niche Association
**Example:** Premium_Laptop + Gold_Case: Support 2%, Confidence 95%
- **Meaning**: Rare, but when it happens, they always go together
- **Action**: Target premium customers; Create exclusive bundles

### High Support but Low Confidence = Coincidence
**Example:** Both popular but not dependent
- **Meaning**: Frequently bought but not together
- **Action**: May not be worth bundling

### High Lift = Non-obvious Association
**Example:** Laptop + Specific Game: Lift 4.0
- **Meaning**: 4x more likely together than random chance
- **Action**: Market this combo to relevant audiences

## Common Questions

**Q: Why don't I see any associations?**
A: Try lowering the minimum support threshold. Some products might naturally be bought less frequently together.

**Q: What if products have different names in different rows?**
A: Standardize your data first. Use Find & Replace to ensure "laptop", "Laptop", "LAPTOP" are all the same.

**Q: Can I use this with more than 2 products?**
A: The current version shows pairs, but it analyzes all transactions with multiple products. You'll see the top combinations.

**Q: What's a good Lift value?**
A: Lift > 1.5 is interesting, Lift > 2.5 is very strong. Lift close to 1 means no real association.

**Q: How many transactions do I need?**
A: Minimum 50-100, but 500+ gives much more reliable results.

## Business Actions

Once you've identified associations, you can:

1. **Create Product Bundles**
   - "Laptop + Mouse + Keyboard Bundle"
   - Offer 10-15% discount

2. **Strategic Product Placement**
   - Place associated items near each other
   - Make customers discover complements

3. **Personalized Recommendations**
   - "Customers who bought this also bought..."
   - Increase average order value

4. **Marketing Campaigns**
   - Target users with relevant offers
   - "Complete your setup" campaigns

5. **Inventory Management**
   - Stock associated items together
   - Predict demand patterns

6. **Cross-selling Strategy**
   - Suggest complementary products at checkout
   - Email campaigns with targeted bundles

## Next Steps

1. **Prepare your transaction data** with all products in one column
2. **Upload to SmartBI** and load the dataset
3. **Navigate to Market Basket** analysis
4. **Explore the visualizations** and metrics
5. **Extract actionable insights** for your business
6. **Download results** as CSV for further analysis

---

**Need help?** Check the MARKET_BASKET_FEATURE.md file for technical details or run market_basket_examples.py to see sample data.

**Happy analyzing! 🎯**
