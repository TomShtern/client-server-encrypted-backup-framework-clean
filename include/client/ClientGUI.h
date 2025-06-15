#pragma once

// These helpers are intended to be available even if the full _WIN32 GUI is not.
// Their declarations should NOT be inside #ifdef _WIN32
#include <string> // For std::string used in helpers
#include <functional> // For std::function

#ifdef _WIN32 // Include Windows headers first to define DWORD
#define WIN32_LEAN_AND_MEAN  // Exclude rarely-used stuff from Windows headers
#ifndef NOMINMAX
#define NOMINMAX  // Prevent min/max macro conflicts
#endif
#include <winsock2.h>  // Include winsock2.h before windows.h to avoid conflicts
#include <ws2tcpip.h>
#include <windows.h>
#endif

namespace ClientGUIHelpers {
    bool initializeGUI();
    void shutdownGUI();
    void updatePhase(const std::string& phase);
    void updateOperation(const std::string& operation, bool success = true, const std::string& details = "");
    void updateProgress(int current, int total, const std::string& speed = "", const std::string& eta = "");
    void updateConnectionStatus(bool connected);    void updateError(const std::string& message);
#ifdef _WIN32
    void showNotification(const std::string& title, const std::string& message, unsigned long iconType = 0x00000001L /*NIIF_INFO*/);
#else
    void showNotification(const std::string& title, const std::string& message, unsigned long iconType = 0x00000001L /*NIIF_INFO*/);
#endif
} // namespace ClientGUIHelpers


#ifdef _WIN32 // The ClientGUI class itself IS Windows-specific
#include <thread>
#include <atomic>
#include <memory>
#include <vector>
#include <shellapi.h>

// Custom Window Messages
#define WM_TRAYICON         (WM_APP + 1)
#define WM_STATUS_UPDATE    (WM_APP + 2)

// Context Menu Command IDs
#define ID_SHOW_STATUS      1001
#define ID_SHOW_CONSOLE     1002
#define ID_EXIT             1003

// Window Control IDs
#define ID_RETRY_CONNECTION 2001
#define ID_RECONNECT        2001  // Alias for compatibility
#define ID_SHOW_LOGS        2002
#define ID_TOGGLE_CONSOLE   2003
#define ID_SETTINGS         2004
#define ID_MINIMIZE         2005
#define ID_ABOUT            2006
#define ID_DIAGNOSTICS      2007
#define ID_START_BACKUP     2008
#define ID_PAUSE_BACKUP     2009
#define ID_STOP_BACKUP      2010
#define ID_BROWSE_FILE      2011
#define ID_BROWSE_MULTIPLE  2012
#define ID_VIEW_LOGS        2013
#define ID_REFRESH_STATUS   2014
#define ID_EXPORT_LOGS      2015
#define ID_CHANGE_SERVER    2016

struct GUIStatus {
    std::string phase;
    std::string operation;
    std::string details;
    std::string error;
    std::string speed;
    std::string eta;
    std::string serverIP;
    std::string serverPort;
    std::string filename;
    std::string fileSize;
    std::string transferredBytes;
    std::string lastActivity;
    std::string connectionTime;
    bool connected;
    bool success;
    bool backupInProgress;
    bool paused;
    int progress;
    int totalProgress;
    int filesTransferred;
    int totalFiles;

    GUIStatus() : connected(false), success(true), backupInProgress(false),
                  paused(false), progress(0), totalProgress(0),
                  filesTransferred(0), totalFiles(0) {}
};

class ClientGUI {
public:
    static ClientGUI* getInstance();
    bool initialize();
    void shutdown();
    void updatePhase(const std::string& phase);
    void updateOperation(const std::string& operation, bool success = true, const std::string& details = "");
    void updateProgress(int current, int total, const std::string& speed = "", const std::string& eta = "");
    void updateConnectionStatus(bool connected);
    void updateError(const std::string& error);
    void showNotification(const std::string& title, const std::string& message, unsigned long iconType = 0x00000001L /*NIIF_INFO*/);
    void showPopup(const std::string& title, const std::string& message, unsigned int type = 0x00000000L /*MB_OK*/);
    void toggleStatusWindow();
    void showStatusWindow(bool show);
    void toggleConsoleWindow();
    void showConsoleWindow(bool show);
    void setRetryCallback(std::function<void()> callback);

