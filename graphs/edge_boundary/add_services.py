import networkx as nx

from graphs.utils.plot import draw_digraph


def add_services_v1(G_to: nx.DiGraph, G_from: nx.DiGraph, save_plot=""):
    """Add services to the graph G_to from the graph G_from.

    This method iterates over all nodes in G_to and adds its upstream services.
    """
    service_edges = {
        node: [edge[0] for edge in G_from.in_edges(node) if edge[0].startswith("S")]
        for node in G_from.nodes
    }

    def _add_upstream_edge(node):

        services = service_edges.get(node, [])
        for service in services:
            G_to.add_edge(service, node)
            _add_upstream_edge(service)

    G_to_original = G_to.copy()

    for downstream_node in G_to_original.nodes:
        _add_upstream_edge(downstream_node)

    return G_to


def add_services_v2(G_to: nx.graph, G_from: nx.graph, save_plot=""):
    """Add services to the graph G_to from the graph G_from.

    This method use `nx.edge_boundary` to recursively add services to the
    boundary of the graph G_to.
    """
    services = {node for node in G_from.nodes if node.startswith("S")}

    boundary_edges = set(
        nx.edge_boundary(G_from, services - set(G_to.nodes), G_to.nodes)
    ) | set(nx.edge_boundary(G_from, G_to.nodes, services & set(G_to.nodes)))

    if set(boundary_edges) - set(G_to.edges):
        G_to.add_edges_from(boundary_edges)
        add_services_v2(G_to, G_from, save_plot)

    return G_to

def add_services_v3(G_to: nx.graph, G_from: nx.graph, save_plot=""):
    """Add services to the graph G_to from the graph G_from.

    This method use `nx.compose` to combine the graph G_to with the services
    from the graph G_from.
    """
    services = {node for node in G_from.nodes if node.startswith("S")}
    H_from = G_from.subgraph(services | set(G_to.nodes))
    G_result = nx.compose(H_from, G_to)

    return G_result
