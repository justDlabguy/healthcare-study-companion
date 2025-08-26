#!/usr/bin/env python3
"""
JWT Secret Generator

This script generates a cryptographically secure JWT secret key suitable for production use.

Usage:
    python scripts/generate-jwt-secret.py [--length LENGTH] [--format FORMAT]
    
Arguments:
    --length: Length of the secret key in bytes (default: 32)
    --format: Output format (hex, base64, raw) (default: hex)
"""

import secrets
import base64
import argparse
import sys


def generate_jwt_secret(length: int = 32, format_type: str = "hex") -> str:
    """Generate a cryptographically secure JWT secret."""
    
    # Generate random bytes
    secret_bytes = secrets.token_bytes(length)
    
    # Format the secret based on the requested format
    if format_type == "hex":
        return secret_bytes.hex()
    elif format_type == "base64":
        return base64.b64encode(secret_bytes).decode('utf-8')
    elif format_type == "raw":
        return secret_bytes.decode('latin-1')
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def validate_length(length: int) -> None:
    """Validate the secret length."""
    if length < 16:
        raise ValueError("Secret length should be at least 16 bytes for security")
    if length > 128:
        raise ValueError("Secret length should not exceed 128 bytes")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a cryptographically secure JWT secret key"
    )
    parser.add_argument(
        "--length", "-l",
        type=int,
        default=32,
        help="Length of the secret key in bytes (default: 32)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["hex", "base64", "raw"],
        default="hex",
        help="Output format (default: hex)"
    )
    parser.add_argument(
        "--multiple", "-m",
        type=int,
        default=1,
        help="Generate multiple secrets (default: 1)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output the secret(s), no additional text"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate inputs
        validate_length(args.length)
        
        if not args.quiet:
            print(f"Generating {args.multiple} JWT secret(s)...")
            print(f"Length: {args.length} bytes")
            print(f"Format: {args.format}")
            print()
        
        # Generate secret(s)
        for i in range(args.multiple):
            secret = generate_jwt_secret(args.length, args.format)
            
            if args.quiet:
                print(secret)
            else:
                if args.multiple > 1:
                    print(f"Secret {i + 1}: {secret}")
                else:
                    print(f"JWT Secret: {secret}")
        
        if not args.quiet:
            print()
            print("Security recommendations:")
            print("- Store this secret securely in your deployment platform")
            print("- Never commit this secret to version control")
            print("- Use different secrets for different environments")
            print("- Rotate secrets regularly")
            print("- Keep a backup of the secret in a secure location")
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()