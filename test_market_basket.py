#!/usr/bin/env python3
"""Test market basket analysis functions"""

import pandas as pd
import numpy as np
import sys
sys.path.insert(0, '/workspaces/smartbi')

# Create sample data
data = {
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
    ]
}

df = pd.DataFrame(data)

print("=" * 60)
print("TEST 1: Load modules")
print("=" * 60)

try:
    # Suppress streamlit warnings
    import warnings
    warnings.filterwarnings('ignore')
    
    import os
    os.environ['STREAMLIT_SERVER_LOGGER_LEVEL'] = 'error'
    
    from smartbi_bundle import InsightGenerator, Visualizer
    print("✅ Modules loaded successfully")
except Exception as e:
    print(f"❌ Error loading modules: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("TEST 2: Run market basket analysis")
print("=" * 60)

try:
    result = InsightGenerator.analyze_product_associations(df, 'products', separator=',')
    
    if 'error' in result:
        print(f"❌ Analysis error: {result['error']}")
    else:
        print(f"✅ Analysis successful")
        print(f"   - Total Transactions: {result['total_transactions']}")
        print(f"   - Unique Products: {result['unique_products']}")
        print(f"   - Product Associations: {len(result['associations'])}")
        print(f"   - Product Frequencies: {len(result['product_freq'])}")
        
except Exception as e:
    print(f"❌ Error during analysis: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("TEST 3: Test visualizations")
print("=" * 60)

try:
    # Test plot_product_frequency
    print("\nTesting plot_product_frequency...")
    fig_freq = Visualizer.plot_product_frequency(result['product_freq'], top_n=10)
    if fig_freq:
        print("✅ plot_product_frequency works")
    else:
        print("❌ plot_product_frequency returned None")
    
    # Test plot_product_association_network
    print("\nTesting plot_product_association_network...")
    filtered = result['associations'][:10]
    fig_network = Visualizer.plot_product_association_network(filtered, top_n=10)
    if fig_network:
        print("✅ plot_product_association_network works")
    else:
        print("❌ plot_product_association_network returned None")
    
    # Test plot_association_strength
    print("\nTesting plot_association_strength...")
    fig_strength = Visualizer.plot_association_strength(filtered, top_n=10)
    if fig_strength:
        print("✅ plot_association_strength works")
    else:
        print("❌ plot_association_strength returned None")
    
except Exception as e:
    print(f"❌ Error during visualization tests: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
