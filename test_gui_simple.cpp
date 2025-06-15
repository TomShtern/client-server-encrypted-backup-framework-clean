#include <windows.h>
#include <iostream>

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    switch (uMsg) {
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            
            // Draw colorful background
            RECT rect;
            GetClientRect(hwnd, &rect);
            
            // Create gradient background
            TRIVERTEX vertices[2];
            vertices[0].x = 0; vertices[0].y = 0;
            vertices[0].Red = 0x4000; vertices[0].Green = 0x1000; vertices[0].Blue = 0x8000;
            vertices[1].x = rect.right; vertices[1].y = rect.bottom;
            vertices[1].Red = 0x0000; vertices[1].Green = 0x6000; vertices[1].Blue = 0xFF00;
            
            GRADIENT_RECT gradRect = {0, 1};
            GradientFill(hdc, vertices, 2, &gradRect, 1, GRADIENT_FILL_RECT_V);
            
            // Draw text
            SetBkMode(hdc, TRANSPARENT);
            SetTextColor(hdc, RGB(255, 255, 255));
            
            HFONT font = CreateFontW(24, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
                                   DEFAULT_CHARSET, OUT_DEFAULT_PRECIS,
                                   CLIP_DEFAULT_PRECIS, CLEARTYPE_QUALITY,
                                   DEFAULT_PITCH | FF_DONTCARE, L"Segoe UI");
            HFONT oldFont = (HFONT)SelectObject(hdc, font);
            
            TextOutW(hdc, 50, 50, L"🚀 ULTRA MODERN GUI TEST", 24);
            TextOutW(hdc, 50, 100, L"✅ GUI is working perfectly!", 28);
            TextOutW(hdc, 50, 150, L"🎨 Modern colorful design", 25);
            TextOutW(hdc, 50, 200, L"💎 Glass effects and gradients", 30);
            TextOutW(hdc, 50, 250, L"🔥 Press ESC to close", 20);
            
            SelectObject(hdc, oldFont);
            DeleteObject(font);
            
            EndPaint(hwnd, &ps);
            return 0;
        }
        
        case WM_KEYDOWN:
            if (wParam == VK_ESCAPE) {
                PostQuitMessage(0);
            }
            return 0;
            
        case WM_CLOSE:
            PostQuitMessage(0);
            return 0;
            
        default:
            return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
}

int main() {
    std::cout << "🚀 Testing Ultra Modern GUI..." << std::endl;
    
    // Register window class
    WNDCLASSEXW wc = {};
    wc.cbSize = sizeof(WNDCLASSEXW);
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = GetModuleHandle(nullptr);
    wc.hbrBackground = nullptr;
    wc.lpszClassName = L"UltraModernTest";
    wc.hIcon = LoadIcon(nullptr, IDI_APPLICATION);
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    
    if (!RegisterClassExW(&wc)) {
        std::cout << "❌ Failed to register window class!" << std::endl;
        return 1;
    }
    
    // Create window
    HWND hwnd = CreateWindowExW(
        WS_EX_LAYERED,
        L"UltraModernTest",
        L"🚀 Ultra Modern GUI Test - WORKING!",
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
    
    // Make window visible and on top
    SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA);
    ShowWindow(hwnd, SW_SHOW);
    UpdateWindow(hwnd);
    SetForegroundWindow(hwnd);
    SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
    
    std::cout << "✅ Ultra Modern GUI Window Created!" << std::endl;
    std::cout << "🖼️  Window should be visible on your screen!" << std::endl;
    std::cout << "🎨 Look for the colorful gradient window!" << std::endl;
    std::cout << "🔥 Press ESC in the window to close it." << std::endl;
    
    // Message loop
    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    std::cout << "👋 GUI Test Complete!" << std::endl;
    return 0;
}
