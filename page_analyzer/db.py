import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import date
import logging

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect():
    return psycopg2.connect(DATABASE_URL)


def add_url(name: str):
    try:
        with connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%(name)s, %(created_at)s)
                    RETURNING id;
                    """,
                    {'name': name, 'created_at': date.today()})
                id = cursor.fetchone()[0]
                return id
    except psycopg2.Error as err:
        logging.error(err)
        return err


def add_check(check: dict):
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO url_checks (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                    VALUES (
                        %(id)s,
                        %(status_code)s,
                        %(h1)s,
                        %(title)s,
                        %(description)s,
                        %(created_at)s)
                    RETURNING id;""", {
                        'id': check['id'],
                        'status_code': check['status_code'],
                        'h1': check['h1'],
                        'title': check['title'],
                        'description': str(check['description']),
                        'created_at': date.today()}
                )
                id = cur.fetchone()[0]
                return id
    except psycopg2.Error as err:
        logging.error(err)
        return err


def get_urls() -> list:
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                """SELECT DISTINCT
                    u.id,
                    u.name,
                    COALESCE(
                        CAST(
                            DATE(ch.created_at) AS varchar), '') as created_at,
                    COALESCE(ch.status_code, '') as status_code
                FROM urls as u
                LEFT JOIN url_checks AS ch
                ON u.id = ch.url_id
                AND ch.created_at =
                    (SELECT MAX(created_at) FROM url_checks
                    WHERE url_id = u.id)
                ORDER BY u.id DESC;""")
            rows = cur.fetchall()
    return rows


def get_checks(id: int) -> list:
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                """SELECT
                id,
                status_code,
                COALESCE(h1, '') as h1,
                COALESCE(title, '') as title,
                COALESCE(description, '') as description,
                DATE(created_at) as created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC;""", (id,))
            rows = cur.fetchall()
    return rows


def find_url(value) -> dict:
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            if isinstance(value, int):
                cursor.execute(
                    """SELECT id, name, DATE(created_at) as created_at
                    FROM urls
                    WHERE id = %s;""", (value,))
                row = cursor.fetchone()
            elif isinstance(value, str):
                cursor.execute(
                    """SELECT id, name, DATE(created_at) as created_at
                    FROM urls
                    WHERE name = %s;""", (value,))
                row = cursor.fetchone()
    return row


def is_exist_url(name: str) -> bool:
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM urls WHERE name = %s;", (name,)
            )
            result = cursor.fetchone()
    return bool(result[0])
