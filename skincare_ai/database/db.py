"""
Thin MySQL connection helper using mysql-connector-python.
Call get_db() inside a Flask request context.
"""
import mysql.connector
from flask import g, current_app


def get_db():
    """Return a cached DB connection for the current request."""
    if 'db' not in g:
        cfg = current_app.config
        g.db = mysql.connector.connect(
            host     = cfg['MYSQL_HOST'],
            user     = cfg['MYSQL_USER'],
            password = cfg['MYSQL_PASSWORD'],
            database = cfg['MYSQL_DB'],
            port     = cfg['MYSQL_PORT'],
            autocommit = False,
            charset  = 'utf8mb4'
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()


def query(sql, params=(), fetchone=False, fetchall=False, commit=False):
    """
    Convenience wrapper.
    Returns: lastrowid  (commit=True)
             single row (fetchone=True)
             all rows   (fetchall=True)
             cursor     (default)
    """
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, params)
    if commit:
        db.commit()
        return cur.lastrowid
    if fetchone:
        return cur.fetchone()
    if fetchall:
        return cur.fetchall()
    return cur


def init_app(app):
    app.teardown_appcontext(close_db)
