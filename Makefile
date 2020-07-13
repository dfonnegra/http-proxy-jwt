export HTTP_PORT=13139

build:
	docker-compose build --build-arg HTTP_PORT=${HTTP_PORT}

run: stop
	docker-compose up --no-recreate -d

stop:
	docker-compose stop

rm: stop
	docker-compose rm
