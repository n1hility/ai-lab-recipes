default: instructlab-nvidia

REGISTRY ?= quay.io
REGISTRY_ORG ?= ai-lab
IMAGE_TAG ?= latest
INSTRUCTLAB_IMAGE = $(REGISTRY)/$(REGISTRY_ORG)/instructlab-nvidia:$(IMAGE_TAG)
WRAPPER = $(CURDIR)../ilab-wraper/ilab
.PHONY: instructlab-nvidia
instructlab-nvidia:
	podman build -t ${REGISTRY}/${REGISTRY_ORG}/instructlab-$@:${IMAGE_TAG} -f $(CURDIR)/Containerfile $(CURDIR)
