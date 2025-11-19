.PHONY: start-all stop-all build logs clean

start-all:
	docker-compose up -d

stop-all:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

migrate:
	docker-compose exec backend python migrate.py

test:
	docker-compose exec backend python -m pytest tests/

load-test:
	./scripts/load_test.sh

deploy-prod:
	./scripts/deploy_prod.sh

scale-up:
	docker-compose up -d --scale backend=3 --scale ml-engine=2

scale-down:
	docker-compose up -d --scale backend=1 --scale ml-engine=1