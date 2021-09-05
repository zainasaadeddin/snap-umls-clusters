from typing import List, Dict, Tuple, Optional, Any
import itertools

import numpy as np
from sklearn import cluster as skcluster
from sklearn import metrics as skmetrics

from . import Types


def count_terms(
        sentence_terms: Dict[int, List[str]],
        unique_terms
) -> Dict[str, int]:
    """

    Tracks how many times each term appear in sentences.
    Return a ranked dict.

    """
    counts = {
        umls_term: sum(umls_term in sentence_term
                       for sentence_term in sentence_terms.values())
        for umls_term in unique_terms
    }

    return dict(sorted(
        counts.items(),
        key=lambda item: item[1],
        reverse=True
    ))


def fetch_cluster_terms(scored_sentence_terms, labels, C):
    #assert min(labels) == min(scored_sentence_terms.keys()), f"{min(labels)} vs {min(scored_sentence_terms.keys())}"
    return {
        k: terms
        for k, terms in scored_sentence_terms.items()
        if labels[k - 1] == C
    }


def extract_sentence_terms(sentences: List[Types.Sentence]) -> Dict[int, List[str]]:
    return {
        sentence.index: [
            x[0]
            for x in sentence.extract_all_related_umls_terms()
        ]
        for sentence in sentences
    }


# FIXME
def extract_sentence_terms_score(
        sentences: List[Types.Sentence]) -> Dict[int, List[Tuple[str, float]]]:
    return {
        sentence.index: [
            x
            for x in sentence.extract_all_related_umls_terms()
        ]
        for sentence in sentences
    }


def extract_unique_terms(all_terms: Dict[Any, Any]) -> List[Any]:
    k = itertools.chain.from_iterable(all_terms.values())
    return list(set(k))


def build_matrix(unique_terms: List[str],
                 sentence_terms: Dict[int, Any]):
    """
    Build the feature matrix.

    """
    X = len(sentence_terms.keys())
    Y = len(unique_terms)
    matrix = np.zeros(shape=(X, Y))

    Terms = sorted(sentence_terms.items(), key=lambda T: T[0])
    for x, (_, sentence_umls_set) in enumerate(Terms):
        for y, unique_umls in enumerate(unique_terms):
            if False:  # DEPRECATED
                matrix[x, y] = sum([
                    score
                    for identifier, score in sentence_umls_set
                    if identifier == unique_umls
                ])
            sentence_term_ids = [
                identifier
                for (identifier, score) in sentence_umls_set
            ]
            matrix[x, y] = int(unique_umls in sentence_term_ids)

    #assert matrix.sum() > 0, "Empty feature matrix."
    return matrix


# FIXME: Deprecated?
def matrix_algorithm(sentences):
    sentence_terms = extract_sentence_terms(sentences)
    unique_terms = extract_unique_terms(sentence_terms)

    scored_sentence_terms = extract_sentence_terms_score(sentences)
    return build_matrix(unique_terms, scored_sentence_terms)


def silhouette(matrix, labels):
    return skmetrics.silhouette_score(matrix, labels)


def _clusterize_matrix(matrix, n_clusters, method="agglomerative") -> List[int]:
    if method == "agglomerative":
        c = skcluster.AgglomerativeClustering(
            n_clusters=n_clusters,
        )
        c.fit(matrix)

        return c.labels_

    if method == "":
        return []


def clusterize_matrix(matrix) -> Tuple[List[int], str]:
    score = -1.0

    methods = ["agglomerative"]
    # This range defines the allowed values for n clusters.
    for k in range(3, 20, 2):
        for method in methods:
            labels = _clusterize_matrix(matrix, k, method)
            S = silhouette(matrix, labels)
            if S > score:
                final_labels = labels
                method_id = f"{method}_{k}_{S}"
                score = S

    return final_labels, method_id


def retrieve_cluster_sentences(sentences, labels, C):
    return [
        sentence
        for i, sentence in enumerate(sentences)
        if labels[i] == C
    ]


def visualize_clusters(
        logger,
        sentences,
        labels,
        CUI_labels: Optional[Dict[str, str]] = None):

    def fetch_label(cui):
        try:
            return CUI_labels[cui][1]
        except KeyError:
            return "UNKNOWN_LABEL"

    for cluster in range(max(labels) + 1):
        cluster_sentences = retrieve_cluster_sentences(
            sentences, labels, cluster)
        Name = ""
        if CUI_labels is not None:
            cluster_common_cui = determine_common_cui(cluster_sentences)
            common_cui_labels = [
                fetch_label(cui)
                for cui in cluster_common_cui
            ]
            Name = "+".join(common_cui_labels[:12])

        logger.write(f"Cluster {cluster}: {Name}")
        for sentence in cluster_sentences:
            logger.write("\t" + sentence.text)


def determine_common_cui(sentences: List[Types.Sentence]) -> List[str]:
    """
    Search CUIs common to all sentences in a sentence group.

    """

    sentence_terms = extract_sentence_terms(sentences)
    unique_terms = extract_unique_terms(sentence_terms)

    return [
        term for term in unique_terms
        if all(
                term in single_sentence_terms
                for single_sentence_terms in sentence_terms.values()
        )
    ]


def agglomerate_features(feature_matrix):
    agg = skcluster.FeatureAgglomeration()
    return agg.fit_transform(feature_matrix)
