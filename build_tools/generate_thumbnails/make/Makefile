SRC_DIR_PATH = ../images
DEST_FILES_PATH = $(shell find $(SRC_DIR_PATH) -type f -iname "*.png" | sed 's/..\/images/out\/thumb/g')
IMAGE_CONVERT_CMD = magick $(SRC_DIR_PATH)/$*.png -resize "100x100" $@


all: out/files.txt

out/files.txt: ${DEST_FILES_PATH}
	@echo -e "Updating files.txt"
	-rm out/files.txt
	@for i in $(DEST_FILES_PATH); do	  \
		echo `ls -sh $$i >> out/files.txt`; \
	done

out/thumb/%.png: $(SRC_DIR_PATH)/%.png | out/thumb
	@echo -e "\nUpdating thumbnail" $@
	$(IMAGE_CONVERT_CMD)

out/thumb:
	mkdir -p out/thumb/

.phony: clean
clean:
	@echo Cleaning temporary files...
	rm -rf out/thumb/*.png
	-rmdir out/thumb
	rm out/files.txt
	-rmdir out
