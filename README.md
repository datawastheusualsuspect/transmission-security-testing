# Transmission Security Testing with Docker and Kali Linux

This project demonstrates the importance of encrypting data before transmission using Docker containers with a Kali Linux instance for security testing.

## Overview

The setup includes:
- **Target HTTP Service**: Unencrypted data transmission (vulnerable)
- **Target HTTPS Service**: Encrypted data transmission (secure)
- **Kali Linux Container**: Security testing and vulnerability assessment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kali Linux    │    │  HTTP Service   │    │ HTTPS Service   │
│   (Tester)      │◄──►│   (Port 8080)   │◄──►│   (Port 8443)   │
│                 │    │   Unencrypted   │    │   Encrypted     │
│ Security Tools  │    │   Transmission  │    │   Transmission  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

1. **Start the testing environment:**
```bash
docker-compose up -d
```

2. **Run basic security tests:**
```bash
docker exec -it kali-tester bash /tests/test_transmission_security.sh
```

3. **Run advanced security tests:**
```bash
docker exec -it kali-tester python3 /tests/advanced_security_tests.py
```

4. **View results:**
```bash
ls -la results/
```

## Services

### HTTP Service (Port 8080)
- **Endpoint**: `http://localhost:8080`
- **Encryption**: None (Clear Text)
- **Vulnerability**: High - All data transmitted in clear text

### HTTPS Service (Port 8443)
- **Endpoint**: `https://localhost:8443`
- **Encryption**: TLS/SSL with self-signed certificate
- **Vulnerability**: Low - Data encrypted in transit

## API Endpoints

### Common Endpoints
- `GET /health` - Service health check
- `GET /data` - Retrieve sensitive data
- `POST /transmit` - Transmit data to service
- `POST /decrypt` - Decrypt received data (HTTPS only)

### Example Usage

#### HTTP (Unencrypted)
```bash
# Get sensitive data (unencrypted)
curl http://localhost:8080/data

# Transmit data (unencrypted)
curl -X POST http://localhost:8080/transmit \
  -H "Content-Type: application/json" \
  -d '{"data": {"user": "test", "info": "sensitive"}}'
```

#### HTTPS (Encrypted)
```bash
# Get sensitive data (encrypted)
curl -k https://localhost:8443/data

# Transmit data (encrypted)
curl -X POST https://localhost:8443/transmit \
  -k -H "Content-Type: application/json" \
  -d '{"data": {"user": "test", "info": "sensitive"}}'
```

## Security Tests

### Basic Tests (`test_transmission_security.sh`)
- Connectivity testing
- Packet capture analysis
- MITM attack simulation
- SSL/TLS configuration analysis

### Advanced Tests (`advanced_security_tests.py`)
- Comprehensive vulnerability assessment
- Encryption comparison
- Network traffic analysis
- Automated security reporting

## Test Results

Results are saved in the `results/` directory:

### Files Generated
- `security_report.md` - Summary security analysis
- `advanced_security_report.json` - Detailed test results
- `http_capture.pcap` - HTTP packet capture
- `https_capture.pcap` - HTTPS packet capture
- `mitm_http_data.txt` - MITM simulation results
- Various JSON files with service responses

### Key Findings

#### HTTP Service
- ❌ **CRITICAL**: Sensitive data transmitted in clear text
- ❌ **VULNERABLE**: Susceptible to eavesdropping
- ❌ **VULNERABLE**: MITM attacks possible
- ❌ **VULNERABLE**: Session hijacking risk

#### HTTPS Service
- ✅ **SECURE**: Data encrypted during transmission
- ✅ **PROTECTED**: Resists eavesdropping
- ✅ **PROTECTED**: MITM attacks prevented (with cert validation)
- ✅ **SECURE**: Protected session management

## Security Recommendations

### 1. Always Use HTTPS/TLS
- Never transmit sensitive data over HTTP
- Implement proper SSL/TLS configuration
- Use strong cipher suites and disable weak protocols

### 2. Implement Client-Side Encryption
- Encrypt sensitive data before transmission
- Use defense-in-depth approach
- Maintain control over encryption keys

### 3. Certificate Management
- Use properly signed certificates in production
- Implement certificate pinning for critical applications
- Monitor certificate expiration

### 4. Network Security
- Monitor for sensitive data leakage
- Implement intrusion detection systems
- Use network segmentation

## Manual Testing

### Packet Capture Analysis
```bash
# Capture HTTP traffic
tcpdump -i any -A -s 0 'port 8080' -w http_capture.pcap

# Capture HTTPS traffic
tcpdump -i any -A -s 0 'port 8443' -w https_capture.pcap

# Analyze captured packets
tcpdump -r http_capture.pcap -A | grep -i "credit_card\|ssn\|api_key"
```

### SSL/TLS Testing
```bash
# Test SSL configuration
openssl s_client -connect localhost:8443 -servername localhost

# Check supported protocols
for proto in ssl2 ssl3 tls1 tls1_1 tls1_2 tls1_3; do
  echo | openssl s_client -connect localhost:8443 -$proto 2>/dev/null | grep "Protocol"
done
```

## Cleanup

Stop and remove all containers:
```bash
docker-compose down -v
```

Remove generated results:
```bash
rm -rf results/
```

## Educational Purpose

This project is designed for educational purposes to demonstrate:
- The importance of data encryption in transit
- How to test transmission security
- Common vulnerabilities in unencrypted communications
- Best practices for secure data transmission

⚠️ **Warning**: Never expose the HTTP service or sensitive data in production environments.

## Requirements

- Docker
- Docker Compose
- Sufficient disk space for packet captures
- Network access to container ports (8080, 8443)

## License

This project is provided for educational purposes. Use responsibly and only on systems you own or have explicit permission to test.
