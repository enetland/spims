all:
	# Creating bin directory...
	mkdir -p bin
	# Bundling source directory...
	@cd src; zip -r ../bin/spims.zip *;
	# Creating executable...
	@echo '#!/usr/bin/env python' | cat - bin/spims.zip > bin/spims;
	@chmod +x bin/spims
	@rm bin/spims.zip
	@echo 'Build successful'
clean:
	@rm -r bin
