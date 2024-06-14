@echo off

cl.exe gust_tools/gust_g1t.c gust_tools/util.c gust_tools/parson.c /Fegust_g1t.exe
for %%i in (*.obj) do del %%i