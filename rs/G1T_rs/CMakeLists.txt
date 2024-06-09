cmake_minimum_required(VERSION 3.10)
project(G1tLib VERSION 0.1.0)

add_definitions(-w)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_STATIC_LIBRARY_PREFIX "")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# include(CTest)
# enable_testing()

# Define sources and headers -DTIXML_USE_STL
file(GLOB G1T_SOURCES 
    ./cpp/*.cpp
    ./cpp/eternity_common/*.cpp
    ./cpp/eternity_common/DOA6/*.cpp
    # ../../src/*.cpp


)
# file(GLOB G1T_SOURCES
    # ./cpp/G1tLib.cpp
#     ./cpp/DdsFile.cpp
#     ./cpp/G1tFile.cpp
#     ../../src/Utils.cpp
#     ../../src/debug.cpp
#     ../../src/FilesOperations.cpp
#     ../../eternity_common/BaseFile.cpp
#     ../../eternity_common/Stream.cpp
#     ../../eternity_common/MemoryStream.cpp
#     ../../eternity_common/FixedMemoryStream.cpp
#     ../../eternity_common/FileStream.cpp
#     ../../eternity_common/BitStream.cpp
#     ../../eternity_common/FixedBitStream.cpp
#     ../../eternity_common/math/Vector.cpp
#     ../../eternity_common/tinyxml/tinyxml.cpp
#     ../../eternity_common/tinyxml/tinystr.cpp
#     ../../eternity_common/tinyxml/tinyxmlerror.cpp
#     ../../eternity_common/tinyxml/tinyxmlparser.cpp
# )

file(GLOB G1T_HEADERS #./cpp/*.h

./cpp/*.h
./cpp/eternity_common/*.h
./cpp/eternity_common/DOA6/*.h
# ../../src/*.h
    # ./cpp/G1tLib.h
    # ./cpp/include/DdsFile.h
    # ./cpp/include/G1tFile.h
    # ../../src/Utils.h
    # ../../src/debug.h
    # ../../src/FilesOperations.h
    # ../../eternity_common/BaseFile.h
    # ../../eternity_common/Stream.h
    # ../../eternity_common/MemoryStream.h
    # ../../eternity_common/FixedMemoryStream.h
    # ../../eternity_common/FileStream.h
    # ../../eternity_common/BitStream.h
    # ../../eternity_common/FixedBitStream.h
    # ../../eternity_common/math/Vector.h
    # ../../eternity_common/tinyxml/tinyxml.h
    # ../../eternity_common/tinyxml/tinystr.h
    # ../../eternity_common/tinyxml/tinyxmlerror.h
    # ../../eternity_common/tinyxml/tinyxmlparser.h
)

# Define the static library
add_library(G1tLib STATIC
    ${G1T_SOURCES}
    ${G1T_HEADERS}
)

# Include directories
target_include_directories(G1tLib
    # PUBLIC ./cpp/include
    PUBLIC ./cpp
    PUBLIC ../../src
    PUBLIC .cpp/eternity_common
    PUBLIC "C:/Program Files/zlib/include"
)

# Compiler options for MSVC and others
if(MSVC)
    target_compile_options(G1tLib PRIVATE /W4 /wd4244 /wd4127 /Zc:__cplusplus)

    # Add the /NODEFAULTLIB:MSVCRTD linker option for MSVC
    target_link_options(G1tLib PRIVATE /NODEFAULTLIB:MSVCRTD)
else()
    target_compile_options(G1tLib PRIVATE -Wall -fno-plt -fshort-wchar -DTIXML_USE_STL)
endif()

# Enable tests if available
# if(BUILD_TESTING)
#     add_subdirectory(tests)
# endif()

# Packaging configuration
set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)
