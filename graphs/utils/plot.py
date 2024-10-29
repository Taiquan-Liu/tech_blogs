import os
from pathlib import Path

import networkx as nx
from pygraphviz import AGraph

PLOT_DIR = Path(os.path.dirname(__file__)) / "plots"

COLORS = {
    "included": "#52eeb8",
    "from": "#eeb152",
    "to": "#ee5b52",
}


def draw_digraph(
    G,
    colored_nodes={},
    colored_edges={},
    rank=True,
    prog="dot",
    output_format="png",
    args="",
    filename="",
):
    """Helper for plotting a NetworkX DiGraph"""
    A: AGraph = nx.nx_agraph.to_agraph(G)
    A.node_attr["style"] = "filled"

    # for node_name in A.nodes():
    #     node = A.get_node(node_name)
    #     if color := COLORS.get(node.attr["status"]):
    #         node.attr["fillcolor"] = color

    # for edge_name in A.edges():
    #     edge = A.get_edge(*edge_name)
    #     if color := COLORS.get(edge.attr["status"]):
    #         edge.attr["color"] = color

    for node, color in colored_nodes.items():
        assert node in G.nodes(), f"Node {node} not in graph"
        A.get_node(node).attr["fillcolor"] = COLORS.get(color, color)

    for edge, color in colored_edges.items():
        assert edge in G.edges(), f"Edge {edge} not in graph"
        A.get_edge(*edge).attr["color"] = COLORS.get(color, color)

    # put all root nodes at the top
    if rank:
        roots = [n for n, d in G.in_degree() if d == 0]
        s = A.add_subgraph(rank="same")
        s.add_nodes_from(roots)

    for node in A.nodes():
        if node.name.startswith("S"):
            node.attr["shape"] = "box"

    A.layout(prog=prog, args=args)

    if filename.startswith("auto"):
        func_name = filename.split("_", 1)[1]
        plot_dir = PLOT_DIR / func_name
        plot_dir.mkdir(parents=True, exist_ok=True)
        existing_files = list(plot_dir.glob(f"*.{output_format}"))
        if existing_files:
            max_index = max(int(f.stem) for f in existing_files)
            filename = plot_dir / f"{max_index + 1}.{output_format}"
        else:
            filename = plot_dir / f"0.{output_format}"
        A.draw(filename, format=output_format)
    elif filename:
        A.draw(filename, format=output_format)
    else:
        return A.draw(format=output_format)


def draw_graph(
    G,
    colored_nodes={},
    colored_edges={},
    prog="dot",
    output_format="png",
    args="",
    filename=None,
):
    """Helper for plotting a NetworkX non-DiGraph"""
    A: AGraph = nx.nx_agraph.to_agraph(G)
    A.node_attr["style"] = "filled"

    for node, color in colored_nodes.items():
        assert node in G.nodes(), f"Node {node} not in graph"
        A.get_node(node).attr["fillcolor"] = color

    for edge, color in colored_edges.items():
        assert (edge in G.edges()) or (
            edge[::-1] in G.edges()
        ), f"Edge {edge} not in graph"
        A.get_edge(*edge).attr["color"] = color

    for node in A.nodes():
        if node.name.startswith("S"):
            node.attr["shape"] = "box"

    A.layout(prog=prog, args=args)

    if filename:
        A.draw(filename, format=output_format)
    else:
        return A.draw(format=output_format)
