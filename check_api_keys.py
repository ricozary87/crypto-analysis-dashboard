#!/usr/bin/env python3
import os

# Check API keys configuration
print("API Key Configuration Status:")
print("=" * 40)

# OKX API Keys
okx_api_key = os.environ.get('OKX_API_KEY')
okx_secret_key = os.environ.get('OKX_SECRET_KEY')
okx_passphrase = os.environ.get('OKX_PASSPHRASE')

print(f"OKX_API_KEY: {'✅ Available' if okx_api_key else '❌ Not found'}")
print(f"OKX_SECRET_KEY: {'✅ Available' if okx_secret_key else '❌ Not found'}")
print(f"OKX_PASSPHRASE: {'✅ Available' if okx_passphrase else '❌ Not found'}")

# OpenAI API Key
openai_api_key = os.environ.get('OPENAI_API_KEY')
print(f"OPENAI_API_KEY: {'✅ Available' if openai_api_key else '❌ Not found'}")

# Display key lengths (for verification without exposing values)
if okx_api_key:
    print(f"OKX_API_KEY length: {len(okx_api_key)} characters")
if okx_secret_key:
    print(f"OKX_SECRET_KEY length: {len(okx_secret_key)} characters")
if okx_passphrase:
    print(f"OKX_PASSPHRASE length: {len(okx_passphrase)} characters")
if openai_api_key:
    print(f"OPENAI_API_KEY length: {len(openai_api_key)} characters")

print("\n" + "=" * 40)
print("API Configuration Summary:")
print(f"OKX Configuration: {'✅ Complete' if all([okx_api_key, okx_secret_key, okx_passphrase]) else '⚠️ Incomplete'}")
print(f"OpenAI Configuration: {'✅ Complete' if openai_api_key else '❌ Missing'}")