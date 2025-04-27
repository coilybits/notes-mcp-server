from pyignite import Client

from models.types import Query


class Notebook:
    PREFIX = "notes://"

    def __init__(self, dns: str, port: int):
        self.port = port
        self.dns = dns
        self.client: Client = Client()
        self.init()

    def init(self):
        try:
            with self.client.connect(self.dns, self.port):
                for query in [Query.CREATE_NOTE_META]:
                    self.client.sql(query)
        finally:
            self.client.close()

    def notes(self) -> list[(str, str)]:
        results = []
        with self.client.connect(self.dns, self.port):
            with self.client.sql(Query.GET_NOTES) as cursor:
                for name, description in cursor:
                    results.append((name, description))
        return results

    def create(self, name: str, description: str):
        with self.client.connect(self.dns, self.port):
            self.client.sql(Query.INSERT_NOTE, query_args=[name, description])

    def remove(self, name):
        with self.client.connect(self.dns, self.port):
            self.client.sql(Query.REMOVE_NOTE, query_args=[name])

    def get(self, name):
        results = []
        with self.client.connect(self.dns, self.port):
            with self.client.sql(Query.GET_NOTE, query_args=[name]) as cursor:
                for name, description in cursor:
                    results.append((name, description))
        return results
