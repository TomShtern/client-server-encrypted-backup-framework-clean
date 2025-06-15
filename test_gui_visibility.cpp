#include <windows.h>
#include <iostream>
#include <thread>
#include <chrono>

// Simple test to verify GUI window visibility
LRESULT CALLBACK TestWindowProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            
            // Draw a simple test interface
            RECT rect;
            GetClientRect(hwnd, &rect);
            
            // Fill background with dark blue
            HBRUSH bgBrush = CreateSolidBrush(RGB(30, 40, 60));
            FillRect(hdc, &rect, bgBrush);
            DeleteObject(bgBrush);
            
            // Draw title text
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, RGB(255, 255, 255));
            
            HFONT hFont = CreateFontW(24, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
                                   DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
                                   CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                                   DEFAULT_PITCH | FF_DONTCARE, L"Segoe UI");
            HFONT hOldFont = (HFONT)SelectObject(hdc, hFont);
            
            std::wstring text = L"🚀 ULTRA MODERN GUI TEST - VISIBLE! 🚀";
            TextOutW(hdc, 50, 50, text.c_str(), static_cast<int>(text.length()));
            
            std::wstring text2 = L"✅ If you can see this, the GUI is working!";
            TextOutW(hdc, 50, 100, text2.c_str(), static_cast<int>(text2.length()));
            
            std::wstring text3 = L"🔥 Enhanced GUI Features Are Active!";
            TextOutW(hdc, 50, 150, text3.c_str(), static_cast<int>(text3.length()));
            
            SelectObject(hdc, hOldFont);
            DeleteObject(hFont);
            
            EndPaint(hwnd, &ps);
            return 0;
        }
        
        case WM_CLOSE:
            PostQuitMessage(0);
            return 0;
            
        case WM_KEYDOWN:
            if (wParam == VK_ESCAPE) {
                PostQuitMessage(0);
            }
            return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

int main() {
    std::cout << "🚀 Testing GUI Visibility..." << std::endl;
    
    // Register window class
    WNDCLASSEXW wc = {};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.lpfnWndProc = TestWindowProc;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    wc.lpszClassName = L"TestGUIWindow";
    wc.hIcon = LoadIcon(nullptr, IDI_APPLICATION);
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    
    if (!RegisterClassExW(&wc)) {
        std::cout << "❌ Failed to register window class!" << std::endl;
        return 1;
    }
    
    // Create window
    HWND hwnd = CreateWindowExW(
        WS_EX_LAYERED | WS_EX_TOPMOST,
        L"TestGUIWindow",
        L"🚀 ULTRA MODERN GUI TEST",
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        100, 100, 800, 600,
        nullptr, nullptr,
        GetModuleHandle(nullptr),
        nullptr
    );
    
    if (!hwnd) {
        std::cout << "❌ Failed to create window!" << std::endl;
        return 1;
    }
    
    // Make sure window is visible
    SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA);
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);
    SetForegroundWindow(hwnd);
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    
    std::cout << "✅ GUI Window Created and Should Be Visible!" << std::endl;
    std::cout << "📱 Look for the window on your screen..." << std::endl;
    std::cout << "🔥 Press ESC in the window or close it to exit." << std::endl;
    
    // Message loop
    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    std::cout << "👋 GUI Test Complete!" << std::endl;
    return 0;
}
