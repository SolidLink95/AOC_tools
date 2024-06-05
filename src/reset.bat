@echo off
@REM for /r %%i in (*.o) do del "%%i"
for /r %%i in (*.exe) do del "%%i"

cd ..

for /r %%i in (*.o) do del "%%i"

cd src