"""
Interactive API Setup Script for NanoP

Run this script to configure your Gemini API key.
"""

import os
import sys
from pathlib import Path

# Add project root to path to import nanop
sys.path.insert(0, str(Path(__file__).parent.parent))

from nanop.utils.api_mgmt import set_gemini_key, validate_gemini_key, get_masked_key, load_api_keys

def main():
    print("=" * 60)
    print("      NanoP LCA-TEA: Gemini API Key Setup Tool")
    print("=" * 60)

    # Try loading existing keys
    load_api_keys()
    
    current_key = get_masked_key()
    print(f"\nCurrent Gemini Key: {current_key}")

    # Ask for new key
    new_key = input("\nEnter your Google API Key (leave blank to keep current): ").strip()

    if new_key:
        print("\nSaving key to .env file...")
        set_gemini_key(new_key)
    
    # Validate
    print("\nValidating API key...")
    success, message = validate_gemini_key()
    
    if success:
        print(f"✅ {message}")
        print("\nSetup complete! You can now use LightRAG and AI extraction features.")
    else:
        print(f"❌ {message}")
        print("\nPlease ensure your key is correct and has access to the Gemini API.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(0)
