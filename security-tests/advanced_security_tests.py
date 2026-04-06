#!/usr/bin/env python3

import requests
import json
import ssl
import socket
import subprocess
import time
import base64
from cryptography.fernet import Fernet
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TransmissionSecurityTester:
    def __init__(self):
        self.http_url = "http://target-http:8080"
        self.https_url = "https://target-https:8443"
        self.results = {}
        
    def test_http_vulnerabilities(self):
        """Test various HTTP vulnerabilities"""
        print("Testing HTTP Service Vulnerabilities...")
        
        results = {
            "service": "HTTP",
            "url": self.http_url,
            "tests": {}
        }
        
        # Test 1: Clear text transmission
        try:
            response = requests.get(f"{self.http_url}/data", timeout=5)
            if response.status_code == 200:
                data = response.json()
                results["tests"]["clear_text_transmission"] = {
                    "status": "VULNERABLE",
                    "description": "Data transmitted in clear text",
                    "evidence": "Sensitive data visible in response"
                }
                results["sample_data"] = data
        except Exception as e:
            results["tests"]["clear_text_transmission"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        # Test 2: Session hijacking risk
        try:
            response = requests.get(f"{self.http_url}/health", timeout=5)
            cookies = response.cookies
            if cookies:
                results["tests"]["session_security"] = {
                    "status": "VULNERABLE",
                    "description": "Session cookies transmitted over HTTP",
                    "cookies": dict(cookies)
                }
            else:
                results["tests"]["session_security"] = {
                    "status": "NO_COOKIES",
                    "description": "No session cookies detected"
                }
        except Exception as e:
            results["tests"]["session_security"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        # Test 3: Data injection possibility
        try:
            malicious_data = {
                "data": {
                    "injection": "<script>alert('XSS')</script>",
                    "sql": "'; DROP TABLE users; --"
                }
            }
            response = requests.post(f"{self.http_url}/transmit", 
                                   json=malicious_data, timeout=5)
            results["tests"]["data_injection"] = {
                "status": "TESTED",
                "description": "Data injection test completed",
                "response_status": response.status_code
            }
        except Exception as e:
            results["tests"]["data_injection"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        self.results["http"] = results
        return results
    
    def test_https_security(self):
        """Test HTTPS security features"""
        print("Testing HTTPS Service Security...")
        
        results = {
            "service": "HTTPS",
            "url": self.https_url,
            "tests": {}
        }
        
        # Test 1: SSL/TLS configuration
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection(("target-https", 8443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname="target-https") as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    results["tests"]["ssl_configuration"] = {
                        "status": "SECURE",
                        "tls_version": version,
                        "cipher_suite": cipher,
                        "certificate": cert
                    }
        except Exception as e:
            results["tests"]["ssl_configuration"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        # Test 2: Encrypted data transmission
        try:
            response = requests.get(f"{self.https_url}/data", 
                                  verify=False, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results["tests"]["encrypted_transmission"] = {
                    "status": "SECURE",
                    "description": "Data transmitted over encrypted channel",
                    "encryption_status": data.get("encrypted", False)
                }
                results["sample_data"] = data
        except Exception as e:
            results["tests"]["encrypted_transmission"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        # Test 3: Certificate validation
        try:
            # Try with strict verification (should fail with self-signed cert)
            requests.get(f"{self.https_url}/data", timeout=5, verify=True)
            results["tests"]["certificate_validation"] = {
                "status": "VALID",
                "description": "Certificate validates successfully"
            }
        except Exception as e:
            results["tests"]["certificate_validation"] = {
                "status": "SELF_SIGNED",
                "description": "Using self-signed certificate (expected in test)",
                "error": str(e)
            }
        
        self.results["https"] = results
        return results
    
    def test_encryption_comparison(self):
        """Compare encryption vs no encryption scenarios"""
        print("Testing Encryption vs No Encryption...")
        
        comparison = {
            "test_scenario": "Data Transmission Security",
            "results": {}
        }
        
        # Test data size and transmission time
        test_data = {
            "user_data": {
                "name": "Test User",
                "email": "test@example.com",
                "sensitive_info": "This is sensitive data that should be protected"
            }
        }
        
        # HTTP transmission test
        try:
            start_time = time.time()
            response = requests.post(f"{self.http_url}/transmit", 
                                   json=test_data, timeout=5)
            http_time = time.time() - start_time
            comparison["results"]["http"] = {
                "transmission_time": http_time,
                "status_code": response.status_code,
                "encryption": "None",
                "security_level": "Low"
            }
        except Exception as e:
            comparison["results"]["http"] = {
                "error": str(e),
                "encryption": "None",
                "security_level": "Low"
            }
        
        # HTTPS transmission test
        try:
            start_time = time.time()
            response = requests.post(f"{self.https_url}/transmit", 
                                   json=test_data, verify=False, timeout=5)
            https_time = time.time() - start_time
            comparison["results"]["https"] = {
                "transmission_time": https_time,
                "status_code": response.status_code,
                "encryption": "TLS/SSL",
                "security_level": "High"
            }
        except Exception as e:
            comparison["results"]["https"] = {
                "error": str(e),
                "encryption": "TLS/SSL",
                "security_level": "High"
            }
        
        # Client-side encryption test
        try:
            key = Fernet.generate_key()
            cipher_suite = Fernet(key)
            
            # Encrypt data before transmission
            encrypted_data = cipher_suite.encrypt(json.dumps(test_data).encode())
            encrypted_b64 = base64.b64encode(encrypted_data).decode()
            
            payload = {"encrypted_data": encrypted_b64}
            
            start_time = time.time()
            response = requests.post(f"{self.https_url}/transmit", 
                                   json=payload, verify=False, timeout=5)
            client_enc_time = time.time() - start_time
            
            comparison["results"]["client_side_encryption"] = {
                "transmission_time": client_enc_time,
                "status_code": response.status_code,
                "encryption": "Client-side + TLS/SSL",
                "security_level": "Very High"
            }
        except Exception as e:
            comparison["results"]["client_side_encryption"] = {
                "error": str(e),
                "encryption": "Client-side + TLS/SSL",
                "security_level": "Very High"
            }
        
        self.results["comparison"] = comparison
        return comparison
    
    def run_network_capture_analysis(self):
        """Analyze network captures for security issues"""
        print("Analyzing Network Captures...")
        
        analysis = {
            "network_analysis": {},
            "security_findings": []
        }
        
        # Analyze HTTP capture if available
        try:
            result = subprocess.run(['tcpdump', '-r', '/results/http_capture.pcap', '-A'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                # Look for sensitive data patterns
                sensitive_patterns = [
                    'credit_card', 'ssn', 'api_key', 'email', 'password'
                ]
                
                found_patterns = []
                for pattern in sensitive_patterns:
                    if pattern.lower() in result.stdout.lower():
                        found_patterns.append(pattern)
                
                analysis["network_analysis"]["http"] = {
                    "status": "ANALYZED",
                    "sensitive_data_found": found_patterns,
                    "risk_level": "HIGH" if found_patterns else "MEDIUM"
                }
                
                if found_patterns:
                    analysis["security_findings"].append({
                        "severity": "HIGH",
                        "issue": "Sensitive data transmitted in clear text over HTTP",
                        "patterns": found_patterns
                    })
        except Exception as e:
            analysis["network_analysis"]["http"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        # Analyze HTTPS capture if available
        try:
            result = subprocess.run(['tcpdump', '-r', '/results/https_capture.pcap', '-A'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.stdout:
                # Look for sensitive data patterns (should not find any in encrypted traffic)
                sensitive_patterns = [
                    'credit_card', 'ssn', 'api_key', 'email', 'password'
                ]
                
                found_patterns = []
                for pattern in sensitive_patterns:
                    if pattern.lower() in result.stdout.lower():
                        found_patterns.append(pattern)
                
                analysis["network_analysis"]["https"] = {
                    "status": "ANALYZED",
                    "sensitive_data_found": found_patterns,
                    "risk_level": "LOW" if not found_patterns else "MEDIUM"
                }
                
                if not found_patterns:
                    analysis["security_findings"].append({
                        "severity": "INFO",
                        "issue": "HTTPS traffic appears to be properly encrypted",
                        "status": "GOOD"
                    })
        except Exception as e:
            analysis["network_analysis"]["https"] = {
                "status": "ERROR",
                "error": str(e)
            }
        
        self.results["network_analysis"] = analysis
        return analysis
    
    def generate_security_report(self):
        """Generate comprehensive security report"""
        print("Generating Security Report...")
        
        report = {
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_tests": 0,
                "vulnerabilities_found": 0,
                "security_recommendations": []
            },
            "detailed_results": self.results
        }
        
        # Count tests and vulnerabilities
        for service, results in self.results.items():
            if isinstance(results, dict) and "tests" in results:
                for test_name, test_result in results["tests"].items():
                    report["summary"]["total_tests"] += 1
                    if test_result.get("status") == "VULNERABLE":
                        report["summary"]["vulnerabilities_found"] += 1
        
        # Generate recommendations
        recommendations = [
            "Always use HTTPS/TLS for sensitive data transmission",
            "Implement client-side encryption for defense in depth",
            "Validate SSL certificates and use strong cipher suites",
            "Monitor network traffic for sensitive data leakage",
            "Use secure session management practices",
            "Implement proper access controls and authentication"
        ]
        
        report["summary"]["security_recommendations"] = recommendations
        
        # Save report
        with open("/results/advanced_security_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"Security report saved to /results/advanced_security_report.json")
        return report
    
    def run_all_tests(self):
        """Run all security tests"""
        print("Starting Comprehensive Transmission Security Tests...")
        print("=" * 60)
        
        self.test_http_vulnerabilities()
        print()
        
        self.test_https_security()
        print()
        
        self.test_encryption_comparison()
        print()
        
        self.run_network_capture_analysis()
        print()
        
        report = self.generate_security_report()
        
        print("=" * 60)
        print("Testing Complete!")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Vulnerabilities Found: {report['summary']['vulnerabilities_found']}")
        print("Detailed report saved to /results/advanced_security_report.json")
        
        return report

if __name__ == "__main__":
    tester = TransmissionSecurityTester()
    tester.run_all_tests()
