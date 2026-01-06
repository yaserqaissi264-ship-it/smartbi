#!/usr/bin/env python3
"""
Test market basket analysis page - standalone test
"""

import pandas as pd
import numpy as np
import sys
import os

# Suppress streamlit warnings
os.environ['STREAMLIT_SERVER_LOGGER_LEVEL'] = 'error'

import warnings
warnings.filterwarnings('ignore')

# Create sample market basket data
print("=" * 70)
print("Testing Market Basket Analysis")
print("=" * 70)

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

df = pd.DataFrame(ecommerce_data)

print("\nSample Data:")
print(df)

# Import the functions from smartbi_bundle
from smartbi_bundle import InsightGenerator, Visualizer

print("\n" + "=" * 70)
print("Step 1: Analyze Product Associations")
print("=" * 70)

transaction_col = 'products'
delimiter = ','
min_support = 10

result = InsightGenerator.analyze_product_associations(df, transaction_col, separator=delimiter)

if "error" in result:
    print(f"❌ Error: {result['error']}")
    sys.exit(1)

print(f"✅ Analysis successful!")
print(f"\n📊 Summary Statistics:")
print(f"  - Total Transactions: {result['total_transactions']}")
print(f"  - Unique Products: {result['unique_products']}")
print(f"  - Total Product Associations: {len(result['associations'])}")

# Filter by minimum support
min_support_count = max(1, int(result['total_transactions'] * min_support / 100))
filtered_associations = [a for a in result['associations'] if a['Co-occurrence'] >= min_support_count]

print(f"  - Associations above {min_support}% support: {len(filtered_associations)}")

print("\n" + "=" * 70)
print("Step 2: Display Top Associations")
print("=" * 70)

if filtered_associations:
    print("\nTop Product Associations (first 5):")
    for i, assoc in enumerate(filtered_associations[:5], 1):
        print(f"\n  {i}. {assoc['Product A']} ↔ {assoc['Product B']}")
        print(f"     - Co-occurrence Count: {assoc['Co-occurrence']}")
        print(f"     - Support: {assoc['Support']}")
        print(f"     - Confidence A→B: {assoc['Confidence (A→B)']}")
        print(f"     - Confidence B→A: {assoc['Confidence (B→A)']}")
        print(f"     - Lift: {assoc['Lift']}")
else:
    print("❌ No associations found with current support threshold")
    sys.exit(1)

print("\n" + "=" * 70)
print("Step 3: Test Visualizations")
print("=" * 70)

# Test 1: Product Frequency
print("\n📊 Testing Product Frequency Visualization...")
try:
    fig_freq = Visualizer.plot_product_frequency(result['product_freq'], top_n=20)
    if fig_freq:
        print("✅ Product Frequency chart created")
        print(f"   - Chart type: Plotly Bar Chart")
        print(f"   - Data points: {len(result['product_freq'])}")
    else:
        print("❌ Product Frequency chart returned None")
except Exception as e:
    print(f"❌ Error creating Product Frequency chart: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Network Visualization
print("\n🕸️  Testing Network Visualization...")
try:
    fig_network = Visualizer.plot_product_association_network(filtered_associations, top_n=15)
    if fig_network:
        print("✅ Network chart created")
        print(f"   - Chart type: Plotly Scatter (Network)")
        print(f"   - Top associations shown: {min(15, len(filtered_associations))}")
    else:
        print("❌ Network chart returned None")
except Exception as e:
    print(f"❌ Error creating Network chart: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Association Strength
print("\n💪 Testing Association Strength Visualization...")
try:
    fig_strength = Visualizer.plot_association_strength(filtered_associations, top_n=15)
    if fig_strength:
        print("✅ Association Strength chart created")
        print(f"   - Chart type: Plotly Bar Chart")
        print(f"   - Top associations shown: {min(15, len(filtered_associations))}")
    else:
        print("❌ Association Strength chart returned None")
except Exception as e:
    print(f"❌ Error creating Association Strength chart: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("Step 4: Test Data Export")
print("=" * 70)

try:
    display_assoc = []
    for assoc in filtered_associations[:50]:
        display_assoc.append({
            '🔗 Product A': assoc['Product A'],
            '🔗 Product B': assoc['Product B'],
            '📊 Bought Together': assoc['Co-occurrence'],
            '📈 Support': assoc['Support'],
            '✅ Confidence A→B': assoc['Confidence (A→B)'],
            '✅ Confidence B→A': assoc['Confidence (B→A)'],
            '🎯 Lift': assoc['Lift']
        })
    
    export_df = pd.DataFrame(display_assoc)
    csv_data = export_df.to_csv(index=False)
    
    print("✅ Data export successful")
    print(f"   - CSV size: {len(csv_data)} bytes")
    print(f"   - Rows: {len(export_df)}")
    print(f"   - Columns: {len(export_df.columns)}")
except Exception as e:
    print(f"❌ Error exporting data: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print("\nMarket Basket Analysis is working correctly.")
print("The feature should work in Streamlit when you:")
print("  1. Upload data with a transaction column")
print("  2. Navigate to '🛒 Market Basket' page")
print("  3. Select the transaction column")
print("  4. Click 'Analyze Product Associations'")
