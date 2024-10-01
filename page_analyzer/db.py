import psycopg2
from psycopg2.extras import NamedTupleCursor
import datetime


def db_connect(app):
    return psycopg2.connect(app.database_url)


def db_execute(query, connection, fetch=True, fetchall=False):
    with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
        cursor.execute(query)
        if fetchall:
            return cursor.fetchall()
        return cursor.fetchone() if fetch else None


def get_url_by(param, value, connection, from_db="urls"):
    return db_execute(
        f"""SELECT * FROM {from_db} WHERE {param} = '{value}'""", connection=connection
    )


def get_all_urls(app, connection):
    query = """
        SELECT DISTINCT ON (urls.id)
            urls.id,
            urls.name,
            url_checks.status_code,
            url_checks.created_at
        FROM urls
        LEFT JOIN url_checks
        ON urls.id = url_checks.url_id
        ORDER BY urls.id DESC, url_checks.created_at DESC NULLS LAST
    """
    rows = db_execute(
        query,
        connection=connection,
        fetchall=True,
    )
    data = []
    for row in rows:
        data.append(
            {
                "id": row.id,
                "name": row.name,
                "status_code": row.status_code if row.status_code is not None else "",
                "created_at": row.created_at if row.created_at is not None else "",
            }
        )
    return data


def insert_url(name, connection):
    date = datetime.date.today()
    db_execute(
        f"""INSERT INTO urls (name, created_at)
            VALUES ('{name}', '{date}')""",
        connection=connection,
        fetch=False,
    )
    connection.commit()
    return get_url_by("name", name, connection=connection)


def insert_url_check(url_id, data, connection):
    date = datetime.date.today()
    db_execute(
        f"""INSERT INTO url_checks (url_id, status_code,
                h1, title, description, created_at)
            VALUES ({url_id}, {data['status_code']},
                '{data['h1']}', '{data['title']}',
                '{data['description']}', '{date}') ;
            """,
        connection=connection,
        fetch=False,
    )
    connection.commit()
    return get_url_by("id", url_id, connection=connection, from_db="url_checks")


def get_url_checks(url_id, connection, fetchall=True):
    return db_execute(
        f"""SELECT * FROM url_checks WHERE url_id = '{url_id}'
            ORDER BY id DESC
            """,
        connection=connection,
        fetchall=fetchall,
    )
