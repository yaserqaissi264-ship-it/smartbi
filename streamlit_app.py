"""
Entry point for Streamlit Cloud deployment.
"""
import sys
import os

# Ensure the main module is imported
if __name__ == "__main__":
    # This imports and executes the main app
    exec(open("smartbi_bundle.py").read())

