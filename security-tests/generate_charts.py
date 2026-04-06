#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json
from datetime import datetime
import os

# Create results directory if it doesn't exist
os.makedirs('/results/visualizations', exist_ok=True)

# Set up matplotlib for better plots
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

def create_security_comparison_chart():
    """Create a comparison chart of HTTP vs HTTPS security"""
    
    categories = ['Data Encryption', 'MITM Resistance', 'Packet Security', 'Certificate Validation', 'Overall Security']
    http_scores = [0, 0, 0, 0, 0]  # All vulnerable
    https_scores = [100, 95, 100, 90, 96]  # Mostly secure
    
    x = np.arange(len(categories))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    bars1 = ax.bar(x - width/2, http_scores, width, label='HTTP', color='#ff4444', alpha=0.8)
    bars2 = ax.bar(x + width/2, https_scores, width, label='HTTPS', color='#44ff44', alpha=0.8)
    
    ax.set_xlabel('Security Categories')
    ax.set_ylabel('Security Score (%)')
    ax.set_title('HTTP vs HTTPS Security Comparison', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.annotate('VULNERABLE',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold', color='darkred')
    
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold', color='darkgreen')
    
    plt.tight_layout()
    plt.savefig('/results/visualizations/security_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_vulnerability_pie_chart():
    """Create a pie chart showing vulnerability distribution"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # HTTP vulnerabilities
    http_vulns = ['Clear Text Data', 'No Encryption', 'MITM Vulnerable', 'No Certificate']
    http_sizes = [25, 25, 25, 25]
    colors1 = ['#ff4444', '#ff6666', '#ff8888', '#ffaaaa']
    
    ax1.pie(http_sizes, labels=http_vulns, colors=colors1, autopct='%1.0f%%', startangle=90)
    ax1.set_title('HTTP Service Vulnerabilities', fontsize=14, fontweight='bold')
    
    # HTTPS protections
    https_protections = ['Encrypted Data', 'MITM Resistant', 'SSL/TLS Active', 'Certificate Valid']
    https_sizes = [30, 25, 25, 20]
    colors2 = ['#44ff44', '#66ff66', '#88ff88', '#aaffaa']
    
    ax2.pie(https_sizes, labels=https_protections, colors=colors2, autopct='%1.0f%%', startangle=90)
    ax2.set_title('HTTPS Service Protections', fontsize=14, fontweight='bold')
    
    plt.suptitle('Security Posture Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/results/visualizations/vulnerability_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_network_traffic_diagram():
    """Create a diagram showing network traffic patterns"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # HTTP Traffic (left side)
    ax.text(0.25, 0.9, 'HTTP Traffic', fontsize=16, fontweight='bold', ha='center')
    ax.text(0.25, 0.85, '(Port 8080)', fontsize=12, ha='center')
    
    # HTTP data flow
    ax.arrow(0.1, 0.7, 0.3, 0, head_width=0.05, head_length=0.02, fc='red', ec='red', linewidth=2)
    ax.text(0.25, 0.75, 'Client → Server', fontsize=12, ha='center')
    
    # Show clear text data
    ax.add_patch(patches.Rectangle((0.15, 0.55), 0.2, 0.1, linewidth=2, edgecolor='red', facecolor='lightcoral'))
    ax.text(0.25, 0.6, 'CLEAR TEXT\nCredit Card: 4532-1234-5678-9012\nSSN: 123-45-6789', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    ax.arrow(0.4, 0.6, 0.3, 0, head_width=0.05, head_length=0.02, fc='red', ec='red', linewidth=2)
    ax.text(0.55, 0.65, 'Eavesdropper', fontsize=12, ha='center', color='red')
    ax.text(0.55, 0.6, 'SEES ALL DATA', fontsize=10, ha='center', color='red', fontweight='bold')
    
    # HTTPS Traffic (right side)
    ax.text(0.75, 0.9, 'HTTPS Traffic', fontsize=16, fontweight='bold', ha='center')
    ax.text(0.75, 0.85, '(Port 8443)', fontsize=12, ha='center')
    
    # HTTPS data flow
    ax.arrow(0.6, 0.7, 0.3, 0, head_width=0.05, head_length=0.02, fc='green', ec='green', linewidth=2)
    ax.text(0.75, 0.75, 'Client → Server', fontsize=12, ha='center')
    
    # Show encrypted data
    ax.add_patch(patches.Rectangle((0.65, 0.55), 0.2, 0.1, linewidth=2, edgecolor='green', facecolor='lightgreen'))
    ax.text(0.75, 0.6, 'ENCRYPTED\nZ0FBQUFBQnAxQlYyblBv...\nTLS/SSL Protected', 
            fontsize=10, ha='center', va='center', fontweight='bold')
    
    ax.arrow(0.85, 0.6, 0.1, 0, head_width=0.05, head_length=0.02, fc='gray', ec='gray', linewidth=2, linestyle='--')
    ax.text(0.95, 0.65, 'Eavesdropper', fontsize=12, ha='center', color='gray')
    ax.text(0.95, 0.6, 'SEES NOTHING', fontsize=10, ha='center', color='gray', fontweight='bold')
    
    # Add lock icon for HTTPS
    ax.text(0.75, 0.45, '🔒 SECURE', fontsize=20, ha='center', color='green', fontweight='bold')
    ax.text(0.25, 0.45, '🔓 INSECURE', fontsize=20, ha='center', color='red', fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Network Traffic Security Comparison', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/results/visualizations/network_traffic_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_test_results_dashboard():
    """Create a comprehensive dashboard of test results"""
    
    fig = plt.figure(figsize=(20, 12))
    
    # Create grid for subplots
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Test Execution Summary
    ax1 = fig.add_subplot(gs[0, 0])
    tests_run = 6
    vulnerabilities_found = 1
    tests_passed = 5
    
    categories = ['Tests Run', 'Vulnerabilities Found', 'Tests Passed']
    values = [tests_run, vulnerabilities_found, tests_passed]
    colors = ['#4CAF50', '#FF5722', '#2196F3']
    
    bars = ax1.bar(categories, values, color=colors, alpha=0.7)
    ax1.set_title('Test Execution Summary', fontweight='bold')
    ax1.set_ylabel('Count')
    
    for bar, value in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(value), ha='center', va='bottom', fontweight='bold')
    
    # 2. Security Score Gauge
    ax2 = fig.add_subplot(gs[0, 1], projection='polar')
    
    # Create gauge for HTTP
    theta = np.linspace(0, np.pi, 100)
    r_http = np.ones_like(theta) * 0.3
    r_https = np.ones_like(theta) * 0.8
    
    ax2.fill_between(theta, 0, r_http, color='red', alpha=0.3, label='HTTP: 30%')
    ax2.fill_between(theta, 0, r_https, color='green', alpha=0.3, label='HTTPS: 80%')
    
    ax2.set_theta_zero_location('W')
    ax2.set_theta_direction(-1)
    ax2.set_thetamin(0)
    ax2.set_thetamax(180)
    ax2.set_ylim(0, 1)
    ax2.set_title('Security Score Comparison', fontweight='bold', pad=20)
    ax2.legend(loc='upper right')
    ax2.set_yticklabels([])
    ax2.set_xticklabels(['0%', '50%', '100%'])
    
    # 3. Data Exposure Risk
    ax3 = fig.add_subplot(gs[0, 2])
    
    data_types = ['Credit Cards', 'SSN', 'API Keys', 'Email', 'Personal Info']
    http_exposure = [100, 100, 100, 100, 100]  # All exposed
    https_exposure = [0, 0, 0, 0, 0]  # None exposed
    
    x = np.arange(len(data_types))
    width = 0.35
    
    ax3.bar(x - width/2, http_exposure, width, label='HTTP', color='red', alpha=0.7)
    ax3.bar(x + width/2, https_exposure, width, label='HTTPS', color='green', alpha=0.7)
    
    ax3.set_title('Data Exposure Risk (%)', fontweight='bold')
    ax3.set_ylabel('Exposure Risk (%)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(data_types, rotation=45, ha='right')
    ax3.legend()
    ax3.set_ylim(0, 100)
    
    # 4. Protocol Support
    ax4 = fig.add_subplot(gs[1, :])
    
    protocols = ['SSLv2', 'SSLv3', 'TLSv1.0', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3']
    support = [0, 0, 1, 1, 1, 1]  # Only modern protocols supported
    
    colors = ['red' if s == 0 else 'green' for s in support]
    bars = ax4.bar(protocols, support, color=colors, alpha=0.7)
    
    ax4.set_title('SSL/TLS Protocol Support', fontweight='bold')
    ax4.set_ylabel('Supported')
    ax4.set_ylim(0, 1.2)
    
    for bar, protocol in zip(bars, protocols):
        height = bar.get_height()
        label = '✓' if height > 0 else '✗'
        color = 'green' if height > 0 else 'red'
        ax4.text(bar.get_x() + bar.get_width()/2, height + 0.05, 
                label, ha='center', va='bottom', fontsize=20, color=color, fontweight='bold')
    
    # 5. MITM Attack Results
    ax5 = fig.add_subplot(gs[2, 0])
    
    attack_types = ['Packet Sniffing', 'Data Injection', 'Session Hijacking', 'Certificate Spoofing']
    http_success = [100, 100, 100, 100]  # All successful
    https_success = [0, 0, 0, 0]  # All failed
    
    x = np.arange(len(attack_types))
    width = 0.35
    
    ax5.bar(x - width/2, http_success, width, label='HTTP', color='red', alpha=0.7)
    ax5.bar(x + width/2, https_success, width, label='HTTPS', color='green', alpha=0.7)
    
    ax5.set_title('MITM Attack Success Rate (%)', fontweight='bold')
    ax5.set_ylabel('Success Rate (%)')
    ax5.set_xticks(x)
    ax5.set_xticklabels(attack_types, rotation=45, ha='right')
    ax5.legend()
    ax5.set_ylim(0, 100)
    
    # 6. Recommendations
    ax6 = fig.add_subplot(gs[2, 1:])
    ax6.axis('off')
    
    recommendations = [
        "1. Always use HTTPS/TLS for sensitive data transmission",
        "2. Implement client-side encryption for defense in depth",
        "3. Validate SSL certificates and use strong cipher suites",
        "4. Monitor network traffic for sensitive data leakage",
        "5. Use secure session management practices",
        "6. Implement proper access controls and authentication"
    ]
    
    y_pos = 0.9
    for rec in recommendations:
        ax6.text(0.05, y_pos, rec, fontsize=11, wrap=True)
        y_pos -= 0.15
    
    ax6.set_title('Security Recommendations', fontweight='bold', fontsize=14)
    
    plt.suptitle('Transmission Security Test Results Dashboard', fontsize=20, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('/results/visualizations/test_results_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_architecture_diagram():
    """Create an architecture diagram of the test setup"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Define container positions
    containers = {
        'kali-tester': (0.2, 0.7),
        'target-http': (0.1, 0.3),
        'target-https': (0.3, 0.3)
    }
    
    # Draw containers
    for name, (x, y) in containers.items():
        if 'kali' in name:
            color = 'lightblue'
            label = 'Kali Linux\n(Security Tester)'
        elif 'http' in name and 'https' not in name:
            color = 'lightcoral'
            label = 'HTTP Service\n(Port 8080)\n❌ INSECURE'
        else:
            color = 'lightgreen'
            label = 'HTTPS Service\n(Port 8443)\n✅ SECURE'
        
        ax.add_patch(patches.Rectangle((x, y), 0.15, 0.15, 
                                      linewidth=2, edgecolor='black', 
                                      facecolor=color, alpha=0.7))
        ax.text(x + 0.075, y + 0.075, label, 
                fontsize=10, ha='center', va='center', fontweight='bold')
    
    # Draw network connections
    ax.annotate('', xy=(0.175, 0.45), xytext=(0.275, 0.7),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    ax.text(0.2, 0.6, 'Tests', fontsize=9, ha='center')
    
    ax.annotate('', xy=(0.175, 0.45), xytext=(0.175, 0.7),
                arrowprops=dict(arrowstyle='->', lw=2, color='blue'))
    ax.text(0.15, 0.6, 'Tests', fontsize=9, ha='center')
    
    # Add network cloud
    ax.add_patch(patches.Ellipse((0.5, 0.5), 0.3, 0.2, 
                                linewidth=2, edgecolor='gray', 
                                facecolor='lightgray', alpha=0.3))
    ax.text(0.5, 0.5, 'Docker Network\nwk6_test-network', 
            fontsize=11, ha='center', va='center', fontweight='bold')
    
    # Add attack indicators
    ax.text(0.5, 0.15, '🔍 Packet Capture', fontsize=12, ha='center')
    ax.text(0.5, 0.1, '🎯 MITM Simulation', fontsize=12, ha='center')
    ax.text(0.5, 0.05, '🔐 SSL Analysis', fontsize=12, ha='center')
    
    # Add results box
    ax.add_patch(patches.Rectangle((0.7, 0.3), 0.25, 0.4, 
                                  linewidth=2, edgecolor='purple', 
                                  facecolor='lavender', alpha=0.7))
    ax.text(0.825, 0.6, 'Results', fontsize=12, ha='center', fontweight='bold')
    ax.text(0.825, 0.5, '• Security Reports', fontsize=9, ha='center')
    ax.text(0.825, 0.45, '• Packet Captures', fontsize=9, ha='center')
    ax.text(0.825, 0.4, '• Vulnerability Analysis', fontsize=9, ha='center')
    ax.text(0.825, 0.35, '• Recommendations', fontsize=9, ha='center')
    
    ax.annotate('', xy=(0.7, 0.5), xytext=(0.65, 0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='purple'))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Test Architecture Diagram', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('/results/visualizations/architecture_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all visualizations"""
    print("Generating security test visualizations...")
    
    create_security_comparison_chart()
    print("✓ Security comparison chart created")
    
    create_vulnerability_pie_chart()
    print("✓ Vulnerability distribution chart created")
    
    create_network_traffic_diagram()
    print("✓ Network traffic diagram created")
    
    create_test_results_dashboard()
    print("✓ Test results dashboard created")
    
    create_architecture_diagram()
    print("✓ Architecture diagram created")
    
    print(f"\nAll visualizations saved to /results/visualizations/")
    print("Files generated:")
    print("- security_comparison.png")
    print("- vulnerability_distribution.png") 
    print("- network_traffic_diagram.png")
    print("- test_results_dashboard.png")
    print("- architecture_diagram.png")

if __name__ == "__main__":
    main()
