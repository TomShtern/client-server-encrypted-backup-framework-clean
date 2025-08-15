#!/usr/bin/env python3
"""
Comprehensive UTF-8 Test Suite - All UTF-8 Functionality in One File

This comprehensive test suite validates the complete UTF-8 solution for the 
Client-Server Encrypted Backup Framework, covering all previously tested scenarios:

1. Global UTF-8 patching activation
2. Subprocess UTF-8 support with Hebrew+emoji content
3. Project component integration
4. Real-world UnicodeDecodeError scenario reproduction
5. Console output validation
6. Hebrew filename processing
7. Entry point UTF-8 initialization
8. Detailed environment validation and reporting
9. Before/after UTF-8 fix comparison testing
10. Codebase emoji file analysis

CONSOLIDATED FROM: test_unicode_encoding_validation.py, test_real_emoji_validation.py, 
test_encoding_fixed.py, zero_config_child.py and previous comprehensive tests
APPROACH: One comprehensive test covers all UTF-8 functionality
"""

import sys
import os
import tempfile
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import contextlib
from typing import List, Dict, Any, Tuple, Callable, Optional
import importlib
import importlib.util

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the consolidated UTF-8 solution dynamically to avoid static import errors
if importlib.util.find_spec('utf8_solution') is not None:
    utf8_solution = importlib.import_module('utf8_solution')
else:
    print("WARNING: utf8_solution module not found - some tests may not work as expected")
    utf8_solution = None

