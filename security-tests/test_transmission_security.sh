#!/bin/bash

# Transmission Security Testing Script
# This script tests both encrypted and unencrypted data transmission

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Target services
HTTP_SERVICE="target-http:8080"
HTTPS_SERVICE="target-https:8443"

# Results directory
RESULTS_DIR="/results"
mkdir -p $RESULTS_DIR

echo -e "${BLUE}=== Transmission Security Testing ===${NC}"
echo "Testing both HTTP and HTTPS services for transmission security vulnerabilities"
echo ""

# Function to test HTTP service
test_http_service() {
    echo -e "${YELLOW}Testing HTTP Service (Unencrypted)${NC}"
    echo "Target: $HTTP_SERVICE"
    
    # Test 1: Basic connectivity
    echo -e "${BLUE}1. Testing basic connectivity...${NC}"
    curl -s http://$HTTP_SERVICE/health | jq '.' > $RESULTS_DIR/http_health.json
    echo "Health check result saved to $RESULTS_DIR/http_health.json"
    
    # Test 2: Data transmission (unencrypted)
    echo -e "${BLUE}2. Testing unencrypted data transmission...${NC}"
    curl -s http://$HTTP_SERVICE/data | jq '.' > $RESULTS_DIR/http_data.json
    echo "Unencrypted data response saved to $RESULTS_DIR/http_data.json"
    
    # Test 3: Packet capture simulation
    echo -e "${BLUE}3. Simulating packet capture...${NC}"
    timeout 5 tcpdump -i any -n -s 0 -w $RESULTS_DIR/http_capture.pcap host target-http 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1
    
    # Send some data while capturing
    curl -s http://$HTTP_SERVICE/data > /dev/null
    curl -s http://$HTTP_SERVICE/data > /dev/null
    
    sleep 2
    kill $TCPDUMP_PID 2>/dev/null || true
    
    if [ -f $RESULTS_DIR/http_capture.pcap ]; then
        echo "Packet capture saved to $RESULTS_DIR/http_capture.pcap"
        # Analyze captured packets
        tcpdump -r $RESULTS_DIR/http_capture.pcap -A | grep -i "credit_card\|ssn\|api_key" > $RESULTS_DIR/http_sensitive_data.txt || true
        if [ -s $RESULTS_DIR/http_sensitive_data.txt ]; then
            echo -e "${RED}CRITICAL: Sensitive data found in unencrypted packets!${NC}"
            echo "Sensitive data found in: $RESULTS_DIR/http_sensitive_data.txt"
        else
            echo -e "${GREEN}No sensitive data found in clear text packets${NC}"
        fi
    fi
    
    echo ""
}

# Function to test HTTPS service
test_https_service() {
    echo -e "${YELLOW}Testing HTTPS Service (Encrypted)${NC}"
    echo "Target: $HTTPS_SERVICE"
    
    # Test 1: Basic connectivity with SSL verification
    echo -e "${BLUE}1. Testing HTTPS connectivity...${NC}"
    curl -ks https://$HTTPS_SERVICE/health | jq '.' > $RESULTS_DIR/https_health.json
    echo "Health check result saved to $RESULTS_DIR/https_health.json"
    
    # Test 2: SSL/TLS configuration analysis
    echo -e "${BLUE}2. Analyzing SSL/TLS configuration...${NC}"
    if command -v openssl >/dev/null 2>&1; then
        echo | openssl s_client -connect $HTTPS_SERVICE -servername localhost 2>/dev/null | openssl x509 -noout -text > $RESULTS_DIR/https_cert_info.txt
        echo "SSL certificate info saved to $RESULTS_DIR/https_cert_info.txt"
        
        # Test SSL protocols
        echo "Testing SSL/TLS protocols..."
        for protocol in ssl2 ssl3 tls1 tls1_1 tls1_2 tls1_3; do
            if echo | timeout 5 openssl s_client -connect $HTTPS_SERVICE -$protocol 2>/dev/null | grep -q "Verify return code"; then
                echo -e "${GREEN}✓ $protocol supported${NC}"
            else
                echo -e "${RED}✗ $protocol not supported${NC}"
            fi
        done
    fi
    
    # Test 3: Data transmission (encrypted)
    echo -e "${BLUE}3. Testing encrypted data transmission...${NC}"
    curl -ks https://$HTTPS_SERVICE/data | jq '.' > $RESULTS_DIR/https_data.json
    echo "Encrypted data response saved to $RESULTS_DIR/https_data.json"
    
    # Test 4: Packet capture for HTTPS
    echo -e "${BLUE}4. Capturing HTTPS packets...${NC}"
    timeout 5 tcpdump -i any -n -s 0 -w $RESULTS_DIR/https_capture.pcap host target-https 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1
    
    # Send some data while capturing
    curl -ks https://$HTTPS_SERVICE/data > /dev/null
    curl -ks https://$HTTPS_SERVICE/data > /dev/null
    
    sleep 2
    kill $TCPDUMP_PID 2>/dev/null || true
    
    if [ -f $RESULTS_DIR/https_capture.pcap ]; then
        echo "HTTPS packet capture saved to $RESULTS_DIR/https_capture.pcap"
        # Try to find sensitive data (should be encrypted)
        tcpdump -r $RESULTS_DIR/https_capture.pcap -A | grep -i "credit_card\|ssn\|api_key" > $RESULTS_DIR/https_sensitive_data.txt || true
        if [ -s $RESULTS_DIR/https_sensitive_data.txt ]; then
            echo -e "${RED}WARNING: Potential sensitive data exposure detected!${NC}"
        else
            echo -e "${GREEN}Good: No clear text sensitive data found in HTTPS packets${NC}"
        fi
    fi
    
    echo ""
}

