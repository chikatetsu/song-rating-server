from json import load as json_load
from sqlite3 import connect as sqlite_connect

from app.graph import Graph


class DBConnection:
    def __init__(self):
        self._connection = sqlite_connect("rank.sqlite" ,check_same_thread=False)
        self._cursor = self._connection.cursor()

    def load_db_from_json(self):
        with open("rates_graph.json", "r", encoding="utf-8") as f:
            rates_graph = json_load(f)

        visited = {}
        for node, songs in rates_graph.items():
            if node not in visited:
                self.insert_song(node)
                node_id = self.get_id_by_song_name(node)
                visited[node] = node_id
            else:
                node_id = visited[node]

            for song in songs:
                if song not in visited:
                    self.insert_song(song)
                    song_id = self.get_id_by_song_name(song)
                    visited[song] = song_id
                else:
                    song_id = visited[song]
                self.insert_vote(node_id, song_id)

    def load_graph(self) -> Graph:
        self._cursor.execute("SELECT better_id, worse_id FROM vote")
        rows = self._cursor.fetchall()
        graph = Graph()
        for row in rows:
            graph.create_edge(row[0], row[1])
        self._cursor.execute("SELECT id, name FROM song")
        rows = self._cursor.fetchall()
        for row in rows:
            graph.rename_node(int(row[0]), row[1])
        return graph

    def get_song_by_id(self, song_id: int) -> str:
        self._cursor.execute("SELECT name FROM song WHERE id = ?", (song_id,))
        song = self._cursor.fetchone()[0]
        return song

    def get_id_by_song_name(self, song_name: str) -> int:
        self._cursor.execute("SELECT id FROM song WHERE name = ?", (song_name,))
        song_id = int(self._cursor.fetchone()[0])
        return song_id

    def get_all_songs(self) -> dict[int, str]:
        self._cursor.execute("SELECT id, name FROM song")
        rows = self._cursor.fetchall()
        songs: dict[int, str] = {}
        for row in rows:
            songs[int(row[0])] = row[1]
        return songs

    def insert_vote(self, better_id: int, worse_id: int):
        self._cursor.execute("INSERT OR IGNORE INTO vote (better_id, worse_id) VALUES (?, ?)", (better_id, worse_id))
        self._connection.commit()

    def insert_song(self, song: str):
        self._cursor.execute("INSERT OR IGNORE INTO song (name) VALUES (?)", (song,))
        self._connection.commit()

    def disconnect(self):
        self._cursor.close()
        self._connection.close()


if __name__ == "__main__":
    db = DBConnection()
    db.load_db_from_json()
    db.disconnect()
