"""
Sample Usage Example for Market Basket Analysis Feature
========================================================

This file shows how to use the Market Basket Analysis feature with example data.
"""

import pandas as pd

# Example 1: E-commerce Product Purchases
print("=" * 60)
print("Example 1: E-commerce Product Purchases")
print("=" * 60)

ecommerce_data = {
    'transaction_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'products': [
        'Laptop,Mouse,Keyboard',
        'Monitor,HDMI Cable',
        'Laptop,Keyboard',
        'Mouse,USB Hub,Keyboard',
        'Monitor,Keyboard',
        'Laptop,Mouse,Monitor',
        'HDMI Cable,USB Hub',
        'Laptop,Mouse,Keyboard',
        'Monitor,Mouse',
        'USB Hub,Keyboard'
    ],
    'date': pd.date_range('2024-01-01', periods=10, freq='D')
}

df_ecommerce = pd.DataFrame(ecommerce_data)

print("\nSample Data:")
print(df_ecommerce[['transaction_id', 'products']].to_string())
print("\nHow to use in SmartBI:")
print("1. Upload this CSV to SmartBI")
print("2. Navigate to 🛒 Market Basket")
print("3. Select 'products' column")
print("4. Set delimiter to ','")
print("5. Run analysis")
print("\nExpected Findings:")
print("- Laptop, Mouse, Keyboard are frequently bought together")
print("- Strong association between Laptop and Mouse")
print("- Monitor and Keyboard have good co-occurrence")

# Example 2: Grocery Store Purchases
print("\n" + "=" * 60)
print("Example 2: Grocery Store Purchases")
print("=" * 60)

grocery_data = {
    'transaction_id': range(1, 11),
    'items': [
        'Bread|Milk|Butter',
        'Apples|Oranges|Bananas',
        'Bread|Cheese|Butter',
        'Milk|Yogurt|Cheese',
        'Apples|Flour',
        'Bread|Milk',
        'Yogurt|Cheese|Butter',
        'Apples|Bananas|Oranges',
        'Bread|Butter|Cheese',
        'Milk|Yogurt'
    ]
}

df_grocery = pd.DataFrame(grocery_data)

print("\nSample Data (with pipe delimiter):")
print(df_grocery[['transaction_id', 'items']].to_string())
print("\nHow to use in SmartBI:")
print("1. Upload this CSV to SmartBI")
print("2. Navigate to 🛒 Market Basket")
print("3. Select 'items' column")
print("4. Set delimiter to '|'")
print("5. Run analysis")
print("\nExpected Findings:")
print("- Bread, Milk, Butter are frequently bought together")
print("- Dairy products (Milk, Cheese, Yogurt, Butter) have high co-occurrence")
print("- Fruits (Apples, Bananas, Oranges) are often purchased together")

# Example 3: Restaurant Menu Orders
print("\n" + "=" * 60)
print("Example 3: Restaurant Menu Orders")
print("=" * 60)

restaurant_data = {
    'order_id': range(1, 11),
    'ordered_items': [
        'Burger,Fries,Coke',
        'Pasta,Salad,Wine',
        'Burger,Fries,Beer',
        'Pasta,Salad,Dessert',
        'Pizza,Beer',
        'Burger,Coke',
        'Pasta,Wine,Dessert',
        'Pizza,Beer,Dessert',
        'Burger,Fries,Beer',
        'Pasta,Salad,Wine,Dessert'
    ]
}

df_restaurant = pd.DataFrame(restaurant_data)

print("\nSample Data:")
print(df_restaurant[['order_id', 'ordered_items']].to_string())
print("\nHow to use in SmartBI:")
print("1. Upload this CSV to SmartBI")
print("2. Navigate to 🛒 Market Basket")
print("3. Select 'ordered_items' column")
print("4. Set delimiter to ','")
print("5. Run analysis")
print("\nExpected Findings:")
print("- Burger, Fries, Beer are frequently ordered together")
print("- Pasta pairs well with Salad and Wine")
print("- Dessert is often ordered with Wine")

# Example 4: Movie Subscription Combinations
print("\n" + "=" * 60)
print("Example 4: Movie Subscription Combinations")
print("=" * 60)

subscription_data = {
    'user_id': range(1, 11),
    'subscriptions': [
        'Netflix,Disney+,Prime Video',
        'HBO Max,Apple TV',
        'Netflix,Prime Video',
        'Netflix,Disney+,HBO Max',
        'Prime Video,Apple TV',
        'Netflix,HBO Max',
        'Disney+,Apple TV,Prime Video',
        'Netflix,Prime Video,HBO Max',
        'Disney+,HBO Max',
        'Netflix,Apple TV,Prime Video'
    ]
}

df_subscription = pd.DataFrame(subscription_data)

print("\nSample Data:")
print(df_subscription[['user_id', 'subscriptions']].to_string())
print("\nHow to use in SmartBI:")
print("1. Upload this CSV to SmartBI")
print("2. Navigate to 🛒 Market Basket")
print("3. Select 'subscriptions' column")
print("4. Set delimiter to ','")
print("5. Run analysis")
print("\nExpected Findings:")
print("- Netflix and Prime Video are frequently subscribed together")
print("- HBO Max often pairs with Netflix")
print("- Disney+ subscribers often have Prime Video")

# Tips for Best Results
print("\n" + "=" * 60)
print("Tips for Best Results")
print("=" * 60)
print("""
1. **Data Quality**:
   - Ensure products are consistently named (e.g., "Laptop" not "laptop", "LAPTOP")
   - Remove leading/trailing spaces
   - Use consistent delimiter throughout

2. **Minimum Support**:
   - Start with 5-10% for exploration
   - Increase to 20-30% for strong associations only
   - Decrease for detailed analysis

3. **Data Size**:
   - Works best with 100+ transactions
   - Works efficiently with 10,000+ transactions
   - Can handle 100,000+ transactions

4. **Interpretation**:
   - High Support + High Lift = Strong, popular association
   - High Confidence = Good predictability
   - Look for actionable insights in top associations

5. **Business Actions**:
   - Bundle frequently bought items
   - Cross-sell in marketing campaigns
   - Optimize store layout
   - Adjust inventory levels
   - Create targeted recommendations
""")

print("✨ Ready to analyze your product associations in SmartBI!")
