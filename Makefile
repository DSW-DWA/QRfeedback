run:
	docker compose -f docker-compose.prod.yml up -d --build

logs:
	docker compose -f docker-compose.prod.yml logs -f

.PHONY: run logs