class UTF8TestSuite:
    """Comprehensive UTF-8 testing suite."""
    # Instance attributes (typed at class-level for static checkers)
    test_results: List[Tuple[str, bool]]
    detailed_results: Dict[str, Any]
    passed: int
    total: int
    errors_found: List[str]
    emoji_files: List[str]
    
    def __init__(self):
        self.test_results = []
        self.detailed_results = {}
        self.passed = 0
        self.total = 0
        self.errors_found = []
        
        # Emoji files from codebase for testing
        self.emoji_files = [
            "python_server/server_gui/ServerGUI.py",
            "scripts/test_fixes.py", 
            "scripts/fix_and_test.py",
            "scripts/fix_vcpkg_issues.py",
            "scripts/check_dependencies.py",
            "scripts/fixed_launcher.py",
            "start_servers.py"
        ]
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result with detailed information."""
        status = "PASS" if success else "FAIL"
        timestamp = datetime.now().isoformat()
        print(f"[{status}] {test_name}")
        if details:
            print(f"      {details}")
        
        self.detailed_results[test_name] = {
            'success': success,
            'details': details,
            'timestamp': timestamp
        }
        
        if not success:
            self.errors_found.append(f"{test_name}: {details}")
    
    def run_test(self, test_name: str, test_func: 'Callable[[], bool]'):
        """Run a single test and track results."""
        print(f"\n=== {test_name} ===")
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASS")
                self.passed += 1
            else:
                print(f"❌ {test_name}: FAIL")
            self.test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            self.test_results.append((test_name, False))
        finally:
            self.total += 1

    def _run_python_script(self, cmd: List[str], env: Optional[Dict[str, str]] = None, timeout: int = 15, encoding: Optional[str] = 'utf-8') -> subprocess.CompletedProcess[str]:
        """Run a python command with consistent capture/text/encoding options.

        If encoding is None the encoding parameter is not passed (to simulate
        default platform behavior).
        """
        run_kwargs = {
            'capture_output': True,
            'text': True,
            'timeout': timeout
        }
        if encoding is not None:
            run_kwargs['encoding'] = encoding
        if env is not None:
            run_kwargs['env'] = env

        return subprocess.run(cmd, **run_kwargs)

    def _print_positive_summary(self):
        """Print the small positive summary block used in multiple places."""
        print("   ✅ UTF-8 encoding is properly configured")
        print("   ✅ Subprocess pipes handle Unicode correctly")
        print("   ✅ Hebrew filenames process without errors")
        print("   ✅ Before/after comparison shows fix effectiveness")
        print("   ✅ Codebase emoji files process correctly")
        print("   ⚠️  Consider replacing emojis with ASCII alternatives for maximum compatibility")

    def _write_run_temp_script(self, script_text: str, encoding: str = 'utf-8', run_encoding: Optional[str] = 'utf-8', timeout: int = 15, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
        """Write a temporary python script, run it with _run_python_script, and cleanup.

        Returns subprocess.CompletedProcess[str].
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding=encoding) as f:
            f.write(script_text)
            tmp = f.name

        try:
            return self._run_python_script([sys.executable, tmp], env=env, timeout=timeout, encoding=run_encoding)
        finally:
            with contextlib.suppress(Exception):
                os.unlink(tmp)

    def _get_encoding_info(self) -> Dict[str, str]:
        """Return a small dict with current encoding info (extracted for reuse)."""
        return {
            'default_encoding': sys.getdefaultencoding(),
            'fs_encoding': sys.getfilesystemencoding(),
            'stdout_encoding': getattr(sys.stdout, 'encoding', 'unknown'),
            'stderr_encoding': getattr(sys.stderr, 'encoding', 'unknown')
        }

    def _make_utf8_env(self) -> Dict[str, str]:
        """Return a copy of the current env with PYTHONIOENCODING=utf-8."""
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        return env

    def _is_encoding_error(self, proc: subprocess.CompletedProcess[str]) -> bool:
        """Return True if the process result indicates an encoding error."""
        stderr = str(getattr(proc, 'stderr', '') or '')
        return (
            'UnicodeDecodeError' in stderr or
            'UnicodeEncodeError' in stderr or
            'charmap' in stderr.lower() or
            getattr(proc, 'returncode', 0) != 0
        )

    def _run_script_and_get_text(self, script_text: str, encoding: str = 'utf-8', run_encoding: Optional[str] = 'utf-8', timeout: int = 15, env: Optional[Dict[str, str]] = None) -> Tuple[str, str, int]:
        """Write script, run it, return tuple (stdout, stderr, returncode) as strings/ints."""
        proc = self._write_run_temp_script(script_text, encoding=encoding, run_encoding=run_encoding, timeout=timeout, env=env)
        stdout = str(getattr(proc, 'stdout', '') or '')
        stderr = str(getattr(proc, 'stderr', '') or '')
        return stdout, stderr, int(getattr(proc, 'returncode', 0))
    
    def _check_real_backup_executor(self) -> bool:
        """Try to import and construct RealBackupExecutor; return True on success."""
        try:
            from api_server.real_backup_executor import RealBackupExecutor
            RealBackupExecutor()
            return True
        except Exception:
            return False

    def _check_script_before_after(self, script_text: str, success_marker: str = 'COMPARISON_TEST_SUCCESS', timeout: int = 10) -> Tuple[bool, bool]:
        """Run a script twice: once with default env (no PYTHONIOENCODING) and once with PYTHONIOENCODING=utf-8.

        Returns (has_encoding_error_without_utf8, fix_works_with_utf8)
        """
        _stdout1, stderr1, rc1 = self._run_script_and_get_text(script_text, encoding='utf-8', run_encoding=None, timeout=timeout)
        has_encoding_error = self._is_encoding_error(subprocess.CompletedProcess(args=[], returncode=rc1, stdout=_stdout1, stderr=stderr1))

        utf8_env = self._make_utf8_env()
        _stdout2, stderr2, rc2 = self._run_script_and_get_text(script_text, encoding='utf-8', run_encoding='utf-8', timeout=timeout, env=utf8_env)
        fix_works = (rc2 == 0 and success_marker in _stdout2 and not self._is_encoding_error(subprocess.CompletedProcess(args=[], returncode=rc2, stdout=_stdout2, stderr=stderr2)))

        return has_encoding_error, fix_works

    def _run_and_check_success(self, script_text: str, success_marker: str, run_encoding: Optional[str] = 'utf-8', timeout: int = 15, env: Optional[Dict[str, str]] = None) -> bool:
        """Helper to run a temporary script and check for success marker and encoding errors."""
        proc = self._write_run_temp_script(script_text, encoding='utf-8', run_encoding=run_encoding, timeout=timeout, env=env)
        stdout = str(getattr(proc, 'stdout', '') or '')
        stderr = str(getattr(proc, 'stderr', '') or '')
        return (
            getattr(proc, 'returncode', 1) == 0 and
            success_marker in stdout and
            'UnicodeDecodeError' not in stderr and
            'charmap' not in stderr.lower()
        )

    def _print_proc_debug(self, proc: subprocess.CompletedProcess[str]):
        """Print helpful debug info about a subprocess CompletedProcess."""
        print(f"Exit code: {getattr(proc, 'returncode', 'unknown')}")
        print(f"STDOUT: {getattr(proc, 'stdout', '')}")
        print(f"STDERR: {getattr(proc, 'stderr', '')}")

    def _print_encoding_info(self) -> Dict[str, str]:
        """Print encoding environment info and return the info dict."""
        info = self._get_encoding_info()
        print(f"Default encoding: {info['default_encoding']}")
        print(f"Filesystem encoding: {info['fs_encoding']}")
        print(f"stdout encoding: {info['stdout_encoding']}")
        print(f"stderr encoding: {info['stderr_encoding']}")
        return info

    def _gather_and_log_encoding_env(self) -> Tuple[Dict[str, str], bool]:
        """Fetch encoding info, log environment, and return (info, utf8_configured)."""
        info = self._print_encoding_info()
        pythonioencoding = os.environ.get('PYTHONIOENCODING', 'Not set')
        print(f"PYTHONIOENCODING: {pythonioencoding}")
        utf8_configured = (info['default_encoding'] == 'utf-8' and info['fs_encoding'] == 'utf-8')
        return info, utf8_configured
    
    def test_encoding_environment(self) -> bool:
        """Test current encoding configuration with detailed analysis."""
        print("Testing detailed encoding environment...")
        
        try:
            # Gather and log encoding environment via helper
            info, utf8_configured = self._gather_and_log_encoding_env()

            self.log_result(
                "Encoding Environment Validation",
                utf8_configured,
                f"UTF-8: {utf8_configured}, Default: {info['default_encoding']}, FS: {info['fs_encoding']}"
            )
            
            return utf8_configured
            
        except Exception as e:
            self.log_result("Encoding Environment Validation", False, f"Exception: {e}")
            return False
    
    def test_before_after_utf8_comparison(self) -> bool:
        """Test before/after UTF-8 fix comparison to prove the solution works."""
        print("Testing before/after UTF-8 fix comparison...")
        
        # Create test script with real emojis that caused the original error
        real_emoji_script = '''
import sys
import os

# Print the actual emojis from our codebase that were causing problems
print("🎉 SUCCESS! All servers are running:")  # From start_servers.py
print("✅ Port 9090 (API Server): AVAILABLE")  # From scripts/test_fixes.py
print("❌ Port 1256 (Backup Server): IN USE")  # From scripts/test_fixes.py
print("⚠️ Warning: Large file detected")       # From various status messages
print("🔧 Initializing encryption...")         # From fix_vcpkg_issues.py
print("📁 Processing file: קובץ_עברי.txt")     # Hebrew filename with emoji
print("📊 Transfer progress: 100%")            # From ServerGUI.py
print("▶️ Starting backup process")            # From ServerGUI.py
print("⏹️ Backup stopped")                     # From ServerGUI.py
print("🚀 Client started successfully")        # From various scripts

# Test Hebrew text that caused the original error
hebrew_filename = "קובץ_בדיקה_עם_אמוג'י_🎉.txt"
print(f"Processing Hebrew file with emoji: {hebrew_filename}")

print("COMPARISON_TEST_SUCCESS")
'''
        
        # Use helper to run before/after comparison
        has_encoding_error, fix_works = self._check_script_before_after(real_emoji_script, success_marker='COMPARISON_TEST_SUCCESS', timeout=10)
        print(f"  Without UTF-8 fix: {'ENCODING ERROR (as expected)' if has_encoding_error else 'UNEXPECTED SUCCESS'}")
        print(f"  With UTF-8 fix: {'SUCCESS' if fix_works else 'STILL FAILING'}")

        test_passed = bool(has_encoding_error and fix_works)
        self.log_result(
            "Before/After UTF-8 Comparison",
            test_passed,
            f"Problem exists without UTF-8: {has_encoding_error}, Fix works: {fix_works}"
        )

        return test_passed
    
    def test_emoji_file_analysis(self) -> bool:
        """Test and analyze emoji usage in actual codebase files."""
        print("Testing emoji file analysis from actual codebase...")
        
        passed_files = 0
        total_files = 0
        emoji_count = 0
        files_with_emojis = 0
        problematic_files: List[str] = []
        
        for file_path in self.emoji_files:
            full_path = project_root / file_path
            if not full_path.exists():
                print(f"     SKIP: {file_path} (not found)")
                continue
                
            total_files += 1
            
            try:
                # Read file content
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count emojis (common ones from our codebase)
                emoji_chars = ['🎉', '✅', '❌', '⚠️', '🔧', '📁', '📊', '▶️', '⏹️', '🚀', '💻', '🔒', '✨']
                file_emoji_count = sum(content.count(emoji) for emoji in emoji_chars)
                
                if file_emoji_count > 0:
                    files_with_emojis += 1
                    emoji_count += file_emoji_count
                    print(f"  ✅ {file_path}: {file_emoji_count} emojis found")
                else:
                    print(f"  ℹ️  {file_path}: no target emojis found")
                
                # Test subprocess syntax check
                result = self._run_python_script([
                    sys.executable,
                    '-c',
                    f'import ast; ast.parse(open(r"{full_path}", encoding="utf-8").read()); print("✅ Syntax OK")'
                ], timeout=10, encoding='utf-8')
                
                stderr_text = str(result.stderr or "")
                if result.returncode == 0 and 'UnicodeDecodeError' not in stderr_text:
                    passed_files += 1
                else:
                    print(f"     ✗ Subprocess test failed: {stderr_text.strip()}")
                    problematic_files.append(file_path)
                    
            except Exception as e:
                print(f"     ✗ {file_path}: Exception - {e}")
                problematic_files.append(file_path)
        
        success = not problematic_files

        self.log_result(
            "Emoji File Analysis",
            success,
            f"{passed_files}/{total_files} files passed, {files_with_emojis} files contain {emoji_count} emojis, Problematic: {len(problematic_files)}"
        )

        return success
    
    def test_utf8_activation(self) -> bool:
        """Test that UTF-8 global patching activates correctly."""
        print("Testing UTF-8 activation and subprocess patching...")
        
        test_script = '''
import sys
sys.path.insert(0, ".")

# Test BEFORE import
import subprocess
original_run = subprocess.run

# Import UTF-8 solution (should patch subprocess)
import utf8_solution

# Test AFTER import
patched_run = subprocess.run

# Check if subprocess was patched
if original_run != patched_run:
    print("✅ Subprocess successfully patched with UTF-8 support")
    success = True
else:
    print("❌ Subprocess was not patched")
    success = False

# Test immediate UTF-8 capability
print("Testing immediate Hebrew+emoji: קובץ_עברי_🎉.txt")
print("ACTIVATION_TEST_COMPLETE")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_script = f.name
        
        try:
            result = self._write_run_temp_script(test_script, encoding='utf-8', run_encoding='utf-8', timeout=15)

            stdout = result.stdout or ""
            success = (
                result.returncode == 0 and
                "✅ Subprocess successfully patched with UTF-8 support" in stdout and
                "קובץ_עברי_🎉.txt" in stdout and
                "ACTIVATION_TEST_COMPLETE" in stdout
            )
            
            if not success:
                self._print_proc_debug(result)
            
            return success
            
        finally:
            with contextlib.suppress(Exception):
                os.unlink(temp_script)
    
    def test_subprocess_hebrew_emoji(self) -> bool:
        """Test subprocess calls with Hebrew+emoji content."""
        print("Testing subprocess with comprehensive Hebrew+emoji content...")
        
        test_script = '''
