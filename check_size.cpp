#include <iostream>
#include <cstdint>

struct ResponseHeader {
    uint8_t version;
    uint16_t code;
    uint32_t payload_size;
};

int main() {
    std::cout << "sizeof(ResponseHeader): " << sizeof(ResponseHeader) << " bytes" << std::endl;
    return 0;
}