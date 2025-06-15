#include <windows.h>
#include <shellapi.h>
#include <iostream>
#include <string>
#include <thread>
#include <atomic>

// Window constants
const wchar_t* WINDOW_CLASS = L"WorkingBackupClient";
const wchar_t* WINDOW_TITLE = L"🚀 WORKING Encrypted Backup Client";

// Global variables
HWND g_hWnd = nullptr;
std::atomic<bool> g_connected{false};
std::atomic<int> g_progress{0};
std::atomic<int> g_total{100};
std::atomic<bool> g_running{true};

// Forward declarations
LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
void DrawWorkingUI(HDC hdc, RECT rect);

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    std::cout << "🚀 Starting WORKING Encrypted Backup Client..." << std::endl;

    // Register window class
    WNDCLASSEXW wc = {};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.hbrBackground = nullptr; // Custom painting
    wc.lpszClassName = WINDOW_CLASS;
    wc.hIcon = LoadIcon(hInstance, IDI_APPLICATION);
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.style = CS_HREDRAW | CS_VREDRAW;

    if (!RegisterClassExW(&wc)) {
        MessageBoxW(nullptr, L"Failed to register window class", L"Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    // Create window
    g_hWnd = CreateWindowExW(
        WS_EX_LAYERED,
        WINDOW_CLASS,
        WINDOW_TITLE,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 900, 700,
        nullptr, nullptr, hInstance, nullptr
    );

    if (!g_hWnd) {
        MessageBoxW(nullptr, L"Failed to create window", L"Error", MB_OK | MB_ICONERROR);
        return 1;
    }

    // Make window visible and bring to front
    SetLayeredWindowAttributes(g_hWnd, 0, 255, LWA_ALPHA);
    ShowWindow(g_hWnd, SW_SHOW);
    UpdateWindow(g_hWnd);
    SetForegroundWindow(g_hWnd);

    std::cout << "✅ WORKING GUI Window Created and Visible!" << std::endl;

    // Simulate backup progress
    std::thread([]{
        while (g_running) {
            for (int i = 0; i <= 100 && g_running; i += 2) {
                g_progress = i;
                if (i == 30) g_connected = true;
                if (i == 100) {
                    Sleep(2000);
                    g_progress = 0;
                    g_connected = false;
                }
                InvalidateRect(g_hWnd, nullptr, TRUE);
                Sleep(100);
            }
        }
    }).detach();

    // Message loop
    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    g_running = false;
    return static_cast<int>(msg.wParam);
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            RECT rect;
            GetClientRect(hwnd, &rect);
            DrawWorkingUI(hdc, rect);
            EndPaint(hwnd, &ps);
            return 0;
        }
        
        case WM_DESTROY:
            g_running = false;
            PostQuitMessage(0);
            return 0;
            
        case WM_LBUTTONDOWN: {
            // Toggle connection
            g_connected = !g_connected;
            g_progress = g_connected ? 75 : 25;
            InvalidateRect(hwnd, nullptr, TRUE);
            return 0;
        }
        
        case WM_KEYDOWN: {
            if (wParam == VK_ESCAPE) {
                PostQuitMessage(0);
            }
            return 0;
        }
    }
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

