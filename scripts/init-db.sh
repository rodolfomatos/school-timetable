#!/bin/bash
# init-db.sh - Script de inicialização do banco de dados
# Executado automaticamente pelo PostgreSQL na primeira inicialização

set -euo pipefail

# Aguarda o PostgreSQL estar pronto
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Aguardando PostgreSQL..."
  sleep 1
done

echo "PostgreSQL pronto. Executando inicialização..."

# Extensões úteis
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Extensões úteis
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    CREATE EXTENSION IF NOT EXISTS "btree_gin";
    CREATE EXTENSION IF NOT EXISTS "btree_gist";

    -- Configurações de performance
    ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
    ALTER SYSTEM SET pg_stat_statements.track = 'all';
    ALTER SYSTEM SET pg_stat_statements.max = 10000;
    
    -- Configurações de log
    ALTER SYSTEM SET log_min_duration_statement = 1000;
    ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
    ALTER SYSTEM SET log_checkpoints = on;
    ALTER SYSTEM SET log_connections = on;
    ALTER SYSTEM SET log_disconnections = on;
    ALTER SYSTEM SET log_lock_waits = on;
    
    -- Configurações de checkpoint
    ALTER SYSTEM SET checkpoint_completion_target = 0.9;
    ALTER SYSTEM SET wal_buffers = '16MB';
    ALTER SYSTEM SET default_statistics_target = 100;
    
    -- Recarregar configurações
    SELECT pg_reload_conf();
EOSQL

echo "Inicialização do banco de dados concluída com sucesso."