#include <iostream>
#include <mutex>
#include <thread>
#include "hello.h"

int main() {
    std::mutex a, b;

    std::thread t1([&a, &b] {
        a.lock();
        b.lock();
    });

    std::thread t2([&a, &b] {
        b.lock();
        a.lock();
    });

    t1.join();
    t2.join();
}
