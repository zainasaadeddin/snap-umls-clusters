"""

Main module.

"""
from typing import Dict, List
import argparse
import copy
import os
import shutil

from medical_terms import SentenceReader, Processor, Cluster, UMLS_local
from medical_terms import Concepts, Record
from medical_terms import Networks, Analysis, Types, UMLS_remote


class Logger():
    """
    Coordinates output file writing.

    """
    def __init__(self, filepath):
        self.stream = open(filepath, 'w')

    def __del__(self):
        self.stream.close()

    def write(self, message):
        print(message)
        self.stream.write(str(message) + '\n')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--umls-db-path",
        dest="umls_database_filepath",
        default="",
        help="Path to directory where UMLS Thesaurus files and databases are located."
    )

    parser.add_argument(
        'filepath',
        metavar='N',
        help="Questionnaire PDF filepath."
    )

    return parser.parse_args()


def load_sentences(filepath):
    raw_sentences = SentenceReader.load_sentences_from_pdf(filepath)
    model = Processor.initialize_model()

    # !. Load sentences and locate included UMLS terms.
    loaded_sentences = []
    base_logger = Logger("sentences-terms.txt")
    for sentence in raw_sentences:
        entities = Processor.process_sentence(model, sentence)
        sentence.umls_entities = entities
        sentence.show(base_logger)
        # umls = Processor.locate_umls_entities(model, sentence)
        loaded_sentences.append(sentence)

    return loaded_sentences


def remove_semantic_types(sentences, umls_name_map, category_blacklist):
    atemp_sentences = copy.deepcopy(sentences)
    for sentence in atemp_sentences:
        for token in list(sentence.umls_entities.keys()):
            w = sentence.umls_entities[token]
            sentence.umls_entities[token] = [
                (term, score)
                for term, score in w
                if term in umls_name_map.keys() and umls_name_map[term][2] not in category_blacklist
            ]

    return atemp_sentences


def main():
    arguments = parse_arguments()

    loaded_sentences = load_sentences(arguments.filepath)

    Processor.filter_term_scores(loaded_sentences)

    # Initialize UMLS concept retrievers
    UMLS = UMLS_local.UMLS(arguments.umls_database_filepath)
    remote_umls_agent = UMLS_remote.UMLS()

    #
    #
    # ...
    ExpansionMethods = [
        [Types.ExpansionMethod.core],
        [Types.ExpansionMethod.core, Types.ExpansionMethod.ancestors],
        [Types.ExpansionMethod.ancestors],
    ]

    sentence_grouping_blacklists = [
        ("T", []),
        ("NO_T", ["Temporal Concept"])
    ]

    sentence_terms = Cluster.extract_sentence_terms(loaded_sentences)
    unique_terms = Cluster.extract_unique_terms(sentence_terms)

    cui_database = {
        cui: Types.CUIRecord(
            cui,
            "",
            ancestors=UMLS.get_relationships(cui, [Types.ExpansionMethod.ancestors]),
            descendants=UMLS.get_relationships(cui, [Types.ExpansionMethod.descendants])
        )
        for cui in unique_terms
    }

    umls_universes = {
        Types.ExpansionMethod.ancestors: Concepts.get_all_subgroup(
            cui_database,
            group_name=Types.ExpansionMethod.ancestors),
        Types.ExpansionMethod.descendants: Concepts.get_all_subgroup(
            cui_database,
            group_name=Types.ExpansionMethod.descendants),
        Types.ExpansionMethod.core: set(unique_terms)
    }

    named_set = set.union(
        umls_universes[Types.ExpansionMethod.ancestors],
        umls_universes[Types.ExpansionMethod.core]
    )

    print(len(named_set))
    umls_name_map = Record.manage_cached_cui_name_map(
        remote_umls_agent,
        named_set
    )

    base_output_dir = "output"
    if os.path.isdir(base_output_dir):
        shutil.rmtree(base_output_dir)
    os.mkdir(base_output_dir)

    print("Analysis initialized...")
    for output_file_prefix, semantic_blacklist in sentence_grouping_blacklists:
        logger = Logger(f"{output_file_prefix}-results.txt")

        all_results: List[Types.ClusteringResult] = []
        # Apply preprocessing;
        sentences = remove_semantic_types(
            loaded_sentences,
            umls_name_map,
            semantic_blacklist
        )

        for ExpansionMethod in ExpansionMethods:
            expansion_code = "+".join([m.name for m in ExpansionMethod])
            execution_id = f"{output_file_prefix}-{expansion_code}"
            run_result = execute_single_run(
                logger,
                UMLS,
                sentences,
                execution_id,
                ExpansionMethod
            )

            all_results.append(run_result)

        analyze_results(
            logger,
            base_output_dir,
            sentences,
            umls_name_map,
            all_results,
            umls_universes
        )

    print("Success.")


