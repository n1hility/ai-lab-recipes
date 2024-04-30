default: help

help:
	@echo "Please choose one of the following targets:"
	@echo "  - amd"
	@echo "  - nvidia"
	@echo "  - intel"

.PHONY: amd nvidia intel
amd:
	make -C amd-bootc/ image
nvidia:
	make -C nvidia-bootc/ image
intel:
	make -C intel-bootc/ image
amd-ssh:
	make -C amd-bootc/ image-ssh
nvidia-ssh:
	make -C nvidia-bootc/ image-ssh
intel-ssh:
	make -C intel-bootc/ image-ssh
