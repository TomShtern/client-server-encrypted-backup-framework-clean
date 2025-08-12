#include <iostream>
#include <cstdint>

constexpr size_t CLIENT_ID_SIZE = 16;

struct RequestHeader {
    uint8_t client_id[CLIENT_ID_SIZE];
    uint8_t version;
    uint16_t code;
    uint32_t payload_size;
};

int main() {
    std::cout << "sizeof(RequestHeader): " << sizeof(RequestHeader) << " bytes" << std::endl;
    std::cout << "Expected size without padding: " << (16 + 1 + 2 + 4) << " bytes" << std::endl;
    return 0;
}