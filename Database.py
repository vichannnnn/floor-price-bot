import sqlite3

class Database:
    @staticmethod
    def connect():
        conn = sqlite3.connect('bot.db', timeout=5.0)
        c = conn.cursor()
        return c

    @staticmethod
    def execute(statement, *args):
        c = Database.connect()
        c.execute(statement, args)
        c.connection.commit()
        c.connection.close()

    @staticmethod
    def get(statement, *args):
        c = Database.connect()
        c.execute(statement, args)
        res = c.fetchall()
        c.connection.close()
        return res
