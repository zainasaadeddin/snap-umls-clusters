from typing import Dict, List, Tuple
import itertools
import enum


class Sentence:
    """
    Holds information about a single sentence.

    """
    index: int
    text: str
    umls_entities: Dict[str, List[Tuple[str, float]]]

    def __init__(self, i, t, u={}):
        self.index = i
        self.text = t
        self.umls_entities = u

    def extract_all_related_umls_terms(self):
        return list(itertools.chain.from_iterable(self.umls_entities.values()))

    def show(self, logger):
        m = f"""{self.index}. {self.text}"""
        logger.write(m)
        for entity in self.umls_entities.keys():
            logger.write(f"Token <{entity}>:")
            for umls, score in self.umls_entities[entity]:
                logger.write(f"   {umls} - {score}")


class ClusteringResult:
    """
    Holds result information for a single clustering run.
    """
    def __init__(self, ID, FM, L, UT, EST, ER, CM):
        self.execution_id = ID
        self.feature_matrix = FM
        self.cluster_labels = L
        self.expanded_unique_terms = UT
        self.expanded_scored_terms = EST
        self.expansion_relationships = ER
        self.cluster_method = CM

    def __str__(self):
        return "\n".join(
            [
                self.execution_id,
                self.cluster_method
            ])


class CUIRecord:
    """
    Holds information on a CUI that is found in the base sentences.

    """
    def __init__(self, N, L, ancestors=[], descendants=[]):
        self.name: str = N
        self.label: str = L
        self.ancestors = ancestors
        self.descendants = descendants

    def FromJSON(self):
        pass

    def ToJSON(self):
        pass


class ExpansionMethod(enum.Enum):
    """
    Possible expansion methods.
    Core represents the CUIs found in the sentence tokens.

    """
    core = "core"
    ancestors = "ancestors"
    descendants = "descendants"
    root_ancestor = "root_ancestor"
