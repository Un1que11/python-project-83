import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor
from datetime import date
import logging

load_dotenv()
DBNAME = os.getenv('DBNAME')
USER_NAME = os.getenv('USER_NAME')
PASSWORD = os.getenv('PASSWORD')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')


def connect():
    return psycopg2.connect(
        dbname=DBNAME,
        user=USER_NAME,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )


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


def get_urls() -> list:
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            cursor.execute("""SELECT
                    u.id,
                    u.name
                    FROM urls AS u
                    ORDER BY u.id;""")
            urls = cursor.fetchall()
    return urls


def find_url(value) -> dict:
    with connect() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
            match value:
                case int():
                    cursor.execute(
                        """SELECT id, name, DATE(created_at) as created_at
                        FROM urls
                        WHERE id = %s;""", (value,))
                    row = cursor.fetchone()
                case str():
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
