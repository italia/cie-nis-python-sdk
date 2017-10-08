C++ = g++
BINDIR = ./bin/
FLAGS = -std=c++11 -g -I /usr/include/PCSC -lpcsclite

all: objs test-interactive
objs: example-interactive.o requests.o
	
test-interactive:
	$(C++) $(FLAGS) -o $(BINDIR)test-interactive example-interactive.o requests.o
	rm *.o

example-interactive.o:
	$(C++) $(FLAGS) -c example-interactive.cpp

requests.o:
	$(C++) $(FLAGS) -c requests.cpp

clean:
	rm -f test *.o
