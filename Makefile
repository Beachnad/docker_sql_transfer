build:
	docker build -t docker_sql_transfer:dev .

help: build
	docker run -it --rm docker_sql_transfer:dev python sql_transfer.py --help

run:
	docker run -it --rm --network host docker_sql_transfer:dev

bash:
	docker run -it --rm --network host -v "$(PWD)/test:/tests" docker_sql_transfer:dev bash

postgres-up:
	docker run --name postgres-test -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres

postgres-down:
	docker rm -f postgres-test

mysql-up:
	docker run --name mysql-test -e MYSQL_ROOT_PASSWORD=mysql -d mysql:tag

mysql-down:
	docker rm -f mysql-test

#infra-tests: build
#	docker run -it --rm --network host docker_sql_transfer:dev python sql_transfer.py \
#		--from-conn-string "mssql+pyodbc://appguest@192.168.2.41/MPC?driver=ODBC+Driver+17+for+SQL+Server" \
#		--to-conn-string "postgresql+psycopg2://postgres:postgres@localhost:5432" \
#		--sql "SELECT TOP 100 * FROM PatientProfile" \
#		--destination-table "patients" \
#		--mode "append"

build-test: build
	docker build -f DockerfileTest --rm -t docker_sql_transfer:dev-test .

test: build-test
	./test.sh

bash-test: build-test
	docker run -it --rm \
		--network host \
		-v "$(PWD)/tests:/tests" \
		-v /var/run/docker.sock:/var/run/docker.sock docker_sql_transfer:dev-test bash