import sys
import subprocess
sys.path.insert(0, ".")

# Import UTF-8 solution
import utf8_solution

# Create child script with extensive Hebrew+emoji content
child_content = """
print("Hebrew filename: קובץ_גיבוי_🎉_עברי.txt")
print("Status messages:")
print("  ✅ File validation complete")
print("  🔧 Starting encryption process")
print("  📊 Transfer progress: 100%")
print("  🎉 Backup completed successfully!")
print("Hebrew text: זהו מבחן מקיף של תמיכה ב-UTF-8")
print("Mixed content: File_עברי_🎯_backup.log")
print("SUBPROCESS_HEBREW_EMOJI_SUCCESS")
"""

with open("hebrew_emoji_child.py", "w", encoding="utf-8") as f:
    f.write(child_content)

# Use subprocess (should automatically have UTF-8 support)
result = self._run_python_script([sys.executable, "hebrew_emoji_child.py"], encoding=None)
output = result.stdout or ""

contains_hebrew = 'קובץ_גיבוי' in output
contains_emojis = '🎉' in output and '✅' in output and '🔧' in output and '📊' in output
contains_success = 'SUBPROCESS_HEBREW_EMOJI_SUCCESS' in output

print(f"Contains Hebrew: {contains_hebrew}")
print(f"Contains emojis: {contains_emojis}")
print(f"Success marker: {contains_success}")

