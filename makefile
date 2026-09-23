ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: init-db

init-db:
	docker exec -i mssql_products /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$${MSSQL_SA_PASSWORD}" -C -i /dev/stdin < ./web-hook/sql/init.sql