def analyze_results(logger,
                    base_output_dir,
                    sentences,
                    umls_name_map,
                    all_results,
                    umls_universes):
    """
    Analyze run results: create image files, save text files, etc...

    """

    for run_result in all_results:
        logger.write(f"Clusters for {run_result.execution_id}")

        # Write cluster text files;
        Cluster.visualize_clusters(
            logger,
            sentences,
            run_result.cluster_labels,
            umls_name_map
        )

        #
        Analysis.plot_cluster_mini_matrices(
            base_output_dir,
            run_result.expanded_scored_terms,
            run_result.cluster_labels,
            umls_name_map,
            run_result.execution_id
        )

        # Plot feature matrix;
        reordered_feature_matrix = Analysis.reorder_matrix(
            run_result.feature_matrix,
            run_result.cluster_labels
        )

        feature_names = [
            umls_name_map[term][2]
            for term in run_result.expanded_unique_terms
        ]

        Analysis.plot_feature_matrix(
            reordered_feature_matrix,
            f"Feature Matrix-{run_result.execution_id}",
            output_filepath=os.path.join(
                base_output_dir,
                f"clusters-{run_result.execution_id}.png",
            ),
            feature_ids=feature_names
        )

        # Plot distance matrix;
        distance_filepath = os.path.join(
            base_output_dir,
            f"distance-{run_result.execution_id}.png"
        )
        Analysis.plot_distance_matrices(
            run_result,
            distance_filepath
        )

        # Build graphs;
        graph_filepath = os.path.join(
            base_output_dir,
            f"graph-{run_result.execution_id}.png"
        )

        Networks.build_knowledge_graph(
            run_result,
            umls_universes,
            umls_name_map,
            graph_filepath
        )


def execute_single_run(logger,
                       UMLS,
                       sentences,
                       execution_id,
                       ExpansionMethod) -> Types.ClusteringResult:
    """
    Coordinate the evaluation execution for a single parameter set.

    """

    sentence_terms = Cluster.extract_sentence_terms(sentences)
    unique_terms = Cluster.extract_unique_terms(sentence_terms)

    K = len(unique_terms)
    logger.write(f"Found {K} unique UMLS terms before expansion.")

    expansion_relationships, expanded_scored_terms = execute_expansion(
        UMLS,
        sentences,
        unique_terms,
        ExpansionMethod,
    )

    expanded_unique_terms = [
        label
        for label, score in
        Cluster.extract_unique_terms(
            expanded_scored_terms)
    ]

    Ke = len(list(set(expanded_unique_terms)))
    logger.write(f"Found {Ke} unique UMLS terms after expansion.")

    m = " + ".join([m.name for m in ExpansionMethod])
    logger.write(f"Calculating clusters... expansion rules: {m}")

    assert expanded_unique_terms, f"No expanded terms detected! EM={ExpansionMethod}"

    feature_matrix = Cluster.build_matrix(
        expanded_unique_terms,
        expanded_scored_terms
    )

    # TODO: Feature reduction?
    # reduced_matrix = Cluster.agglomerate_features(feature_matrix)
    # print(reduced_matrix.shape)

    cluster_labels, cluster_method = Cluster.clusterize_matrix(feature_matrix)

    logger.write(cluster_labels)
    logger.write(f"Found {max(cluster_labels)} groups.")

    return Types.ClusteringResult(
        execution_id,
        feature_matrix,
        cluster_labels,
        expanded_unique_terms,
        expanded_scored_terms,
        expansion_relationships,
        cluster_method
    )


def execute_expansion(
        UMLS,
        sentences,
        unique_terms,
        ExpansionMethod):
    """
    Expand UMLS terms with ancestors and descendants.
    Algorithm step #2.

    """

    scored_terms = Cluster.extract_sentence_terms_score(sentences)
    # Expand terms:
    expansion_relationships: Dict[str, List[str]] = {
        term: UMLS.get_relationships(
            term,
            relationship_types=ExpansionMethod)
        for term in unique_terms
    }

    expanded_scored_terms =\
        Concepts.merge_umls_terms_with_expansion(
            scored_terms,
            expansion_relationships,
            keep_original=Types.ExpansionMethod.core in ExpansionMethod
        )

    return expansion_relationships, expanded_scored_terms


if __name__ == "__main__":
    main()
