.PHONY: test serve docker-build docker-run compose-up

test:
	python tests/check_site.py

serve:
	python -m http.server 8080

docker-build:
	docker build -t recmin:local .

docker-run: docker-build
	docker run --rm -p 8080:8080 recmin:local

compose-up:
	docker compose up --build
