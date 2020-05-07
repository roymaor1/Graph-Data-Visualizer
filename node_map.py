import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from networkx.algorithms.shortest_paths.weighted import single_source_dijkstra
import numpy as np
from PIL import Image

SRC_NAME = "miserables.json"


def build_graph(g):

    # Parse input JSON file
    with open(SRC_NAME) as json_file:
        data = json.load(json_file)

    # Add nodes to graph
    for node in data['nodes']:
        name, group_id = node['name'], node['group']
        g.add_node(name, group=group_id)
    nodes = list(g.nodes())

    # Add edges to graph
    for edge in data['links']:
        src, target, w = edge['source'], edge['target'], edge['value']
        g.add_edge(nodes[src], nodes[target], weight=w)


def choose_layout(g, node_to_group, groups):
    pos = nx.circular_layout(g)
    angs = np.linspace(0, 2 * np.pi, 1 + len(groups))
    repos = []
    rad = 3.5  # radius of circle
    for ang in angs:
        if ang > 0:
            # print(rad*np.cos(ea), rad*np.sin(ea))  # location of each cluster
            repos.append(np.array([rad * np.cos(ang), rad * np.sin(ang)]))
    group_to_posx = {}
    posx, next_posx = 0, 0
    for node in pos.keys():
        group = node_to_group[node]
        if group in group_to_posx:
            posx = group_to_posx[group]
        else:
            group_to_posx[group] = next_posx
            posx = next_posx
            next_posx += 1
        pos[node] += repos[posx]
    return pos


def plot_graph(g, src, target):

    # Map node groups to their respective color
    nodes = list(g.nodes())
    node_to_group = nx.get_node_attributes(g, 'group')
    groups = set(node_to_group.values())
    max_group_id = max(groups)
    group_to_color = {group: group / max_group_id for group in groups}
    node_colors = [group_to_color[node_to_group[node]] for node in nodes]

    # Choose graph layout
    pos = choose_layout(g, node_to_group, groups)

    # Node size in correspondence to degree
    d = dict(g.degree)

    # Find Shortest Path
    sp = find_shortest_path(g, src, target)
    sp_edges = list(zip(sp, sp[1:]))
    labels = nx.get_edge_attributes(g, 'weight')
    sp_labels = {e: labels[e] for e in sp_edges}

    # Draw the graph
    nx.draw(g, pos=pos, cmap=plt.get_cmap('gist_rainbow'),
            node_color=node_colors, with_labels=True,
            font_size=6, alpha=0.8, node_size=[v * 100 for v in d.values()])
    nx.draw_networkx_edges(g, pos=pos)
    nx.draw_networkx_edges(g, pos=pos, width=2, edgelist=sp_edges, edge_color="red")
    nx.draw_networkx_edge_labels(g, pos, edgelist=sp_edges, edge_labels=sp_labels)

    # Output the graph
    fig1 = plt.gcf()
    fig1.savefig('out.png', dpi=400)
    Image.open('out.png').show()


def find_shortest_path(g, src, target):
    try:
        path_sum, sp = single_source_dijkstra(g, src, target, weight='weight')
    except:
        raise ValueError("No such path exists, try different nodes") from None
    print("Found shortest path between {} and {}!".format(src, target))
    path = ""
    for node in sp:
        path += node + "->"
    print("Path (displayed in red): {}".format(path[:-2]))
    print("Path weight: {}".format(path_sum))
    return sp


def main(src, target):
    g = nx.DiGraph()
    build_graph(g)
    plot_graph(g, src, target)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
