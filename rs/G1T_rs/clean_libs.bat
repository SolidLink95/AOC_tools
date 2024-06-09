@echo off
for /r %%i in (*.obj) do del "%%i"
for /r %%i in (*.o) do del "%%i"
for /r %%i in (*.lib) do del "%%i"