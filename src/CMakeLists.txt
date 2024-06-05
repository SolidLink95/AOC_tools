cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_C_COMPILER gcc)
set(CMAKE_CXX_COMPILER g++)

# Set the output executables
set(OUTPUT1 g1m_converter)
set(OUTPUT2 g1t_converter)

# List all source files
set(OBJS
    debug.cpp
    Utils.cpp
    ../eternity_common/BaseFile.cpp
    ../eternity_common/crypto/sha1.c
    ../eternity_common/crypto/md5.c
    ../eternity_common/crypto/rijndael.c
    ../eternity_common/Stream.cpp
    ../eternity_common/MemoryStream.cpp
    ../eternity_common/FixedMemoryStream.cpp
    ../eternity_common/FileStream.cpp
    ../eternity_common/BitStream.cpp
    ../eternity_common/FixedBitStream.cpp
    ../eternity_common/math/Vector.cpp
    ../eternity_common/DOA6/G1mFile.cpp
    G1tFile.cpp
    ../eternity_common/DdsFile.cpp
    ../eternity_common/tinyxml/tinyxml.cpp
    ../eternity_common/tinyxml/tinystr.cpp
    ../eternity_common/tinyxml/tinyxmlerror.cpp
    ../eternity_common/tinyxml/tinyxmlparser.cpp
)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -std=gnu99 -O2")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wno-strict-aliasing -O2 -DTIXML_USE_STL")

# Include directories
include_directories(. ../eternity_common "C:/Program Files/zlib/include")

# Library directories and libraries
link_directories(.)
set(LIBS stdc++ z version d3dx9 d3d9)

# Add the executable targets
add_executable(${OUTPUT1} main.cpp ${OBJS})
add_executable(${OUTPUT2} g1t_converter.cpp ${OBJS})

# Link the libraries
target_link_libraries(${OUTPUT1} ${LIBS})
target_link_libraries(${OUTPUT2} ${LIBS})

# Custom clean target
add_custom_target(clean-all
    COMMAND ${CMAKE_COMMAND} -E remove ${OUTPUT1} ${OUTPUT2}
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/*.o
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/../eternity_common/*.o
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/../eternity_common/DOA6/*.o
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/../eternity_common/tinyxml/*.o
    COMMAND ${CMAKE_COMMAND} -E remove ${CMAKE_BINARY_DIR}/../eternity_common/crypto/*.o
)
