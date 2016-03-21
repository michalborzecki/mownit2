import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
from networkx.drawing.nx_agraph import graphviz_layout
import math


def main():
    convert("1684.edges", "input2.txt", 40, 10, 4, 100)
    handle_file("input2.txt")


def convert(path, output_path, cut_to_n_nodes, max_edges, max_edges_2, voltage):
    # read edge list from file
    g = nx.read_weighted_edgelist(path, nodetype=int)
    # generate some random resistance
    for (x, y) in nx.edges(g):
         g[x][y]['weight'] = random.randint(1, 10)

    # let g be the biggest consistent subgraph (in the best case,
    # the whole graph is consistent)
    # g = max(nx.connected_component_subgraphs(g), key=len)

    # cycles = nx.cycle_basis(g)
    # nodes = [x for cycle in cycles for x in cycle]
    # g.remove_nodes_from([x for x in nx.nodes(g) if x not in nodes])

    x1, x2 = nx.nodes(g)[:2]
    nodes_set = {x1, x2}
    nodes_set_left = {x1, x2}
    i = 2
    while i < cut_to_n_nodes:
        for node in nx.nodes(g)[2:]:
            if node in nodes_set:
                continue

            intersect = set(nx.neighbors(g, node)).intersection(nodes_set_left)
            if len(intersect) >= 2:
                i += 1
                while len(intersect) > 2:
                    g.remove_edge(node, intersect.pop())
                nodes_set.add(node)
                print(node)
                if len(intersect) < max_edges:
                    nodes_set_left.add(node)
                for neighbour in intersect:
                    if len(set(nx.neighbors(g, neighbour)).intersection(nodes_set)) >= max_edges:
                        nodes_set_left.remove(neighbour)
                        for neighbour2 in nx.neighbors(g, neighbour):
                            if neighbour2 not in nodes_set:
                                g.remove_edge(neighbour, neighbour2)
            if i == cut_to_n_nodes:
                break

    unused = [node for node in nx.nodes(g) if node not in nodes_set]
    g.remove_nodes_from(unused)

    # remove excess edges
    for node in nx.nodes(g):
        neighbours = tuple(nx.all_neighbors(g, node))
        overmax = len(neighbours) - max_edges_2
        if overmax > 0:
            i = 0
            for neighbour in neighbours:
                if len(tuple(nx.all_neighbors(g, neighbour))) == 2:
                    continue
                backup = g[node][neighbour]
                g.remove_edge(node, neighbour)
                if not nx.has_path(g, node, neighbour):
                    g.add_edge(node, neighbour, backup)
                else:
                    i += 1
                if i == overmax:
                    break

    # save to file
    lines = [x + "\n" for x in nx.generate_edgelist(g, data=['weight'])]
    o = open(output_path, "w")
    # x1, x2 = nx.nodes(g)[:2]
    o.write(" ".join((str(x1), str(x2), str(voltage))) + "\n")
    o.writelines(lines)


def handle_file(path):
    i = open(path, "r")
    lines = i.readlines()
    g = nx.parse_edgelist(lines[1:], nodetype=int, data=(('weight', float),))
    x1, x2, vol = lines[0].rstrip("\n").split(" ")
    i.close()
    x1 = int(x1)
    x2 = int(x2)
    vol = float(vol)
    g.add_node(0)
    g.add_weighted_edges_from([(0, x1, 0), (0, x2, 0)])
    calculate(g, vol)

    # create directed graph for presentation
    result = nx.DiGraph()
    result.add_nodes_from(nx.nodes(g))
    for x1, x2 in nx.edges(g):
        sx1, sx2 = tuple(sorted((x1, x2)))
        if g[x1][x2]['current'] > 0:
            result.add_edge(sx1, sx2, current=g[x1][x2]['current'])
        else:
            result.add_edge(sx2, sx1, current=-g[x1][x2]['current'])

    pos = graphviz_layout(result, prog='sfdp',)
    nx.draw_networkx_nodes(result, pos=pos, node_size=250, node_color='white')

    edges = nx.edges(result)
    currents_dict = nx.get_edge_attributes(result, 'current')
    currents_list = tuple(currents_dict[e] for e in edges)
    widths_list = tuple(0.3 + 4 * x/max(currents_list) for x in currents_list)
    colors = ("green", "yellow", "red")
    colors_list = [colors[(math.floor(len(colors)*x/max(widths_list) - 0.1))]
                   for x in widths_list]
    for key, val in currents_dict.items():
        currents_dict[key] = "{:.1f}".format(val)
    nx.draw_networkx_edges(result, pos=pos, edgelist=edges, width=widths_list,
                           edge_color=colors_list)
    bbox_props = dict(boxstyle="square,pad=0", fc="none", ec='none', lw=2)
    nx.draw_networkx_edge_labels(result, pos=pos, edge_labels=currents_dict,
                                 font_size=8, bbox=bbox_props)
    nx.draw_networkx_labels(result, pos=pos, font_size=8)
    plt.get_current_fig_manager().full_screen_toggle()
    plt.show()


def calculate(g, voltage):
    edges_num = nx.number_of_edges(g)
    # sort nodes in edges
    edges = [edge if edge[0] < edge[1] else (edge[1], edge[0])
             for edge in nx.edges(g)]

    a = np.zeros((edges_num, edges_num))
    b = np.zeros((edges_num, 1))
    i = 0
    # first law
    for node in [node for node in nx.nodes(g) if node != 0]:
        for neighbor in nx.all_neighbors(g, node):
            edge = tuple(sorted((node, neighbor)))
            a[i][edges.index(edge)] = 1 if neighbor < node else -1
        i += 1
    # second law
    cycles = nx.cycle_basis(g, 0)
    for cycle in cycles:
        for j in range(0, len(cycle)):
            node = cycle[j]
            next_node = cycle[(j + 1) % len(cycle)]
            edge = tuple(sorted((node, next_node)))
            resistance = g[node][next_node]['weight']
            a[i][edges.index(edge)] = resistance if node < next_node else -resistance
        if 0 in cycle:
            b[i] = voltage
        i += 1
    # solve
    x = np.linalg.solve(a, b)
    for (x1, x2), res in zip(edges, x):
        g[x1][x2]['current'] = res[0]

if __name__ == "__main__":
    main()
