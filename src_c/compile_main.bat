@echo off
REM Compile main.c using GCC
gcc main.c ./cJSON/cJSON.c -I./cJSON -lm -o grp_to_json.exe

REM Check if the compilation was successful
if %errorlevel% neq 0 (
    echo Compilation failed.
    exit /b %errorlevel%
)

echo Compilation successful.