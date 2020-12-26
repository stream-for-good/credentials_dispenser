VERSION=$(shell git describe --tags)
VERSION_MAJOR=$(shell git describe --tags|sed -rn 's/([0-9]+)\..*/\1/p')
VERSION_MAJOR_MINOR=$(shell git describe --tags|sed -rn 's/([0-9]+\.[0-9]+)\..*/\1/p')
docker-build-testing:
	docker build . -t stream4good/credentials-dispenser:testing
docker-push-testing:
	docker push stream4good/credentials-dispenser:testing
docker-build-release:
	docker build . -t stream4good/credentials-dispenser:$(VERSION)
docker-push-release:
	docker tag stream4good/credentials-dispenser:$(VERSION) stream4good/credentials-dispenser:$(VERSION_MAJOR)
	docker tag stream4good/credentials-dispenser:$(VERSION) stream4good/credentials-dispenser:$(VERSION_MAJOR_MINOR)
	docker push stream4good/credentials-dispenser:$(VERSION)
	docker push stream4good/credentials-dispenser:$(VERSION_MAJOR)
	docker push stream4good/credentials-dispenser:$(VERSION_MAJOR_MINOR)


