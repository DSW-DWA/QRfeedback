runprod:
	docker compose -f docker-compose.prod.yml up -d --build

rundev:
	docker compose -f docker-compose.dev.yml up --build

logs:
	docker compose -f docker-compose.prod.yml logs -f

.PHONY: logs
