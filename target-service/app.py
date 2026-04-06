#!/usr/bin/env python3

import os
import json
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import ssl
import base64

app = Flask(__name__)

# Generate or load encryption key
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# Service configuration
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'Test-Service')
USE_ENCRYPTION = os.environ.get('ENCRYPTION', 'false').lower() == 'true'

# Sample sensitive data
SENSITIVE_DATA = {
    "user_id": "12345",
    "credit_card": "4532-1234-5678-9012",
    "ssn": "123-45-6789",
    "api_key": "sk-1234567890abcdef",
    "personal_info": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "address": "123 Main St, Anytown, USA"
    }
}

def encrypt_data(data):
    """Encrypt data using Fernet symmetric encryption"""
    if isinstance(data, dict):
        data = json.dumps(data)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data):
    """Decrypt data using Fernet symmetric encryption"""
    encrypted_bytes = base64.b64decode(encrypted_data.encode())
    decrypted_data = cipher_suite.decrypt(encrypted_bytes)
    return json.loads(decrypted_data.decode())

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": SERVICE_NAME,
        "encryption_enabled": USE_ENCRYPTION
    })

@app.route('/data', methods=['GET'])
def get_data():
    """Return sensitive data (encrypted or unencrypted based on configuration)"""
    if USE_ENCRYPTION:
        encrypted = encrypt_data(SENSITIVE_DATA)
        return jsonify({
            "status": "success",
            "encrypted": True,
            "data": encrypted,
            "key": ENCRYPTION_KEY  # In production, NEVER expose the key!
        })
    else:
        return jsonify({
            "status": "success",
            "encrypted": False,
            "data": SENSITIVE_DATA
        })

@app.route('/decrypt', methods=['POST'])
def decrypt_endpoint():
    """Decrypt received data (for testing purposes)"""
    if not request.json or 'encrypted_data' not in request.json:
        return jsonify({"error": "Missing encrypted_data field"}), 400
    
    try:
        decrypted = decrypt_data(request.json['encrypted_data'])
        return jsonify({
            "status": "success",
            "decrypted_data": decrypted
        })
    except Exception as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

@app.route('/transmit', methods=['POST'])
def receive_data():
    """Receive and process transmitted data"""
    data = request.json
    
    if USE_ENCRYPTION and 'encrypted_data' in data:
        try:
            decrypted = decrypt_data(data['encrypted_data'])
            return jsonify({
                "status": "success",
                "message": "Encrypted data received and processed",
                "processed_data": decrypted
            })
        except Exception as e:
            return jsonify({"error": f"Failed to decrypt: {str(e)}"}), 400
    elif not USE_ENCRYPTION and 'data' in data:
        return jsonify({
            "status": "success",
            "message": "Unencrypted data received and processed",
            "processed_data": data['data']
        })
    else:
        return jsonify({"error": "Invalid data format"}), 400

if __name__ == '__main__':
    # Determine which port to use based on encryption setting
    port = 8443 if USE_ENCRYPTION else 8080
    
    if USE_ENCRYPTION:
        # Create SSL context for HTTPS
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain('certs/server.crt', 'certs/server.key')
            print(f"Starting {SERVICE_NAME} with HTTPS on port {port}")
            app.run(host='0.0.0.0', port=port, ssl_context=context, debug=True)
        except FileNotFoundError:
            print("SSL certificates not found. Generating self-signed certificates...")
            os.makedirs('certs', exist_ok=True)
            # Generate self-signed certificate
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Import required modules
            import ipaddress
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Org"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Save certificate and key
            with open("certs/server.crt", "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            with open("certs/server.key", "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            print("Self-signed certificates generated successfully")
            app.run(host='0.0.0.0', port=port, ssl_context=('certs/server.crt', 'certs/server.key'), debug=True)
    else:
        print(f"Starting {SERVICE_NAME} with HTTP on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
