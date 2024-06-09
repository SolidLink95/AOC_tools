@echo off
rmdir /s /q build
mkdir build
cd build 
cmake ..
cmake --build .
xcopy .\Debug\G1tLib.lib ..\lib\G1tLib.lib /Y
cd ..
cargo clean
cargo build