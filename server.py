# i know this is terrible code. but let me finish

from flask import Flask, send_from_directory
import os
import sqlite3


PORT = os.environ.get("PORT_EXPLORER", "8000")
DEBUG_EXPLORER = os.environ.get("DEBUG_EXPLORER", True)
PATH_DB = os.environ.get("PATH_DB", "data/graph.db")

TABLE_NODES = "nodes"
TABLE_EDGES = "edges"

app = Flask(__name__)


@app.route('/data/nodes')
def serve_nodes():
    conn = sqlite3.connect(PATH_DB)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {TABLE_NODES}")
    data = c.fetchall()
    nodes = []
    for row in data:
        node = {}
        for i, column in enumerate(c.description):
            node[column[0]] = row[i]
        nodes.append(node)
    return nodes


@app.route('/data/edges')
def serve_edges():
    conn = sqlite3.connect(PATH_DB)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {TABLE_EDGES}")
    data = c.fetchall()
    nodes = []
    for row in data:
        node = {}
        for i, column in enumerate(c.description):
            node[column[0]] = row[i]
        nodes.append(node)
    return nodes


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == "__main__":
    app.run(port=8000, debug=True)
