CC = gcc
CXX = g++

OUTPUT1 := g1m_converter.exe
OUTPUT2 := g1t_converter.exe
OUTPUT3 := ktid_converter.exe
OBJS = debug.o Utils.o ../eternity_common/BaseFile.o FilesOperations.o stb_image.o 
OBJS += ../eternity_common/crypto/sha1.o ../eternity_common/crypto/md5.o ../eternity_common/crypto/rijndael.o
OBJS += ../eternity_common/Stream.o ../eternity_common/MemoryStream.o ../eternity_common/FixedMemoryStream.o ../eternity_common/FileStream.o ../eternity_common/BitStream.o ../eternity_common/FixedBitStream.o
OBJS += ../eternity_common/math/Vector.o 
OBJS += ../eternity_common/DOA6/G1mFile.o G1tFile.o DdsFile.o 
OBJS += tinyxml/tinyxml.o tinyxml/tinystr.o tinyxml/tinyxmlerror.o tinyxml/tinyxmlparser.o
OBJS += KtidFile.o MtlFile.o  ../eternity_common/DOA6/KidsObjDBFile.o

CFLAGS=-Wall -I. -I../eternity_common  -std=gnu99 -O2 
CXXFLAGS=-Wall -Wno-strict-aliasing -I../eternity_common -I../stb  -O2 -std=c++17 -DTIXML_USE_STL -static 
LDFLAGS=-L. -ld3d9 -ld3dx9 -L../lib -lDirectXTex
LIBS = -lstdc++ -lz -lversion -ld3dx9

all: $(OUTPUT1) $(OUTPUT2) $(OUTPUT3)

clean: 
	rm -f $(OUTPUT1) $(OUTPUT2) *.o
	rm -f ../eternity_common/*.o
	rm -f ../eternity_common/DOA6/*.o
	rm -f tinyxml/*.o
	rm -f ../eternity_common/crypto/*.o

$(OUTPUT1): $(OBJS) main.o 
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

$(OUTPUT2): $(OBJS) g1t_converter.o 
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

$(OUTPUT3): $(OBJS) ktid_converter.o 
	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS)

# Compilation rules for C++ files
g1t_converter.o: g1t_converter.cpp
	$(CXX) $(CXXFLAGS) -c g1t_converter.cpp -o g1t_converter.o

main.o: main.cpp
	$(CXX) $(CXXFLAGS) -c main.cpp -o main.o

stb_image.o: stb_image.cpp
	$(CXX) $(CXXFLAGS) -c stb_image.cpp -o stb_image.o

KtidFile.o: KtidFile.cpp
	$(CXX) $(CXXFLAGS) -c KtidFile.cpp -o KtidFile.o

MtlFile.o: MtlFile.cpp
	$(CXX) $(CXXFLAGS) -c MtlFile.cpp -o MtlFile.o

# OidFile.o: OidFile.cpp
# 	$(CXX) $(CXXFLAGS) -c OidFile.cpp -o OidFile.o

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

../eternity_common/DOA6/KidsObjDBFile.o: ../eternity_common/DOA6/KidsObjDBFile.cpp
	$(CXX) $(CXXFLAGS) -c ../eternity_common/DOA6/KidsObjDBFile.cpp -o ../eternity_common/DOA6/KidsObjDBFile.o

G1tFile.o: G1tFile.cpp
	$(CXX) $(CXXFLAGS) -c G1tFile.cpp -o G1tFile.o

DdsFile.o: DdsFile.cpp
	$(CXX) $(CXXFLAGS) -c DdsFile.cpp -o DdsFile.o

tinyxml/tinyxml.o: tinyxml/tinyxml.cpp
	$(CXX) $(CXXFLAGS) -c tinyxml/tinyxml.cpp -o tinyxml/tinyxml.o

tinyxml/tinystr.o: tinyxml/tinystr.cpp
	$(CXX) $(CXXFLAGS) -c tinyxml/tinystr.cpp -o tinyxml/tinystr.o

tinyxml/tinyxmlerror.o: tinyxml/tinyxmlerror.cpp
	$(CXX) $(CXXFLAGS) -c tinyxml/tinyxmlerror.cpp -o tinyxml/tinyxmlerror.o

tinyxml/tinyxmlparser.o: tinyxml/tinyxmlparser.cpp
	$(CXX) $(CXXFLAGS) -c tinyxml/tinyxmlparser.cpp -o tinyxml/tinyxmlparser.o

# Compilation rules for C files
../eternity_common/crypto/sha1.o: ../eternity_common/crypto/sha1.c
	$(CC) $(CFLAGS) -c ../eternity_common/crypto/sha1.c -o ../eternity_common/crypto/sha1.o

../eternity_common/crypto/md5.o: ../eternity_common/crypto/md5.c
	$(CC) $(CFLAGS) -c ../eternity_common/crypto/md5.c -o ../eternity_common/crypto/md5.o

../eternity_common/crypto/rijndael.o: ../eternity_common/crypto/rijndael.c
	$(CC) $(CFLAGS) -c ../eternity_common/crypto/rijndael.c -o ../eternity_common/crypto/rijndael.o
