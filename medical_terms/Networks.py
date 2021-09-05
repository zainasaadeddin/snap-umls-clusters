from typing import List
import networkx as nx
import itertools

from . import Types, Cluster

import matplotlib.pyplot as plt


def build_knowledge_graph(
        clustering_result: Types.ClusteringResult,
        umls_universes,
        umls_name_map,
        output_filepath):

    # Prepare data for edge score calculation;
    concept_names = clustering_result.expanded_unique_terms
    cluster_sentence_terms = [
        Cluster.fetch_cluster_terms(
            clustering_result.expanded_scored_terms,
            clustering_result.cluster_labels,
            C
        )
        for C in range(max(clustering_result.cluster_labels))
    ]

    cluster_terms = [
        list(itertools.chain.from_iterable(cluster_sentences.values()))
        for cluster_sentences in cluster_sentence_terms
    ]

    # Calculate edge scores;
    edgelist = []
    for i, icui in enumerate(concept_names):
        for j, jcui in enumerate(concept_names):
            if j >= i:
                score = 0
                for cluster_term in cluster_terms:
                    if icui in cluster_term and jcui in cluster_term:
                        score = 1
                edgelist.append((icui, jcui, score))

    graph = convert_graph(
        edgelist,
        "Graph - " + clustering_result.execution_id
    )

    # Define node colors;
    color_map: List[str] = []
    for node in graph:
        if node in umls_universes[Types.ExpansionMethod.ancestors]:
            color_map.append('blue')
        elif node in umls_universes[Types.ExpansionMethod.core]:
            color_map.append('green')
        else:
            color_map.append('gray')
    drawgraph(graph, color_map, output_filepath)


def convert_graph(edgelist, name):
    graph = nx.Graph()
    # add weights to the edges
    graph.add_weighted_edges_from(edgelist)
    graph.name = name

    print(nx.info(graph))
    return graph


def drawgraph(graph, colormap, output_path, density=False):
    edges, weights = zip(*nx.get_edge_attributes(graph,'weight').items())
    pos = nx.spring_layout(graph, k=0.05, seed=42)

    plt.clf()
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111)

    nx.draw_networkx(
        graph,
        pos,
        with_labels=True,
        node_size=20,
        node_color=colormap,
        edgelist=edges,
        edge_color=weights,
        #edge_cmap=plt.cm.Blues_r,
        style="solid",
        width=1,
        ax=ax
    )
    #plt.subplots_adjust(left=2, bottom=3.2, right=6, top=6)

    plt.savefig(output_path, bbox_inches='tight')
    plt.clf()
