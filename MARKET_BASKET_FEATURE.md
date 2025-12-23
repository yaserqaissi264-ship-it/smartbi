# Market Basket Analysis Feature

## Overview
A new **Market Basket Analysis** feature has been added to SmartBI that analyzes which products are frequently purchased together from transaction data.

## What Was Added

### 1. Core Analysis Function
**Location**: `Analyzer.analyze_product_associations()` method
- Parses transaction data from a single column
- Extracts individual products from each transaction
- Calculates product pair frequencies and co-occurrences
- Computes association metrics:
  - **Support**: Percentage of transactions containing both products
  - **Confidence (A→B)**: When A is bought, how often is B also bought?
  - **Confidence (B→A)**: When B is bought, how often is A also bought?
  - **Lift**: How much more likely are products bought together than separately?

### 2. Visualization Functions
**Location**: `Visualizer` class

#### `plot_product_association_network()`
- Creates a network graph showing product relationships
- Node size represents product importance
- Edge thickness shows association strength
- Interactive hover information

#### `plot_product_frequency()`
- Bar chart of most frequently purchased products
- Customizable top N products
- Color-coded by frequency

#### `plot_association_strength()`
- Horizontal bar chart showing top product associations
- Ranked by co-occurrence count
- Shows the strength of each pairing

### 3. New Dashboard Page
**Location**: `market_basket_page()` function in main app

Features:
- **Column Selection**: Choose the transaction column containing product lists
- **Delimiter Configuration**: Specify how products are separated (comma, pipe, etc.)
- **Minimum Support Filter**: Filter associations by minimum support threshold
- **Four Analysis Tabs**:
  1. **Association Table**: Detailed metrics for all associations
  2. **Network View**: Visual product relationship graph
  3. **Product Frequency**: Most purchased products
  4. **Association Strength**: Top product pairings

### 4. Navigation Integration
- Added "🛒 Market Basket" option to the sidebar navigation menu
- Positioned between "Dashboard" and "Forecasting" pages

## How to Use

### Data Format
Your transaction column should contain multiple products in a single cell, separated by a delimiter:

**Example:**
```
Laptop,Mouse,Keyboard
Laptop,Monitor
Mouse,Keyboard
Phone,Case,Screen Protector
Laptop,Mouse
```

### Steps:
1. Go to **📤 Data Upload** and load your dataset
2. Navigate to **🛒 Market Basket** in the sidebar
3. Select your transaction column
4. Choose the delimiter (usually comma)
5. Set minimum support threshold (e.g., 10%)
6. Click **🔍 Analyze Product Associations**

### Output:
- Total transactions and unique products
- Product pairs bought together with frequency
- Association strength metrics
- Visual network of product relationships
- Most popular individual products
- Actionable business insights and recommendations

## Association Metrics Explained

| Metric | Meaning | Use Case |
|--------|---------|----------|
| **Co-occurrence** | How many times products appear together | Identify strong pairings |
| **Support** | % of transactions with both products | Measure popularity |
| **Confidence A→B** | If A bought, % chance B also bought | Understand sequential patterns |
| **Lift** | How much more likely together than random | Identify non-obvious combinations |

## Example Insights

- 🏆 "Strongest Association: Product A and B are bought together 45 times"
- 💰 "Consider bundling Product A with B to boost sales"
- 🌟 "Most Popular: Product X appears in 200 transactions"
- 📊 "Average Co-occurrence: 12.5 transactions per pair"

## Business Applications

1. **Product Bundling**: Create attractive bundles of frequently bought items
2. **Cross-selling**: Recommend complementary products at checkout
3. **Store Layout**: Place associated products near each other
4. **Inventory Planning**: Stock items that are purchased together
5. **Marketing Campaigns**: Create targeted offers for product combinations

## Technical Details

- **Algorithm**: Association Rule Mining using co-occurrence analysis
- **Delimiter Support**: Flexible separator configuration
- **Performance**: Efficient for datasets with thousands of transactions
- **Metrics**: Industry-standard association metrics (support, confidence, lift)
