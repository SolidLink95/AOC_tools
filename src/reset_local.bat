@echo off
for /r %%i in (*.o) do del "%%i"
for /r %%i in (*.exe) do del "%%i"