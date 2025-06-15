#include <windows.h>
#include <iostream>

int main() {
    // Create a simple window to test
    MessageBoxW(NULL, L"🚀 DRAMATIC NEW GUI DESIGN! 🎨\n\nThis is the NEW and IMPROVED Backup Client!\nBackground: BRIGHT YELLOW\nText: MODERN STYLING\nIcons: EMOJIS!", L"⭐ AMAZING NEW CLIENT ⭐", MB_OK | MB_ICONINFORMATION);
    
    std::cout << "Simple GUI test completed!" << std::endl;
    return 0;
}
