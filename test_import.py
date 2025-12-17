try:
    exec(open('smartbi_bundle.py').read())
    print("File imported successfully")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
