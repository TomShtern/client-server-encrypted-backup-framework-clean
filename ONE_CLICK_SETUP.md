# 🚀 One-Click Build and Run Guide

This guide provides multiple one-click solutions to build, configure, and launch the complete CyberBackup 3.0 system.

## 📋 What These Scripts Do

The one-click scripts automate the entire setup process:

1. **Prerequisites Check** - Verify Python, CMake, and build tools
2. **CMake Configuration** - Set up vcpkg dependencies and configure build system
3. **C++ Client Build** - Compile the EncryptedBackupClient.exe
4. **Python Environment** - Install required Python packages
5. **Configuration Setup** - Generate RSA keys and config files if needed
6. **Service Launch** - Start backup server, API server, and web GUI

## 🛠️ Available Scripts

### Option 1: Batch File (Windows)
```bash
# Double-click or run from command prompt
one_click_build_and_run.bat
```
- ✅ Simple, no parameters needed
- ✅ Works on all Windows versions
- ✅ Clear step-by-step output

### Option 2: PowerShell (Windows, Enhanced)
```powershell
# From PowerShell
.\one_click_build_and_run.ps1

# With options
.\one_click_build_and_run.ps1 -SkipBuild    # Skip build if already compiled
.\one_click_build_and_run.ps1 -Verbose     # Detailed output
```
- ✅ Colored output and better error handling
- ✅ Support for command-line options
- ✅ More robust error reporting

### Option 3: Python (Cross-Platform)
```bash
# Basic usage
python one_click_build_and_run.py

# With options
python one_click_build_and_run.py --skip-build    # Skip build phase
python one_click_build_and_run.py --verbose       # Detailed output
python one_click_build_and_run.py --help          # Show all options
```
- ✅ Works on Windows, Linux, and macOS
- ✅ Best error handling and colored output
- ✅ Most flexible with command-line options

## 🎯 Quick Start

### For First-Time Setup
1. **Clone the repository** (if not already done)
2. **Choose your preferred script** from the options above
3. **Run the script** - it will handle everything automatically
4. **Wait for completion** - the process takes 2-5 minutes depending on your system
5. **Use the system** - web interface opens automatically at http://localhost:9090

### For Development
If you're actively developing and rebuilding frequently:
```bash
# Skip the build phase if you've already compiled
python one_click_build_and_run.py --skip-build
```

## 📊 What Gets Started

After successful completion, you'll have:

| Service | Port | Description |
|---------|------|-------------|
| **Web GUI** | 9090 | Browser-based file upload interface |
| **API Server** | 9090 | Flask bridge between web UI and client |
| **Backup Server** | 1256 | Python server that receives encrypted files |
| **Server GUI** | - | Tkinter monitoring interface |

## 🔧 Prerequisites

The scripts will check for these automatically:

- **Python 3.x** with pip
- **CMake 3.15+** 
- **Visual Studio Build Tools** (Windows)
- **Git** (optional but recommended)

If any are missing, the script will tell you exactly what to install.

## 📁 What Gets Created/Updated

The scripts will create or verify:

```
├── build/                          # CMake build directory
│   ├── Release/
│   │   └── EncryptedBackupClient.exe
├── data/
│   ├── valid_private_key.der       # RSA private key
│   ├── valid_public_key.der        # RSA public key
│   └── transfer.info               # Connection settings
├── vcpkg/                          # C++ package manager
├── vcpkg_installed/                # Installed C++ libraries
└── server/received_files/          # Where uploaded files go
```

## 🧪 Testing

After the system is running, you can run tests:

```bash
# Run comprehensive test suite
python scripts/master_test_suite.py

# Test individual components
python tests/test_upload.py
python tests/test_gui_upload.py
```

## 🔍 Troubleshooting

### Build Issues
- **CMake not found**: Install CMake 3.15+ from https://cmake.org/
- **vcpkg failures**: Delete `vcpkg/` folder and re-run
- **Compiler errors**: Install Visual Studio Build Tools

### Runtime Issues
- **Port conflicts**: Check if ports 1256 or 9090 are in use
- **Python import errors**: Run `pip install -r requirements.txt`
- **Key generation fails**: Run `python scripts/create_working_keys.py` manually

### General Tips
- Run with `--verbose` for detailed error information
- Check the console output for specific error messages
- Close any existing instances before re-running

## 🚦 System Status

After launch, verify everything is working:

1. **Web GUI**: Visit http://localhost:9090 
2. **Server GUI**: Should open automatically
3. **Upload Test**: Try uploading a small file
4. **Server Logs**: Check console output for transfer activity

## 🛑 Stopping the System

To stop all services:
- Close all console windows
- Or press `Ctrl+C` in each console
- Or restart your computer 😄

## 📞 Support

If you encounter issues:

1. **Check the error output** - scripts provide detailed error messages
2. **Run with verbose mode** - use `--verbose` flag for more details
3. **Check existing documentation** - see CLAUDE.md for detailed project info
4. **Review logs** - check console output and log files

## 🎉 Success!

When everything is working, you should see:
- Web interface at http://localhost:9090
- Server GUI window showing connection status
- Ability to upload files through the web interface
- Files appearing in `server/received_files/` directory

Enjoy your secure backup system! 🔒✨