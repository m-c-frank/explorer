# %%
from sqlite3 import IntegrityError
from pydantic import BaseModel

import os
from glob import glob

BASE_PATH = os.environ.get("PATH_CELIUM", "/home/mcfrank/celium")
PATH_INPUT = os.environ.get("PATH_INPUT", "/home/mcfrank/notes")
PATH_DB = os.environ.get("PATH_DB", "graph.db")


TABLE_NODES = "nodes"
TABLE_EDGES = "edges"
files = glob(PATH_INPUT + "/*.md")

print(files)

# %%


class Node(BaseModel):
    type: str
    text: str
    id: str
    local_id: str


def insert_node(connection, cursor, node):
    try:
        with connection:
            cursor.execute(f"INSERT INTO {TABLE_NODES}(type, text, id, local_id) SELECT ?,?,?,?", (node.type, node.text, node.id, node.local_id))
        connection.commit()
        return True
    except IntegrityError as e:
        print("error inserting node:", e)
        connection.rollback()
        return False


class Edge(BaseModel):
    source: str
    target: str


def insert_edge(connection, cursor, edge):
    try:
        with connection:
            cursor.execute(f"INSERT INTO {TABLE_EDGES}(source, target) SELECT ?,?", (edge.source, edge.target))
        connection.commit()
        return True
    except IntegrityError as e:
        print("error inserting edge:", e)
        connection.rollback()
    return False

# %%

import sqlite3
conn = sqlite3.connect(PATH_DB)
c = conn.cursor()

# %%
# create a table that uses id as the primary key and local_id as another primary key

c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NODES} (type TEXT, text TEXT, id TEXT, local_id TEXT PRIMARY KEY)''')

c.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_EDGES} (source TEXT, target TEXT, PRIMARY KEY(source, target))''')

# %%
import os
from uuid import uuid4

nodes = []
for file in files:
    with open(file, "r") as f:
        node = Node(
                type="file",
                text=f.read(),
                id=str(uuid4()),
                local_id=file
            )
        nodes.append(node)
        insert_node(conn, c, node)
        
# %%
stored_nodes = c.execute(f"SELECT * FROM {TABLE_NODES}").fetchall()
print("stored nodes:", stored_nodes)
print("number of stored nodes:", len(stored_nodes))
print("number of files:", len(files))

# %%
# from ollama import Client

# client = Client(
#     host="http://192.168.2.177:11434"
# )

# # %%
# system_message = "# system message\n\nyou are an expert in the concept of the following note. you provide orthogonal viewpoints and specialize in rephrasing the core concept from a completely orthogonal viewpoint"
# pre_prompt = "\n\n## pre prompt\n\nhere is the note you need to rephrase:\n\n"
# alignment_prompt = "\n\n## alignment prompt\n\nbe creative and respond with a high information to token ratio. please dont speak to much and get straight to the core of it"
# response_primer = "\n\n## response\n\nconsidering only the given context given within <c></c>:\nfrom the perspective of "

# def construct_prompt(node):
#     def to_markdown_codeblock(text):
#         return "\n\n <c>```markdown\n" + text + "\n```</c>"
#     return system_message + pre_prompt + to_markdown_codeblock(node.text) + alignment_prompt + response_primer


# for node in nodes:
#     user_prompt = construct_prompt(node)
#     response = client.generate(model="mistral-ft-optimized-1218:latest",prompt=user_prompt, stream=False)
#     print(response)
#     print(response["response"])
#     new_id = str(uuid4()) # fix this ugly thing
#     new_node = Node(
#         type="generated",
#         text=response["response"],
#         local_id=new_id,
#         id=new_id
#     )
#     new_edge = Edge(
#         source=node.id,
#         target=new_node.id,
#     ) 

#     insert_node(conn, c, new_node)    
#     insert_edge(conn, c, new_edge)

# # %%

# import random

# system_message = "# system message\n\nyou are an expert in the concept of the following topic. you always respond with nothing except the integration of two separate concetps. you specialize in interpreting the core concepts using counterfactual and orthogonal viewpoints"
# pre_prompt_a = "\n\n## pre prompt a\n\nhere is the first note you need to thoroughly examine and nderstand:\n\n"
# pre_prompt_b = "\n\n## pre prompt b\n\nhere is the second note you need to thoroughly examine and understand:\n\n"
# alignment_prompt = "\n\n## alignment prompt\n\nbe creative and respond with a high information to token ratio. please dont speak to much and get straight to the core of it"
# response_primer = "\n\n## response\n\nafter thoroughly examining and taking some time to collect my thoughts, i conclude, solely based on the context provided from within the given <c></c> tags:\n"

# def construct_merge_prompt(node_a, node_b):
#     def to_markdown_codeblock(text):
#         return "\n\n <c>```markdown\n" + text + "\n```</c>"
#     return system_message + pre_prompt_a + to_markdown_codeblock(node_a.text) + pre_prompt_b + to_markdown_codeblock(node_b.text) + alignment_prompt + response_primer

# while True:
#     for i, node in enumerate(nodes):
#         node_a = node
#         node_b = random.choice(nodes)
#         user_prompt = construct_merge_prompt(node_a, node_b)
#         response = client.generate(model="mistral-ft-optimized-1218:latest",prompt=user_prompt, stream=False)
#         print(response)
#         print(response["response"])
#         new_id = str(uuid4()) # fix this ugly thing
#         new_node = Node(
#             type="generated",
#             text=response["response"],
#             local_id=new_id,
#             id=new_id
#         )

#         new_edge_a = Edge(
#             source=node_a.id,
#             target=new_node.id,
#         ) 

#         new_edge_b = Edge(
#             source=node_b.id,
#             target=new_node.id,
#         ) 

#         insert_node(conn, c, new_node)    
#         insert_edge(conn, c, new_edge_a)
#         insert_edge(conn, c, new_edge_b)

# # %%
