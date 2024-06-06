@echo off
for /r %%i in (*.o) do del "%%i"
for /r %%i in (*.exe) do del "%%i"
for  %%i in (*.bin) do del "%%i"

cd ..

for /r %%i in (*.o) do del "%%i"

cd src