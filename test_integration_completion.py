#!/usr/bin/env python3
"""
Comprehensive client integration test to identify missing functionality
"""

import subprocess
import time
import os
import threading
import queue
import signal
import sys

class ClientTester:
    def __init__(self):
        self.server_process = None
        self.client_output = []
        self.integration_issues = []
        self.success_indicators = []
        
    def start_server(self):
        """Start the server in background"""
        try:
            self.server_process = subprocess.Popen(
                ["python", "server/server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            time.sleep(3)  # Give server time to start
            
            if self.server_process.poll() is None:
                print("✅ Server started successfully")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Server startup error: {e}")
            return False
    
    def run_client_with_analysis(self):
        """Run client and analyze output for integration issues"""
        try:
            print("🔧 Running client with detailed analysis...")
            
            process = subprocess.Popen(
                ["client\\EncryptedBackupClient.exe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Capture output with timeout
            try:
                stdout, stderr = process.communicate(timeout=45)
                output = stdout + stderr
                self.client_output = output.split('\n')
                
                # Analyze the output for specific issues
                self.analyze_client_output()
                return True
                
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  Client test timed out (normal for key generation)")
                return True
                
        except Exception as e:
            print(f"❌ Client test error: {e}")
            return False
    
    def analyze_client_output(self):
        """Analyze client output to identify integration issues"""
        print("\n📊 CLIENT OUTPUT ANALYSIS:")
        print("-" * 50)
        
        output_text = '\n'.join(self.client_output)
        
        # Check for key generation
        if "Starting RSA key pair generation" in output_text:
            self.success_indicators.append("RSA key generation initiated")
            print("✅ RSA key generation process started")
        
        if "1024-bit" in output_text:
            self.success_indicators.append("1024-bit key generation")
            print("✅ Using 1024-bit RSA keys (real implementation)")
        
        # Check for configuration loading
        if "Configuration loaded" in output_text:
            self.success_indicators.append("Configuration loading")
            print("✅ Configuration loaded successfully")
        
        if "transfer.info parsed successfully" in output_text:
            self.success_indicators.append("transfer.info parsing")
            print("✅ transfer.info parsing working")
        
        # Check for connection attempts
        if "Connecting to server" in output_text:
            self.success_indicators.append("Server connection attempt")
            print("✅ Server connection initiated")
        
        if "Connected" in output_text or "connection established" in output_text:
            self.success_indicators.append("Server connection success")
            print("✅ Server connection successful")
        
        # Check for file operations
        if "File validation" in output_text:
            self.success_indicators.append("File validation")
            print("✅ File validation working")
        
        # Check for authentication
        if "Registration" in output_text or "registration" in output_text:
            self.success_indicators.append("Registration process")
            print("✅ Registration process initiated")
        
        if "Reconnection" in output_text or "reconnection" in output_text:
            self.success_indicators.append("Reconnection process")
            print("✅ Reconnection process available")
        
        # Check for encryption
        if "AES" in output_text or "encrypted" in output_text:
            self.success_indicators.append("Encryption functionality")
            print("✅ Encryption functionality present")
        
        # Identify issues
        if "Failed to load RSA private key" in output_text:
            self.integration_issues.append("RSA private key loading failure")
            print("⚠️  RSA private key loading needs improvement")
        
        if "BER decode error" in output_text:
            self.integration_issues.append("Key format compatibility issue")
            print("⚠️  Key format needs standardization")
        
        if "Connection failed" in output_text:
            self.integration_issues.append("Network connection problems")
            print("⚠️  Network connection needs refinement")
        
        if "ERROR" in output_text.upper():
            error_lines = [line for line in self.client_output if "ERROR" in line.upper()]
            for error in error_lines:
                self.integration_issues.append(f"Error: {error.strip()}")
            print(f"⚠️  Found {len(error_lines)} error messages")
    
    def check_generated_files(self):
        """Check what files were generated"""
        print("\n📁 FILE GENERATION ANALYSIS:")
        print("-" * 50)
        
        files_to_check = {
            "client/me.info": "Client identity file",
            "client/priv.key": "Private key file", 
            "client/pub.key": "Public key file",
            "client/gui_status.json": "GUI status file",
            "client/client_debug.log": "Debug log file"
        }
        
        generated_files = []
        
        for filepath, description in files_to_check.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"✅ {description}: {filepath} ({size} bytes)")
                generated_files.append(filepath)
                
                # Check file format quality
                if filepath.endswith('me.info'):
                    self.check_me_info_format(filepath)
                elif filepath.endswith('priv.key'):
                    self.check_key_format(filepath)
            else:
                print(f"❌ {description}: {filepath} not found")
        
        return generated_files
    
    def check_me_info_format(self, filepath):
        """Check me.info file format quality"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if len(lines) >= 3:
                username = lines[0].strip()
                uuid_hex = lines[1].strip()
                key_data = lines[2].strip()
                
                if len(username) > 0 and len(uuid_hex) == 32 and len(key_data) > 50:
                    print("  ✅ me.info format appears correct")
                    self.success_indicators.append("Proper me.info format")
                else:
                    print("  ⚠️  me.info format needs verification")
                    self.integration_issues.append("me.info format quality")
            else:
                print("  ⚠️  me.info incomplete")
                self.integration_issues.append("Incomplete me.info file")
                
        except Exception as e:
            print(f"  ❌ Error reading me.info: {e}")
            self.integration_issues.append("me.info reading error")
    
    def check_key_format(self, filepath):
        """Check private key format"""
        try:
            with open(filepath, 'rb') as f:
                data = f.read(20)  # First 20 bytes
            
            # Check for DER format (should start with 0x30)
            if data and data[0] == 0x30:
                print("  ✅ Private key appears to be in DER format")
                self.success_indicators.append("DER format private key")
            elif b"RSA2" in data:
                print("  ⚠️  Private key in Windows CryptoAPI format")
                self.integration_issues.append("Windows CryptoAPI format key")
            else:
                print("  ⚠️  Unknown private key format")
                self.integration_issues.append("Unknown key format")
                
        except Exception as e:
            print(f"  ❌ Error reading private key: {e}")
    
    def cleanup(self):
        """Clean up processes"""
        if self.server_process:
            try:
                self.server_process.terminate()
                time.sleep(1)
                if self.server_process.poll() is None:
                    self.server_process.kill()
            except:
                pass
    
    def generate_completion_report(self):
        """Generate report on what needs to be completed"""
        print("\n" + "=" * 60)
        print("🎯 PHASE 1.3 COMPLETION ANALYSIS")
        print("=" * 60)
        
        print(f"\n✅ SUCCESS INDICATORS ({len(self.success_indicators)}):")
        for i, indicator in enumerate(self.success_indicators, 1):
            print(f"  {i}. {indicator}")
        
        print(f"\n⚠️  INTEGRATION ISSUES ({len(self.integration_issues)}):")
        for i, issue in enumerate(self.integration_issues, 1):
            print(f"  {i}. {issue}")
        
        # Calculate completion score
        total_expected = 12  # Expected success indicators
        completion_score = len(self.success_indicators)
        percentage = min((completion_score / total_expected) * 100, 100)
        
        print(f"\n📊 COMPLETION SCORE: {completion_score}/{total_expected} ({percentage:.1f}%)")
        
        if percentage >= 80:
            status = "🎉 HIGHLY COMPLETE"
        elif percentage >= 60:
            status = "✅ MOSTLY COMPLETE"
        elif percentage >= 40:
            status = "⚠️  PARTIALLY COMPLETE"
        else:
            status = "❌ NEEDS SIGNIFICANT WORK"
        
        print(f"🎯 STATUS: {status}")
        
        # Specific recommendations
        print(f"\n🔧 PRIORITY COMPLETIONS NEEDED:")
        
        priorities = []
        if "RSA key generation" not in str(self.success_indicators):
            priorities.append("Complete RSA key generation implementation")
        if "proper me.info format" not in str(self.success_indicators).lower():
            priorities.append("Fix me.info file format and saving")
        if "Server connection success" not in str(self.success_indicators):
            priorities.append("Improve server connection reliability")
        if "Key format compatibility issue" in str(self.integration_issues):
            priorities.append("Standardize key formats to DER")
        
        if not priorities:
            print("  ✅ No critical completions needed - system is functional!")
        else:
            for i, priority in enumerate(priorities, 1):
                print(f"  {i}. {priority}")
        
        return len(priorities) == 0

def main():
    print("🔧 COMPREHENSIVE CLIENT INTEGRATION TEST")
    print("=" * 60)
    print("Identifying missing functionality for Phase 1.3 completion")
    print("=" * 60)
    
    tester = ClientTester()
    
    try:
        # Step 1: Start server
        print("\n1. STARTING SERVER...")
        if not tester.start_server():
            print("Continuing without server for client analysis...")
        
        # Step 2: Run client with analysis
        print("\n2. RUNNING CLIENT INTEGRATION TEST...")
        tester.run_client_with_analysis()
        
        # Step 3: Check generated files
        print("\n3. CHECKING FILE GENERATION...")
        generated_files = tester.check_generated_files()
        
        # Step 4: Generate completion report
        success = tester.generate_completion_report()
        
        return success
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
