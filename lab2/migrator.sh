#!/bin/bash


DB_NAME="lab_db"        
DB_USER="lab_user"      
DB_HOST="localhost"     
DB_PORT="5432"           


MIGRATIONS_DIR="./migrations"


run_sql() {
    local file="$1"
    echo ">>> Выполняю SQL из файла: $file"
    psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -f "$file"
}

run_sql_c() {
    local sql="$1"
    psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -c "$sql"
}


run_sql_c "CREATE TABLE IF NOT EXISTS migrations (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"


APPLIED=$(psql -U "$DB_USER" -d "$DB_NAME" -h "$DB_HOST" -p "$DB_PORT" -t -c "SELECT migration_name FROM migrations;")


for file in "$MIGRATIONS_DIR"/*.sql; do
    migration_name=$(basename "$file")

    if echo "$APPLIED" | grep -q "$migration_name"; then
        echo "Миграция '$migration_name' уже применена, пропускаю."
    else
        echo "Применяю миграцию: $migration_name"
        run_sql "$file"
        safe_name=$(printf "%q" "$migration_name")
        run_sql_c "INSERT INTO migrations (migration_name) VALUES ('$safe_name');"
        echo "Миграция '$migration_name' применена успешно!"
    fi
done

echo ">>> Все миграции обработаны."
