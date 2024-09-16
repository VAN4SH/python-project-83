import psycopg2
from psycopg2.extras import NamedTupleCursor
import os
from dotenv import load_dotenv
import datetime


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def db_connect():
    return psycopg2.connect(DATABASE_URL)
    pass

def db_execute_without_conn(query, fetch=True, fetchall=False):
    if conn is None:
        with db_connect() as conn:
            return db_execute_with_conn(query, fetch, fetchall, conn)
    return db_execute_with_conn(query, fetch, fetchall, conn)


def db_execute(query, fetch=True, fetchall=False, conn):
    cursor = conn.cursor(cursor_factory=NamedTupleCursor)
    cursor.execute(query)
    if fetchall:
        return cursor.fetchall()
    return cursor.fetchone() if fetch else None


def get_url_by(param, value, from_db='urls'):
    return db_execute(
        f"""SELECT * FROM {from_db} WHERE {param} = '{value}'"""
    )


def get_all_urls():
    urls = db_execute(
        "SELECT id, name FROM urls ORDER BY id DESC",
        fetchall=True
    )
    all_checks = db_execute(
        "SELECT * FROM url_checks ORDER BY id DESC",
        fetchall=True
    )
    data = []
    for url in urls:
        url_checks = [check for check in all_checks if check.url_id == url.id]
        data.append({
            'id': url.id,
            'name': url.name,
            'status_code': url_checks[0].status_code if url_checks else '',
            'created_at': url_checks[0].created_at if url_checks else ''
        })
    return data


def insert_url(name):
    date = datetime.date.today()
    db_execute(
        f"""INSERT INTO urls (name, created_at)
            VALUES ('{name}', '{date}')""",
        fetch=False
    )
    return get_url_by('name', name)


def add_url_check(url_id, data):
    date = datetime.date.today()
    db_execute(
        f"""INSERT INTO url_checks (url_id, status_code,
                h1, title, description, created_at)
            VALUES ({url_id}, {data['status_code']},
                '{data['h1']}', '{data['title']}',
                '{data['description']}', '{date}') ;
            """,
        fetch=False
    )
    return get_url_by('id', url_id, from_db='url_checks')


def get_url_checks(url_id, fetchall=True):
    return db_execute(
        f"""SELECT * FROM url_checks WHERE url_id = '{url_id}'
            ORDER BY id DESC
            """,
        fetchall=fetchall
    )
