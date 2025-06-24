#include <string>

namespace ClientGUIHelpers {
void shutdownGUI() {}
void updatePhase(const std::string&) {}
void updateOperation(const std::string&, bool, const std::string&) {}
void updateProgress(int, int, const std::string&, const std::string&) {}
void updateConnectionStatus(bool) {}
void updateError(const std::string&) {}
void showNotification(const std::string&, const std::string&, unsigned long) {}
}
