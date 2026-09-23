ifneq (,$(wildcard ./.env))
    include .env
    export
endif

.PHONY: init-db check-products

init-db:
	docker exec -i mssql_products /opt/mssql-tools18/bin/sqlcmd -S "$${MSSQL_HOST}" -U "$${MSSQL_USER}" -P "$${MSSQL_SA_PASSWORD}" -C -i /dev/stdin < ./web-hook/sql/schema.sql

check-products:
	docker exec -i mssql_products /opt/mssql-tools18/bin/sqlcmd -S "$${MSSQL_HOST}" -U "$${MSSQL_USER}" -P "$${MSSQL_SA_PASSWORD}" -C -d "$${MSSQL_DB_NAME}" -Q "SELECT * FROM Products"
