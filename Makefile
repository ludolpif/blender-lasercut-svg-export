.PHONY: all build clean
ZIPNAME=$(shell ./get_meta.pl src zipname)
ZIPGLOB=$(shell ./get_meta.pl src zipglob)

all: build
	
build: $(ZIPNAME)

clean:
	rm -f $(ZIPGLOB)

$(ZIPNAME): $(wildcard src/*) Makefile
	blender --command extension build --source-dir src
