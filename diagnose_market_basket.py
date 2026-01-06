#!/usr/bin/env python3
"""
Diagnostic script to identify market basket data format issues
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from smartbi_bundle import InsightGenerator

print("=" * 70)
print("Market Basket Analysis - DIAGNOSTIC TEST")
print("=" * 70)

# Test Case 1: Data with single products per transaction
print("\n📋 TEST 1: Single products per transaction (no associations)")
print("-" * 70)

data1 = {
    'products': ['Laptop', 'Mouse', 'Keyboard', 'Monitor']
}
df1 = pd.DataFrame(data1)

print("Data:")
print(df1)

result1 = InsightGenerator.analyze_product_associations(df1, 'products', separator=',')
print(f"\nResult: {len(result1.get('associations', []))} associations found")
print("⚠️  This is expected - each transaction has only 1 product\n")

# Test Case 2: Data with comma-separated products
print("📋 TEST 2: Comma-separated products (correct format)")
print("-" * 70)

data2 = {
    'products': ['Laptop,Mouse', 'Mouse,Keyboard', 'Laptop,Keyboard', 'Monitor,Mouse']
}
df2 = pd.DataFrame(data2)

print("Data:")
print(df2)

result2 = InsightGenerator.analyze_product_associations(df2, 'products', separator=',')
print(f"\nResult: {len(result2.get('associations', []))} associations found")
if result2.get('associations'):
    print("✅ GOOD - Associations found!")
    for a in result2['associations'][:3]:
        print(f"  - {a['Product A']} + {a['Product B']}: {a['Co-occurrence']} times")

# Test Case 3: Data with spaces after commas
print("\n📋 TEST 3: Products with spaces (common issue)")
print("-" * 70)

data3 = {
    'products': ['Laptop, Mouse', 'Mouse, Keyboard', 'Laptop, Keyboard', 'Monitor, Mouse']
}
df3 = pd.DataFrame(data3)

print("Data:")
print(df3)

result3 = InsightGenerator.analyze_product_associations(df3, 'products', separator=',')
print(f"\nResult: {len(result3.get('associations', []))} associations found")
if result3.get('associations'):
    print("✅ Associations found (spaces are handled)")
else:
    print("❌ NO associations found - might be space issue")
    if result3.get('product_freq'):
        print("\nProducts detected:")
        for p, count in result3['product_freq'][:5]:
            print(f"  - '{p}' (count: {count})")

# Test Case 4: Different delimiter (pipe separated)
print("\n📋 TEST 4: Pipe-separated products")
print("-" * 70)

data4 = {
    'products': ['Laptop|Mouse', 'Mouse|Keyboard', 'Laptop|Keyboard', 'Monitor|Mouse']
}
df4 = pd.DataFrame(data4)

print("Data:")
print(df4)

result4 = InsightGenerator.analyze_product_associations(df4, 'products', separator='|')
print(f"\nResult: {len(result4.get('associations', []))} associations found")
if result4.get('associations'):
    print("✅ Associations found with pipe delimiter!")

# Test Case 5: Empty or null values
print("\n📋 TEST 5: With null/empty values")
print("-" * 70)

data5 = {
    'products': ['Laptop,Mouse', None, 'Mouse,Keyboard', '', 'Laptop,Keyboard']
}
df5 = pd.DataFrame(data5)

print("Data:")
print(df5)

result5 = InsightGenerator.analyze_product_associations(df5, 'products', separator=',')
print(f"\nResult: {len(result5.get('associations', []))} associations found")
print("✅ Nulls are handled gracefully")

print("\n" + "=" * 70)
print("DIAGNOSIS GUIDE")
print("=" * 70)

print("""
If you're getting "No associations found", check:

1. ❌ Each row has ONLY 1 product (no combinations)
   → You need multiple products per transaction
   
2. ❌ Wrong delimiter 
   → If products are separated by '|' but you select ','
   → Try: pipe (|), semicolon (;), or tab
   
3. ❌ Extra spaces around products
   → 'Laptop, Mouse' instead of 'Laptop,Mouse'
   → The code strips spaces automatically, so this should work
   
4. ❌ Empty or mostly null values in the column
   → Check that your product column has actual data
   
5. ❌ Very few transactions with few co-occurrences
   → Lower the minimum support threshold to 1%

SOLUTION: Describe your data format and I'll create a test file!
""")
