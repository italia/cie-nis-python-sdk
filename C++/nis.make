C++ = g++
BINDIR = ./bin/
FLAGS = -std=c++11 -g -I /usr/include/PCSC -lpcsclite

all: objs test-nis
objs: example-nis.o requests.o
	
test-nis:
	$(C++) $(FLAGS) -o $(BINDIR)test-nis example-nis.o requests.o
	rm *.o

example-nis.o:
	$(C++) $(FLAGS) -c example-nis.cpp

requests.o:
	$(C++) $(FLAGS) -c requests.cpp

clean:
	rm -f test *.o