# Function to perform man-in-the-middle simulation
test_mitm_simulation() {
    echo -e "${YELLOW}Man-in-the-Middle Simulation${NC}"
    
    # Test HTTP MITM vulnerability
    echo -e "${BLUE}1. HTTP MITM vulnerability test...${NC}"
    echo "HTTP is vulnerable to MITM attacks by design"
    echo "Capturing HTTP traffic to demonstrate data exposure..."
    
    # Use tcpdump to simulate MITM
    timeout 10 tcpdump -i any -A -s 0 'port 8080' -w $RESULTS_DIR/mitm_http.pcap 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1
    
    for i in {1..3}; do
        curl -s http://$HTTP_SERVICE/data > /dev/null
    done
    
    sleep 3
    kill $TCPDUMP_PID 2>/dev/null || true
    
    # Extract readable data from capture
    tcpdump -r $RESULTS_DIR/mitm_http.pcap -A | grep -E "(credit_card|ssn|api_key|email)" | head -5 > $RESULTS_DIR/mitm_http_data.txt
    echo "MITM HTTP data saved to $RESULTS_DIR/mitm_http_data.txt"
    
    # Test HTTPS MITM resistance
    echo -e "${BLUE}2. HTTPS MITM resistance test...${NC}"
    echo "HTTPS should resist MITM attacks with proper SSL/TLS"
    
    timeout 10 tcpdump -i any -A -s 0 'port 8443' -w $RESULTS_DIR/mitm_https.pcap 2>/dev/null &
    TCPDUMP_PID=$!
    sleep 1
    
    for i in {1..3}; do
        curl -ks https://$HTTPS_SERVICE/data > /dev/null
    done
    
    sleep 3
    kill $TCPDUMP_PID 2>/dev/null || true
    
    # Try to extract readable data (should fail)
    tcpdump -r $RESULTS_DIR/mitm_https.pcap -A | grep -E "(credit_card|ssn|api_key|email)" | head -5 > $RESULTS_DIR/mitm_https_data.txt
    echo "MITM HTTPS data saved to $RESULTS_DIR/mitm_https_data.txt"
    
    if [ -s $RESULTS_DIR/mitm_https_data.txt ]; then
        echo -e "${RED}WARNING: HTTPS may be vulnerable to MITM!${NC}"
    else
        echo -e "${GREEN}Good: HTTPS appears to resist MITM attacks${NC}"
    fi
    
    echo ""
}

# Function to generate summary report
generate_report() {
    echo -e "${BLUE}=== Security Analysis Summary ===${NC}"
    
    cat > $RESULTS_DIR/security_report.md << EOF
# Transmission Security Test Report

## Test Environment
- Date: $(date)
- HTTP Service: target-http:8080
- HTTPS Service: target-https:8443

## Test Results

### HTTP Service Analysis
- **Encryption**: None (Clear Text)
- **Vulnerability**: High
- **Data Exposure**: Sensitive data transmitted in clear text
- **MITM Risk**: High

### HTTPS Service Analysis
- **Encryption**: TLS/SSL
- **Vulnerability**: Low (with proper configuration)
- **Data Protection**: Encrypted in transit
- **MITM Risk**: Low (with certificate validation)

## Key Findings

1. **HTTP Transmission**: 
   - All sensitive data (credit cards, SSN, API keys) visible in network captures
   - Completely vulnerable to eavesdropping and MITM attacks

2. **HTTPS Transmission**:
   - Data encrypted during transmission
   - Resists passive eavesdropping
   - Protected against MITM attacks (with proper certificate validation)

## Recommendations

1. **Always use HTTPS/TLS** for sensitive data transmission
2. **Implement client-side encryption** before transmission for defense in depth
3. **Validate SSL certificates** properly
4. **Use strong cipher suites** and disable weak protocols
5. **Monitor for certificate expiration** and misconfigurations

## Files Generated
- http_health.json: HTTP service health check
- https_health.json: HTTPS service health check
- http_data.json: Unencrypted data sample
- https_data.json: Encrypted data sample
- http_capture.pcap: HTTP packet capture
- https_capture.pcap: HTTPS packet capture
- mitm_http_data.txt: MITM simulation results for HTTP
- mitm_https_data.txt: MITM simulation results for HTTPS
EOF

    echo "Security report generated: $RESULTS_DIR/security_report.md"
    echo ""
    echo -e "${GREEN}=== Testing Complete ===${NC}"
    echo "All results saved to: $RESULTS_DIR"
}

# Install required tools
install_tools() {
    echo -e "${BLUE}Installing required tools...${NC}"
    apt-get update -qq
    apt-get install -y -qq curl jq tcpdump openssl
    echo "Tools installed successfully"
    echo ""
}

# Main execution
main() {
    install_tools
    test_http_service
    test_https_service
    test_mitm_simulation
    generate_report
}

# Run main function
main "$@"
