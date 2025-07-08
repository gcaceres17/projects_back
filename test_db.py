#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print('✅ Conexión exitosa a PostgreSQL')
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f'Versión de PostgreSQL: {version[0]}')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'❌ Error de conexión: {e}')