    // Button callback setters for responsive GUI
    void setConnectCallback(std::function<void()> callback);
    void setStartBackupCallback(std::function<void()> callback);
    void setSelectFileCallback(std::function<void()> callback);
    void setSettingsCallback(std::function<void()> callback);
    void setPauseResumeCallback(std::function<void()> callback);
    void setStopBackupCallback(std::function<void()> callback);
    void setViewLogsCallback(std::function<void()> callback);
    void setDiagnosticsCallback(std::function<void()> callback);

    void updateServerInfo(const std::string& ip, int port, const std::string& filename);
    void updateFileInfo(const std::string& filename, const std::string& fileSize);
    void updateTransferStats(const std::string& transferred, int filesCount, int totalFiles);
    void setBackupState(bool inProgress, bool paused = false);
    void addLogEntry(const std::string& message);
    void showFileDialog();
    void showMultiFileDialog();
    void showSettingsDialog();
    void showLogViewer();
    void exportLogs();
    bool isRunning() const;

    // COMPLETE IMPLEMENTATION: New helper functions
    void saveSettingsToFile(HWND settingsDialog);
    void refreshLogDisplay(HWND logDisplay, HWND statusBar);
    void exportLogsToFile(HWND logDisplay);
    std::wstring generateCurrentSystemLog();
    std::wstring getCurrentTimeString();
    void attemptServerConnection();
    void runSystemDiagnostics();

private:
    // Helper methods
    bool updateTransferInfo(const std::string& filePath);
    bool updateTransferInfoMultiple(const std::vector<std::string>& filePaths);
    std::string formatFileSize(uint64_t bytes);
    void updateMultiFileInfo(const std::vector<std::string>& files);

    // Ultra-modern UI methods
    void createModernButtonLayout();
    void drawModernButton(HDC hdc, RECT rect, const std::wstring& text, bool pressed, bool hovered);
    void drawGlassCard(HDC hdc, RECT rect, COLORREF baseColor, int alpha);
    void drawRoundedRect(HDC hdc, RECT rect, COLORREF color, int radius, int alpha);
    void drawStatusCard(HDC hdc, RECT windowRect, int margin, int y, bool connected);
    void drawInfoCard(HDC hdc, RECT windowRect, int margin, int y, const std::wstring& label, const std::wstring& value);
    void drawProgressCard(HDC hdc, RECT windowRect, int margin, int y, int progress, int total);
    void drawErrorCard(HDC hdc, RECT windowRect, int margin, int y, const std::wstring& error);
    void resizeControls();
    void showLoadingAnimation(bool show);
    void updateToastNotification(const std::string& message, int type);

    ClientGUI();
    ~ClientGUI();
    ClientGUI(const ClientGUI&) = delete;
    ClientGUI& operator=(const ClientGUI&) = delete;
    void guiMessageLoop();
    std::thread guiThread;
    std::atomic<bool> shouldClose;
    HWND statusWindow;
    HWND scrollableContent;
    HWND loadingIndicator;
    HWND hTrayWnd_;
    HWND consoleWindow;
    static LRESULT CALLBACK StatusWindowProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
    static LRESULT CALLBACK TrayWindowProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam);
    bool initializeTrayIcon();
    bool createStatusWindow();
    void showContextMenu(POINT pt);
    void updateStatusWindow();
    void drawStatusContent(HDC hdc);  // Direct HDC drawing for WM_PAINT
    void cleanup();
    std::atomic<bool> guiInitialized;
    std::atomic<bool> statusWindowVisible;
    std::atomic<bool> isLoading;
    CRITICAL_SECTION statusLock;
    GUIStatus currentStatus;
    NOTIFYICONDATAW trayIcon;
    std::function<void()> retryCallback;

    // Button callbacks for responsive functionality
    std::function<void()> connectCallback;
    std::function<void()> startBackupCallback;
    std::function<void()> selectFileCallback;
    std::function<void()> settingsCallback;
    std::function<void()> pauseResumeCallback;
    std::function<void()> stopBackupCallback;
    std::function<void()> viewLogsCallback;
    std::function<void()> diagnosticsCallback;

    // COMPLETE IMPLEMENTATION: Connection and diagnostics state
    bool connectionResult = false;
    std::string connectionError;
    std::vector<std::string> diagnosticsResults;
};

#endif // _WIN32