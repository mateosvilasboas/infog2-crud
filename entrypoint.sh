#!/bin/sh

# Executa as migrações do banco de dados
poetry run alembic upgrade head

# Inicia a aplicação
poetry run uvicorn --host 0.0.0.0 --port 8000 project.main:app

# by https://fastapidozero.dunossauro.com/11/?h=dockeri#__tabbed_2_2
