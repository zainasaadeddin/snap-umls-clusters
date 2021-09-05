from typing import Optional, List, Any
import os
import numpy as np
import matplotlib.pyplot as plt

from . import Cluster, Types, Concepts


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def plot_feature_matrix(matrix,
                        title,
                        output_filepath: str,
                        feature_ids: List[str] = [],
                        sentence_ids: List[Any] = []):

    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_subplot(111)

    # FIXME: Check this.
    try:
        ax.matshow(matrix)
    except ZeroDivisionError:
        return

    if feature_ids:
        ax.set_xticks(range(len(feature_ids)))
        ax.set_xticklabels(feature_ids, rotation='vertical', fontsize=5)

    if sentence_ids:
        ax.set_yticks(range(len(sentence_ids)))
        ax.set_yticklabels([str(x) for x in sentence_ids], fontsize=5)

    plt.tight_layout()

    plt.savefig(output_filepath, bbox_inches='tight')


def plot_distance_matrices(
        clustering_result: Types.ClusteringResult,
        output_filepath
):

    matrix = distance_matrix(clustering_result.feature_matrix)
    size = matrix.shape[0]
    labels = [str(x) for x in range(size)]

    plot_feature_matrix(
        matrix,
        "Distance Matrix - " + clustering_result.execution_id,
        output_filepath,
        feature_ids=labels,
        sentence_ids=labels
    )

    ax = plt.axes()
    ax.matshow(matrix)

def plot_cluster_mini_matrices(
        base_output_dir,
        scored_sentence_terms,
        labels,
        umls_name_map,
        execution_id: str
):

    for cluster in range(max(labels) + 1):
        filename = f"{execution_id}_{cluster}.png"

        cluster_terms = Cluster.fetch_cluster_terms(
            scored_sentence_terms,
            labels,
            cluster
        )

        cluster_unique_terms = Cluster.extract_unique_terms(
            cluster_terms)

        if not cluster_unique_terms:
            print(
                f"Skipping cluster matrix for {filename} "
                "due to the lack of features."
            )
            continue

        matrix = Cluster.build_matrix(
            cluster_unique_terms,
            cluster_terms
        )

        output_filepath = os.path.join(
            base_output_dir,
            "cluster_matrix",
            filename
        )

        ensure_dir(output_filepath)

        feature_ids = [
            umls_name_map[term][1]
            for term, score in cluster_unique_terms
        ]

        plot_feature_matrix(
            matrix,
            execution_id,
            output_filepath=output_filepath,
            feature_ids=feature_ids,
            sentence_ids=list(cluster_terms.keys())
        )


def reorder_matrix(matrix, labels):
    """
    Reorder the Sentences in a matrix to match the clustering.
    """

    new_index: List[int] = []
    for k in range(max(labels) + 1):
        for idx, V in enumerate(labels):
            if V == k:
                new_index.append(idx)

    assert len(new_index) == len(labels), str(new_index) + str(labels)

    return matrix[new_index]


def distance_matrix(feature_matrix):
    """
    Creates a distance matrix from a feature matrix.

    """

    D = feature_matrix.shape[0]
    matrix = np.zeros((D, D))
    for i in range(D):
        for j in range(D):
            matrix[i, j] = sum((feature_matrix[i] - feature_matrix[j]) ** 2)

    return matrix
