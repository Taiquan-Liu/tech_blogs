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
        G_to_before = G_to.copy()
        _add_upstream_edge(downstream_node)

        if save_plot:
            draw_digraph(
                G=G_from,
                colored_nodes={node: "included" for node in G_to_before.nodes},
                colored_edges={edge: "included" for edge in G_to_before.edges},
                filename=save_plot,
            )
            draw_digraph(
                G=G_from,
                colored_nodes={
                    **{node: "included" for node in G_to_before.nodes},
                    **{downstream_node: "from"},
                    **{node: "to" for node in G_to.nodes - G_to_before.nodes},
                },
                colored_edges={
                    **{edge: "included" for edge in G_to_before.edges},
                    **{edge: "to" for edge in G_to.edges - G_to_before.edges},
                },
                filename=save_plot,
            )

    if save_plot:
        draw_digraph(
            G=G_from,
            colored_nodes={node: "included" for node in G_to.nodes},
            colored_edges={edge: "included" for edge in G_to.edges},
            filename=save_plot,
        )

    es_edges = {
        edge for edge in G_from.edges if edge[0].startswith("E") and edge[1].startswith("S")
    }

    for es_edge in es_edges:
        if es_edge[0] in G_to.nodes and es_edge[1] in G_to.nodes:

            if save_plot:
                draw_digraph(
                    G=G_from,
                    colored_nodes={
                        **{node: "included" for node in G_to.nodes},
                        es_edge[0]: "from",
                        es_edge[1]: "from",
                    },
                    colored_edges={
                        **{edge: "included" for edge in G_to.edges},
                        **{es_edge: "to"},
                    },
                    filename=save_plot,
                )

            G_to.add_edge(es_edge[0], es_edge[1])

            if save_plot:
                draw_digraph(
                    G=G_from,
                    colored_nodes={node: "included" for node in G_to.nodes},
                    colored_edges={edge: "included" for edge in G_to.edges},
                    filename=save_plot,
                )

    if save_plot:
        draw_digraph(
            G=G_from,
            colored_nodes={node: "included" for node in G_to.nodes},
            colored_edges={edge: "included" for edge in G_to.edges},
            filename=save_plot,
        )

    return G_to


def add_services_v2(G_to: nx.graph, G_from: nx.graph, save_plot=""):
    """Add services to the graph G_to from the graph G_from.

    This method use `nx.edge_boundary` to recursively add services to the
    boundary of the graph G_to.
    """
    if save_plot:
        draw_digraph(
            G=G_from,
            colored_nodes={node: "included" for node in G_to.nodes},
            colored_edges={edge: "included" for edge in G_to.edges},
            filename=save_plot,
        )

    services = {node for node in G_from.nodes if node.startswith("S")}

    boundary_edges = set(
        nx.edge_boundary(G_from, services - set(G_to.nodes), G_to.nodes)
    ) | set(nx.edge_boundary(G_from, G_to.nodes, services & set(G_to.nodes)))

    if set(boundary_edges) - set(G_to.edges):
        G_to_old = G_to.copy()
        G_to.add_edges_from(boundary_edges)

        if save_plot:
            new_nodes = G_to.nodes - G_to_old.nodes
            new_edges = G_to.edges - G_to_old.edges
            draw_digraph(
                G=G_from,
                colored_nodes={
                    **{node: "included" for node in G_to_old.nodes},
                    **{
                        node: "from"
                        for node in {
                            boundary_node
                            for new_edge in new_edges
                            for boundary_node in new_edge
                            if boundary_node not in new_nodes
                        }
                    },
                    **{node: "to" for node in new_nodes},
                },
                colored_edges={
                    **{edge: "included" for edge in G_to_old.edges},
                    **{edge: "to" for edge in new_edges},
                },
                filename=save_plot,
            )

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

    if save_plot:
        draw_digraph(
            G=G_from,
            colored_nodes={node: "included" for node in G_to.nodes},
            colored_edges={edge: "included" for edge in G_to.edges},
            filename=save_plot,
        )
        draw_digraph(
            G=G_from,
            colored_nodes={
                **{node: "from" for node in G_to.nodes},
                **{node: "to" for node in H_from.nodes - G_to.nodes},
            },
            colored_edges={
                **{edge: "to" for edge in H_from.edges - G_to.edges},
            },
            filename=save_plot,
        )
        draw_digraph(
            G=G_from,
            colored_nodes={node: "included" for node in G_result.nodes},
            colored_edges={edge: "included" for edge in G_result.edges},
            filename=save_plot,
        )

    return G_result