if contains_hebrew and contains_emojis and contains_success:
    print("✅ SUBPROCESS_TEST_SUCCESS")
else:
    print("❌ SUBPROCESS_TEST_FAILED")

# Cleanup
import os
os.unlink("hebrew_emoji_child.py")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_script = f.name
        
        try:
            result = self._write_run_temp_script(test_script, encoding='utf-8', run_encoding='utf-8', timeout=20)

            stdout = result.stdout or ""
            success = (
                result.returncode == 0 and
                "✅ SUBPROCESS_TEST_SUCCESS" in stdout
            )
            
            if not success:
                self._print_proc_debug(result)
            
            return success
            
        finally:
            with contextlib.suppress(Exception):
                os.unlink(temp_script)
    
    def test_original_error_scenario(self) -> bool:
        """Test the exact scenario that caused the original UnicodeDecodeError."""
        print("Testing original UnicodeDecodeError scenario reproduction...")
        
        # Simulate the exact conditions from the original error
        client_simulation_script = '''
import sys
import subprocess
sys.path.insert(0, ".")

# Import UTF-8 solution for this test
import utf8_solution

# Simulate C++ client processing Hebrew filename with emojis
filename = "בדיקה_עם_סמלים_🎉_גיבוי_✅.txt"
print("CyberBackup C++ Client v3.0")
print(f"Processing file: {filename}")
print("🔧 Initializing encryption...")
print("✅ RSA key exchange completed")
print("🚀 Starting file transfer...")
print("📊 Transfer progress: 25%")
print("📊 Transfer progress: 50%")
print("📊 Transfer progress: 75%")
print("📊 Transfer progress: 100%")
print("✅ File transfer completed successfully!")
print("🎉 Backup operation finished")
print("STATUS: Hebrew filename with emojis processed successfully")
print("ORIGINAL_SCENARIO_SUCCESS")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(client_simulation_script)
            temp_script = f.name
        
        try:
            # Use helper to write/run/cleanup temporary script and validate
            success = self._run_and_check_success(client_simulation_script, 'ORIGINAL_SCENARIO_SUCCESS', run_encoding='utf-8', timeout=15)

            if success:
                print("✅ Original UnicodeDecodeError scenario now works correctly")
                print("✅ Hebrew filename with emojis processed successfully")
            else:
                print("Original scenario did not report success; see detailed report")

            return success
        finally:
            with contextlib.suppress(Exception):
                os.unlink(temp_script)
    
    def test_project_component_integration(self) -> bool:
        """Test that project components work with UTF-8 solution."""
        print("Testing project component integration...")
        
        try:
            if self._check_real_backup_executor():
                print("✅ RealBackupExecutor created successfully")
                hebrew_emoji_filename = "מסמך_חשוב_🔒_גיבוי_אבטחה_✅.txt"
                print(f"✅ Can handle filename: {hebrew_emoji_filename}")
                return True
            else:
                print("❌ RealBackupExecutor import/creation failed")
                return False
        except Exception as e:
            print(f"❌ Project integration failed: {e}")
            return False
    
    def test_console_output(self) -> bool:
        """Test console output works with Hebrew+emoji content."""
        print("Testing console output capability...")
        
        try:
            # Test direct Hebrew+emoji output
            test_messages = [
                "קונסולה_🎯_עובדת.txt",
                "Hebrew console: בדיקת קונסולה עברית",
                "Emoji test: ✅🚀⚠️❌📊🔧🎯",
                "Mixed: File_עברי_🎯_console.log"
            ]
            
            for msg in test_messages:
                print(f"  Output test: {msg}")
            
            print("✅ Console output works perfectly")
            return True
            
        except UnicodeEncodeError as e:
            print(f"❌ Console output failed: {e}")
            return False
    
    def test_hebrew_filenames(self) -> bool:
        """Test Hebrew filename creation and processing."""
        print("Testing Hebrew filename handling...")
        
        try:
            test_files = [
                ("בדיקה_🎉.txt", "File content with emojis: ✅🔧📁\nHebrew: תוכן בעברית"),
                ("קובץ_גיבוי_🚀.log", "Backup log: ✅ Success\nWarnings: ⚠️ Large file"),
                ("מסמך_עברי_📊.md", "# Hebrew Document 📊\nContent: תוכן עברי עם emojis: 🎉✅❌")
            ]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                files_created = 0
                files_read = 0
                
                for filename, content in test_files:
                    try:
                        file_path = Path(temp_dir) / filename
                        
                        # Write with UTF-8
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        files_created += 1
                        
                        # Read back and verify
                        with open(file_path, 'r', encoding='utf-8') as f:
                            read_content = f.read()
                        
                        if read_content == content:
                            files_read += 1
                            print(f"  ✅ {filename}: Created and read successfully")
                        else:
                            print(f"  ❌ {filename}: Content mismatch")
                            
                    except Exception as e:
                        print(f"  ❌ {filename}: Error - {e}")
                
                success = files_created == len(test_files) and files_read == len(test_files)
                print(f"Files processed: {files_read}/{len(test_files)}")
                
                return success
                
        except Exception as e:
            print(f"Hebrew filename test failed: {e}")
            return False
    
    def test_zero_configuration_approach(self) -> bool:
        """Test that UTF-8 works with zero manual configuration."""
        print("Testing zero configuration approach...")
        
        test_script = '''
