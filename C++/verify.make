C++ = g++
BINDIR = ./bin/
FLAGS = -std=c++11 -g -I /usr/include/PCSC -lpcsclite

all: objs test-verify
objs: example.o requests.o
	
test-verify:
	$(C++) $(FLAGS) -o $(BINDIR)test-verify example-verify.o requests.o
	rm *.o

example.o:
	$(C++) $(FLAGS) -c example-verify.cpp

requests.o:
	$(C++) $(FLAGS) -c requests.cpp

clean:
	rm -f test *.o
