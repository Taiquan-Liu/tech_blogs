import networkx as nx


def draw_digraph(G, prog='dot', output_format="png", args=''):
    """Helper for plotting a NetworkX DiGraph"""
    A = nx.nx_agraph.to_agraph(G)

    # put all root nodes at the top
    roots = [n for n, d in G.in_degree() if d == 0]
    s = A.add_subgraph(rank='same')
    s.add_nodes_from(roots)

    A.layout(prog=prog, args=args)
    return A.draw(format=output_format)


def draw_graph(G, prog='dot', output_format="png", args=''):
    """Helper for plotting a NetworkX non-DiGraph"""
    A = nx.nx_agraph.to_agraph(G)

    A.layout(prog=prog, args=args)

    return A.draw(format=output_format)