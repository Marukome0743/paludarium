/* Differential-test guest: the smallest C hello world (write + exit only). */
#include <unistd.h>

int main(void) {
    static const char message[] = "Hello, world!\n";
    if (write(1, message, sizeof message - 1) != (ssize_t)(sizeof message - 1)) {
        return 1;
    }
    return 0;
}
