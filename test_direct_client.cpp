#include <iostream>
#include <fstream>

// Forward declaration
extern bool runBackupClient();

int main() {
    std::cout << "=== DIRECT CLIENT TEST ===" << std::endl;
    std::cout << "Testing direct backup client call..." << std::endl;
    
    // Check if transfer.info exists
    std::ifstream transferFile("transfer.info");
    if (!transferFile.is_open()) {
        std::cout << "ERROR: transfer.info not found in current directory" << std::endl;
        std::cout << "Current directory should contain transfer.info" << std::endl;
        return 1;
    }
    
    std::cout << "transfer.info found, reading configuration..." << std::endl;
    std::string line;
    std::getline(transferFile, line);
    std::cout << "Server: " << line << std::endl;
    std::getline(transferFile, line);
    std::cout << "Username: " << line << std::endl;
    std::getline(transferFile, line);
    std::cout << "File: " << line << std::endl;
    transferFile.close();
    
    // Check if test file exists
    std::ifstream testFile(line);
    if (!testFile.is_open()) {
        std::cout << "ERROR: Test file not found: " << line << std::endl;
        return 1;
    }
    testFile.close();
    std::cout << "Test file found!" << std::endl;
    
    std::cout << "Calling runBackupClient()..." << std::endl;
    bool result = runBackupClient();
    
    if (result) {
        std::cout << "SUCCESS: Backup completed!" << std::endl;
        return 0;
    } else {
        std::cout << "FAILED: Backup failed!" << std::endl;
        return 1;
    }
}