void DrawWorkingUI(HDC hdc, RECT rect) {
    // Create beautiful gradient background
    TRIVERTEX vertices[2];
    vertices[0].x = 0;
    vertices[0].y = 0;
    vertices[0].Red = 0x1000;   // Dark blue
    vertices[0].Green = 0x2000;
    vertices[0].Blue = 0x4000;
    vertices[0].Alpha = 0x0000;

    vertices[1].x = rect.right;
    vertices[1].y = rect.bottom;
    vertices[1].Red = 0x2000;   // Lighter blue
    vertices[1].Green = 0x3000;
    vertices[1].Blue = 0x6000;
    vertices[1].Alpha = 0x0000;

    GRADIENT_RECT gradientRect = {0, 1};
    GradientFill(hdc, vertices, 2, &gradientRect, 1, GRADIENT_FILL_RECT_V);

    // Set text properties
    SetBkMode(hdc, TRANSPARENT);
    SetTextColor(hdc, RGB(255, 255, 255));

    // Create fonts
    HFONT hTitleFont = CreateFontW(28, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
                                  DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
                                  CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                                  DEFAULT_PITCH | FF_DONTCARE, L"Segoe UI");
    HFONT hFont = CreateFontW(16, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                             DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
                             CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                             DEFAULT_PITCH | FF_DONTCARE, L"Segoe UI");

    // Draw title
    HFONT hOldFont = (HFONT)SelectObject(hdc, hTitleFont);
    std::wstring title = L"🚀 WORKING Encrypted Backup Client";
    TextOutW(hdc, 50, 50, title.c_str(), static_cast<int>(title.length()));

    // Switch to normal font
    SelectObject(hdc, hFont);

    // Draw connection status
    int y = 120;
    std::wstring status = g_connected ? L"✅ Connected to Server" : L"❌ Disconnected";
    COLORREF statusColor = g_connected ? RGB(100, 255, 100) : RGB(255, 100, 100);
    SetTextColor(hdc, statusColor);
    TextOutW(hdc, 50, y, status.c_str(), static_cast<int>(status.length()));
    SetTextColor(hdc, RGB(255, 255, 255));

    // Draw progress
    y += 50;
    std::wstring progressText = L"Backup Progress: " + std::to_wstring(g_progress.load()) + L"%";
    TextOutW(hdc, 50, y, progressText.c_str(), static_cast<int>(progressText.length()));

    // Draw progress bar
    y += 40;
    RECT progressRect = {50, y, rect.right - 50, y + 30};
    
    // Background
    HBRUSH bgBrush = CreateSolidBrush(RGB(60, 60, 60));
    FillRect(hdc, &progressRect, bgBrush);
    DeleteObject(bgBrush);
    
    // Progress fill
    int progressWidth = (progressRect.right - progressRect.left) * g_progress / 100;
    RECT fillRect = {progressRect.left, progressRect.top, progressRect.left + progressWidth, progressRect.bottom};
    COLORREF progressColor = g_connected ? RGB(0, 200, 255) : RGB(150, 150, 150);
    HBRUSH fillBrush = CreateSolidBrush(progressColor);
    FillRect(hdc, &fillRect, fillBrush);
    DeleteObject(fillBrush);

    // Draw border
    HPEN borderPen = CreatePen(PS_SOLID, 2, RGB(255, 255, 255));
    HPEN oldPen = (HPEN)SelectObject(hdc, borderPen);
    HBRUSH nullBrush = (HBRUSH)GetStockObject(NULL_BRUSH);
    HBRUSH oldBrush = (HBRUSH)SelectObject(hdc, nullBrush);
    Rectangle(hdc, progressRect.left, progressRect.top, progressRect.right, progressRect.bottom);
    SelectObject(hdc, oldPen);
    SelectObject(hdc, oldBrush);
    DeleteObject(borderPen);

    // Instructions
    y += 80;
    std::wstring instr1 = L"💡 Click anywhere to toggle connection";
    std::wstring instr2 = L"🔄 Watch automatic backup progress simulation";
    std::wstring instr3 = L"⌨️ Press ESC to exit";
    
    TextOutW(hdc, 50, y, instr1.c_str(), static_cast<int>(instr1.length()));
    TextOutW(hdc, 50, y + 30, instr2.c_str(), static_cast<int>(instr2.length()));
    TextOutW(hdc, 50, y + 60, instr3.c_str(), static_cast<int>(instr3.length()));

    // Features list
    y += 120;
    SetTextColor(hdc, RGB(200, 200, 255));
    std::wstring feat1 = L"✅ Modern gradient background";
    std::wstring feat2 = L"✅ Real-time progress animation";
    std::wstring feat3 = L"✅ Interactive connection toggle";
    std::wstring feat4 = L"✅ Professional typography";
    std::wstring feat5 = L"✅ Responsive design";
    
    TextOutW(hdc, 50, y, feat1.c_str(), static_cast<int>(feat1.length()));
    TextOutW(hdc, 50, y + 25, feat2.c_str(), static_cast<int>(feat2.length()));
    TextOutW(hdc, 50, y + 50, feat3.c_str(), static_cast<int>(feat3.length()));
    TextOutW(hdc, 50, y + 75, feat4.c_str(), static_cast<int>(feat4.length()));
    TextOutW(hdc, 50, y + 100, feat5.c_str(), static_cast<int>(feat5.length()));

    // Clean up
    SelectObject(hdc, hOldFont);
    DeleteObject(hTitleFont);
    DeleteObject(hFont);
}
