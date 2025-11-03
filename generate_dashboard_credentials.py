#!/usr/bin/env python3
"""
Generate secure credentials for admin dashboard
Run this once to create your dashboard password
"""

from werkzeug.security import generate_password_hash
import secrets
import sys

def generate_credentials():
    """Generate secure dashboard credentials"""

    print("\n" + "="*60)
    print("DASHBOARD CREDENTIAL GENERATOR")
    print("="*60 + "\n")

    # Generate secret key
    secret_key = secrets.token_hex(32)
    print("Generated SECRET KEY (for session encryption)")
    print(f"DASHBOARD_SECRET_KEY={secret_key}\n")

    # Get username
    username = input("Enter admin username (default: admin): ").strip()
    if not username:
        username = "admin"

    # Get password
    while True:
        password = input("Enter admin password (min 12 characters): ").strip()
        if len(password) < 12:
            print("⚠️  Password too short. Must be at least 12 characters.\n")
            continue

        confirm = input("Confirm password: ").strip()
        if password != confirm:
            print("⚠️  Passwords don't match. Try again.\n")
            continue

        break

    # Generate password hash
    password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    print("\n" + "="*60)
    print("CREDENTIALS GENERATED SUCCESSFULLY")
    print("="*60 + "\n")

    print("Add these lines to your ~/.env file:")
    print("-" * 60)
    print(f"DASHBOARD_SECRET_KEY={secret_key}")
    print(f"ADMIN_USERNAME={username}")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print("-" * 60)

    print("\n⚠️  IMPORTANT:")
    print("1. Copy the lines above to ~/.env on your SERVER")
    print("2. NEVER commit these to git")
    print("3. Keep your password secure")
    print("4. Update .gitignore to exclude .env")

    print("\nTo apply on server:")
    print("  nano ~/.env")
    print("  (paste the lines above)")
    print("  source ~/.env")

    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    try:
        generate_credentials()
    except KeyboardInterrupt:
        print("\n\nCredential generation cancelled.")
        sys.exit(1)