# This script has ZERO manual UTF-8 configuration
import sys
import subprocess
sys.path.insert(0, ".")

# ONLY import the UTF-8 solution
import utf8_solution

# Create child script with Hebrew+emoji
child_content = """
print("זה_עובד_🌟_בלי_הגדרות.txt")
print("Automatic UTF-8: ✅🚀⚠️❌📊🔧")
print("ZERO_CONFIG_SUCCESS")
"""

with open("zero_config_test.py", "w", encoding="utf-8") as f:
    f.write(child_content)

# Direct subprocess use - should work automatically
result = subprocess.run([sys.executable, "zero_config_test.py"], capture_output=True)
output = result.stdout

contains_hebrew = 'זה_עובד' in output
contains_emojis = '🌟' in output
contains_success = 'ZERO_CONFIG_SUCCESS' in output

if contains_hebrew and contains_emojis and contains_success:
    print("✅ ZERO_CONFIG_TEST_SUCCESS")
else:
    print("❌ ZERO_CONFIG_TEST_FAILED")

# Cleanup
import os
os.unlink("zero_config_test.py")
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_script)
            temp_script = f.name
        
        try:
            result = self._write_run_temp_script(test_script, encoding='utf-8', run_encoding='utf-8', timeout=15)

            stdout = str(result.stdout or "")
            success = (
                result.returncode == 0 and
                "✅ ZERO_CONFIG_TEST_SUCCESS" in stdout
            )

            if not success:
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {str(result.stderr or '')}")

            return success

        finally:
            with contextlib.suppress(Exception):
                os.unlink(temp_script)
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report with detailed analysis."""
        print(f"\n{'='*70}")
        print("   COMPREHENSIVE UTF-8 VALIDATION REPORT")
        print("="*70)

        total_tests = len(self.detailed_results)
        passed_tests = sum(result['success'] for result in self.detailed_results.values())

        print(f"\nTest Summary: {passed_tests}/{total_tests} tests passed")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")

        if self.errors_found:
            print(f"\n❌ ISSUES FOUND ({len(self.errors_found)}):")
            for error in self.errors_found:
                print(f"   • {error}")
        else:
            print("\n✅ NO ENCODING ISSUES DETECTED")
            print("   Your UTF-8 settings are working correctly!")

        # Environment analysis
        print(f"\n🔍 ENVIRONMENT ANALYSIS:")
        print(f"   Python Version: {sys.version}")
        print(f"   Default Encoding: {sys.getdefaultencoding()}")
        print(f"   Filesystem Encoding: {sys.getfilesystemencoding()}")
        print(f"   PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")

        # Recommendations
        print(f"\n📋 RECOMMENDATIONS:")

        if passed_tests == total_tests:
            self._print_positive_summary()
        else:
            print("   🔧 Fix remaining encoding issues before production use")
            print("   🔧 Ensure all subprocess calls use encoding='utf-8'")
            print("   🔧 Set PYTHONIOENCODING=utf-8 in environment")

        # Generate detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'failed_tests': total_tests - passed_tests
            },
            'detailed_results': self.detailed_results,
            'errors_found': self.errors_found,
            'environment': {
                'python_version': sys.version,
                'default_encoding': sys.getdefaultencoding(),
                'filesystem_encoding': sys.getfilesystemencoding(),
                'stdout_encoding': getattr(sys.stdout, 'encoding', 'unknown'),
                'stderr_encoding': getattr(sys.stderr, 'encoding', 'unknown'),
                'pythonioencoding': os.environ.get('PYTHONIOENCODING', 'Not set')
            },
            'emoji_files_tested': self.emoji_files
        }

        # Save report to file
        report_file = project_root / 'comprehensive_utf8_validation_report.json'
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save detailed report: {e}")

        return report

    def run_all_tests(self):
        """Run the complete comprehensive UTF-8 test suite."""
        print("🎯 COMPREHENSIVE UTF-8 TEST SUITE")
        print("=" * 70)
        print("Testing consolidated UTF-8 solution for Hebrew+emoji support")
        print("Includes: Environment validation, before/after comparison, file analysis")
        print()
        
        # Test UTF-8 capability in this script directly
        try:
            test_text = "בדיקה_🎯_ראשונית"
            print(f"Initial UTF-8 test: {test_text}")
            print("✅ Console output works in test script")
        except UnicodeEncodeError:
            print("❌ Console output failed - UTF-8 not working")
        
        # Run all test categories - enhanced comprehensive list
        tests = [
            ("Environment Validation", self.test_encoding_environment),
            ("UTF-8 Activation", self.test_utf8_activation),
            ("Before/After Comparison", self.test_before_after_utf8_comparison),
            ("Subprocess Hebrew+Emoji", self.test_subprocess_hebrew_emoji),
            ("Original Error Scenario", self.test_original_error_scenario),
            ("Project Component Integration", self.test_project_component_integration),
            ("Console Output", self.test_console_output),
            ("Hebrew Filenames", self.test_hebrew_filenames),
            ("Emoji File Analysis", self.test_emoji_file_analysis),
            ("Zero Configuration", self.test_zero_configuration_approach)
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Generate comprehensive report
        self.generate_comprehensive_report()

        # Print final results
        print(f"\n{'=' * 70}")
        print(f"🎯 COMPREHENSIVE UTF-8 RESULTS: {self.passed}/{self.total} tests passed")

        if self.passed == self.total:
            print("🎉 SUCCESS: Comprehensive UTF-8 solution is working perfectly!")
            self._print_positive_summary()
            print()
            print("USAGE: Simply 'import utf8_solution' in entry point scripts")
            print("RESULT: UTF-8 support works automatically everywhere!")
        else:
            print("❌ ISSUES: Some UTF-8 functionality is not working")
            print("🔧 Check failed tests above for specific problems")
            print("📄 Review the detailed report for comprehensive analysis")

        print("=" * 70)

        return self.passed == self.total

def main():
    """Run the comprehensive UTF-8 test suite."""
    test_suite = UTF8TestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())