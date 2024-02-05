import re
import os
import fnmatch
from pydantic import BaseModel
from typing import List
import json

PATH_BASE = "/home/mcfrank/notes/"
PATH_OUTPUT = "/home/mcfrank/celium/explorer/static/raw.json"


class Node(BaseModel):
    id: str
    name: str
    content: str


class Link(BaseModel):
    base_path: str
    origin: str
    source: str
    target: str
    name: str


def text_to_name(text: str) -> str:
    title = " ".join(text.split("\n")[0].split(" ")[1:])
    return title


def text_to_id(text: str) -> str:
    title = "-".join(text.split("\n")[0].split(" ")[1:])
    return title


def replace_non_url_links(markdown_text):
    # Function to replace non-URL links in markdown with a modified version
    def matchstuff(match):
        text = match.group(1)
        path = match.group(2)

        if path.endswith(".png") and "://" not in path:
            return f"[{text}](content/pngs/{path})"
        elif "://" not in path:
            print(f"replacing {path} with content/{path}")
            return f"[{text}](content/{path})"
        else:
            return f"[{text}]({path})"

    # Define the regular expression pattern for detecting markdown links
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'

    # Replace non-URL links with the modified version
    markdown_text_modified = re.sub(pattern, matchstuff, markdown_text)

    return markdown_text_modified


def extract_markdown_links(
        file_path: str, base_path: str = PATH_BASE
) -> (List[Link], str):
    pattern = r'\[([^]]+)\]\(([^)]+)\)'

    links = []
    content = ""

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(pattern, content)
        for match in matches:
            # Each match is a tuple (link text, URL)
            link = Link(source=text_to_id(content), origin=file_path,
                        name=match[0], target=match[1], base_path=base_path)
            links.append(link)

    return links, replace_non_url_links(content)


def get_all_links_and_nodes(
        base_path: str = PATH_BASE
) -> (List[Link], List[Node]):
    print(f"getting all links from {base_path}")
    all_links = []
    all_nodes = []
    for root, dirs, files in os.walk(base_path):
        if ".git" in root:
            continue
        print(f"currently in {root}")
        for filename in fnmatch.filter(files, '*.md'):
            full_path = os.path.join(root, filename)
            links, content = extract_markdown_links(full_path)
            id = text_to_id(content)
            title = text_to_name(content)
            node = Node(id=id, name=title, content=content)
            all_nodes.append(node)
            if links:
                all_links.extend(links)
                print(f"Extracted links from: {full_path}")
            else:
                print(f"Found no links in: {full_path}")
    return all_links, all_nodes


def make_phantom_nodes(nodes, edges):
    phantom_nodes = []
    for edge in edges:
        is_phantom = True
        for node in nodes:
            if edge.target == node.id:
                is_phantom = False
                break
        if is_phantom:
            content = ""
            if edge.target.endswith(".png"):
                content = f"![{edge.name}](content/pngs/{edge.target})"
            phantom_nodes.append(
                Node(id=edge.target, content=content, name=edge.name))
    return phantom_nodes


def prepare_nodes():
    all_links, all_nodes = get_all_links_and_nodes()

    phantom_nodes = make_phantom_nodes(all_nodes, all_links)
    print(phantom_nodes)
    all_nodes += phantom_nodes

    # Convert instances to list of dicts
    nodes = [node.dict() for node in all_nodes]
    edges = [link.dict() for link in all_links]

    graph = {"nodes": nodes, "edges": edges}

    # Convert list of dicts to JSON string
    with open(PATH_OUTPUT, "w") as f:
        f.write(json.dumps(graph, indent=4))


if __name__ == "__main__":
    prepare_nodes()
    pass
