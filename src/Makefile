CC = gcc
CXX = g++

OUTPUT1 := g1m_converter.exe
OUTPUT2 := g1t_converter.exe
OBJS = debug.o Utils.o ../eternity_common/BaseFile.o FilesOperations.o 
OBJS += ../eternity_common/crypto/sha1.o ../eternity_common/crypto/md5.o ../eternity_common/crypto/rijndael.o
OBJS += ../eternity_common/Stream.o ../eternity_common/MemoryStream.o ../eternity_common/FixedMemoryStream.o ../eternity_common/FileStream.o ../eternity_common/BitStream.o ../eternity_common/FixedBitStream.o
OBJS += ../eternity_common/math/Vector.o 
OBJS += ../eternity_common/DOA6/G1mFile.o G1tFile.o DdsFile.o 
OBJS += ../eternity_common/tinyxml/tinyxml.o ../eternity_common/tinyxml/tinystr.o ../eternity_common/tinyxml/tinyxmlerror.o ../eternity_common/tinyxml/tinyxmlparser.o

CFLAGS=-Wall -I. -I../eternity_common  -std=gnu99 -O2 
CXXFLAGS=-Wall -Wno-strict-aliasing -I../eternity_common  -O2 -std=c++17 -DTIXML_USE_STL 
LDFLAGS=-L. -ld3d9 -ld3dx9
LIBS = -lstdc++ -lz -lversion -ld3dx9

all: $(OUTPUT1) $(OUTPUT2)

clean: 
	rm -f $(OUTPUT1) $(OUTPUT2) *.o
	rm -f ../eternity_common/*.o
	rm -f ../eternity_common/DOA6/*.o
	rm -f ../eternity_common/tinyxml/*.o
	rm -f ../eternity_common/crypto/*.o

$(OUTPUT1): $(OBJS) main.o 
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

$(OUTPUT2): $(OBJS) g1t_converter.o 
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

# Compilation rules for C++ files
g1t_converter.o: g1t_converter.cpp
	$(CXX) $(CXXFLAGS) -c g1t_converter.cpp -o g1t_converter.o

main.o: main.cpp
	$(CXX) $(CXXFLAGS) -c main.cpp -o main.o

FilesOperations.o: FilesOperations.cpp
	$(CXX) $(CXXFLAGS) -c FilesOperations.cpp -o FilesOperations.o

debug.o: debug.cpp
	$(CXX) $(CXXFLAGS) -c debug.cpp -o debug.o

Utils.o: Utils.cpp
	$(CXX) $(CXXFLAGS) -I"C:/Program Files/zlib/include" -c Utils.cpp -o Utils.o

../eternity_common/BaseFile.o: ../eternity_common/BaseFile.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/BaseFile.cpp -o ../eternity_common/BaseFile.o

../eternity_common/Stream.o: ../eternity_common/Stream.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/Stream.cpp -o ../eternity_common/Stream.o

../eternity_common/MemoryStream.o: ../eternity_common/MemoryStream.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/MemoryStream.cpp -o ../eternity_common/MemoryStream.o

../eternity_common/FixedMemoryStream.o: ../eternity_common/FixedMemoryStream.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/FixedMemoryStream.cpp -o ../eternity_common/FixedMemoryStream.o

../eternity_common/FileStream.o: ../eternity_common/FileStream.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/FileStream.cpp -o ../eternity_common/FileStream.o

../eternity_common/BitStream.o: ../eternity_common/BitStream.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/BitStream.cpp -o ../eternity_common/BitStream.o

../eternity_common/FixedBitStream.o: ../eternity_common/FixedBitStream.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/FixedBitStream.cpp -o ../eternity_common/FixedBitStream.o

../eternity_common/math/Vector.o: ../eternity_common/math/Vector.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/math/Vector.cpp -o ../eternity_common/math/Vector.o

../eternity_common/DOA6/G1mFile.o: ../eternity_common/DOA6/G1mFile.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/DOA6/G1mFile.cpp -o ../eternity_common/DOA6/G1mFile.o

G1tFile.o: G1tFile.cpp
	$(CXX) $(CXXFLAGS) -c G1tFile.cpp -o G1tFile.o

DdsFile.o: DdsFile.cpp
	$(CXX) $(CXXFLAGS) -c DdsFile.cpp -o DdsFile.o

../eternity_common/tinyxml/tinyxml.o: ../eternity_common/tinyxml/tinyxml.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/tinyxml/tinyxml.cpp -o ../eternity_common/tinyxml/tinyxml.o

../eternity_common/tinyxml/tinystr.o: ../eternity_common/tinyxml/tinystr.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/tinyxml/tinystr.cpp -o ../eternity_common/tinyxml/tinystr.o

../eternity_common/tinyxml/tinyxmlerror.o: ../eternity_common/tinyxml/tinyxmlerror.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/tinyxml/tinyxmlerror.cpp -o ../eternity_common/tinyxml/tinyxmlerror.o

../eternity_common/tinyxml/tinyxmlparser.o: ../eternity_common/tinyxml/tinyxmlparser.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/tinyxml/tinyxmlparser.cpp -o ../eternity_common/tinyxml/tinyxmlparser.o

# Compilation rules for C files
../eternity_common/crypto/sha1.o: ../eternity_common/crypto/sha1.c
	$(CC) $(CFLAGS) -c ../eternity_common/crypto/sha1.c -o ../eternity_common/crypto/sha1.o

../eternity_common/crypto/md5.o: ../eternity_common/crypto/md5.c
	$(CC) $(CFLAGS) -c ../eternity_common/crypto/md5.c -o ../eternity_common/crypto/md5.o

../eternity_common/crypto/rijndael.o: ../eternity_common/crypto/rijndael.c
	$(CC) $(CFLAGS) -c ../eternity_common/crypto/rijndael.c -o ../eternity_common/crypto/rijndael.o
