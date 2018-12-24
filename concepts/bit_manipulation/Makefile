SHELL=cmd.exe

build: bits.exe

bits.exe: bits.cpp
	@echo ==== Building ====
	cl.exe /std:c++14 /fp:strict /Od /EHsc bits.cpp
	link.exe bits.obj

test: build
	@echo ==== Running tests ====
	@bits.exe

.phony: clean
clean:
	del *.exe *.obj
