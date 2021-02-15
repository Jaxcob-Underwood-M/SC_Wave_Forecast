import sqlite3


class DatabaseConnection:
    def __init__(self, host):
        self.connection = None
        self.host = host

    def __enter__(self):
        self.connection = sqlite3.connect(self.host)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb: #if any error is not None close the connection without committing
            self.connection.close()
        else: #else close the connection with committing
            self.connection.commit()
            self.connection.close()
