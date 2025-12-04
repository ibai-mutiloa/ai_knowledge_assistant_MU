from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import Json
import os
from dotenv import load_dotenv
import openai
import numpy as np

# Cargar variables de entorno
load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Conexión a la base de datos
def get_conn():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

# FastAPI app
app = FastAPI()

# Modelo de documento
class Document(BaseModel):
    title: str
    content: str

# Endpoint para subir documentos
@app.post("/documents/")
def add_document(doc: Document):
    # Generar embedding usando OpenAI
    response = openai.Embedding.create(
        input=doc.content,
        model="text-embedding-3-small"  # o tu modelo de Azure
    )
    embedding = list(response['data'][0]['embedding'])


    # Guardar en PostgreSQL
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO documents (title, content, embedding) VALUES (%s, %s, %s)",
                (doc.title, doc.content, embedding))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success", "title": doc.title}

# Endpoint para buscar documentos similares
class Query(BaseModel):
    question: str

@app.post("/search/")
def search_documents(query: Query):
    # Generar embedding de la pregunta
    response = openai.Embedding.create(
        input=query.question,
        model="text-embedding-3-small"
    )
    query_embedding = list(response['data'][0]['embedding'])

    # Buscar en la DB
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT title, content 
        FROM documents
        ORDER BY embedding <-> %s
        LIMIT 1
    """, (query_embedding,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return {"best_match": None}

    title, content = result

    return {
        "question": query.question,
        "title": title,
        "content": content,
    }