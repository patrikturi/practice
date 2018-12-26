ORIG_IMAGES_PATH = ../images
THUMB_FILES = $(shell find $(ORIG_IMAGES_PATH) -type f -iname "*.png" | sed 's/..\/images/out\/thumb/g')
CONVERT_CMD = convert -resize "100x100" $(ORIG_IMAGES_PATH)/$*.png $@
MSG = @echo -e "\nUpdating thumbnail" $@


all: out/files.txt

out/files.txt: ${THUMB_FILES}
	-rm out/files.txt
	@for i in $(THUMB_FILES); do	  \
		echo `ls -sh $$i >> out/files.txt`; \
	done

out/thumb/%.png: $(ORIG_IMAGES_PATH)/%.png | out/thumb
	$(MSG)
	$(CONVERT_CMD)

out/thumb:
	mkdir -p out/thumb/

.phony: clean
clean:
	@echo Cleaning temporary files...
	rm -rf out/thumb/*.png
	-rmdir out/thumb
	rm out/files.txt
	-rmdir out
