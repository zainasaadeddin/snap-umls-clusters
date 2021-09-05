from typing import List
import os
import sys
from owlready2 import default_world
from owlready2.pymedtermino2.umls import get_ontology, import_umls

from . import Types


class UMLS():
    """

    Handles UMLS queries by running a local UMLS Thesaurus.

    """
    def __init__(self, BASE_PATH):
        thesaurus_path = os.path.join(BASE_PATH, "umls-2021AA-metathesaurus.zip")
        database_path = os.path.join(BASE_PATH, "umls.sqlite3")

        DB_EXISTS = os.path.isfile(database_path)

        default_world.set_backend(filename=database_path)

        if not DB_EXISTS:
            import_umls(
                thesaurus_path,
                #remove_suppressed="",
                terminologies=[
                    #"ICD10",
                    "SNOMEDCT_US",
                    "CUI"
                ])
            default_world.save()

        PYM = get_ontology("http://PYM/").load()
        self.CUI = PYM["CUI"]
        self.SNOMEDCT_US = PYM["SNOMEDCT_US"]

    def get_relationships(
            self,
            term,
            relationship_types: List[Types.ExpansionMethod]
    ):
        """
        Owlready2 only allows descendant and ancestor concepts
        to be retrived for SNOMEDCT_US nomenclatures, not for CUI.
        So we convert CUI to SNOMEDT_US, then retrieve relationships,
        then convert back to CUI.
        """
        concept = self.CUI[term]
        if concept is None:
            return []

        try:
            concept = (concept >> self.SNOMEDCT_US).pop()
        except KeyError:
            return []

        concepts = []
        if Types.ExpansionMethod.descendants in relationship_types:
            concepts += concept.descendant_concepts(include_self=False)

        ANC = set([Types.ExpansionMethod.ancestors, Types.ExpansionMethod.root_ancestor])
        if set(relationship_types).intersection(ANC):
            concepts += concept.ancestor_concepts(include_self=False)

        # FIXME: Is this correct? MOVE THIS ELSEWHERE
        if "root_ancestor" in relationship_types:
            print(concepts)
            # SKIP 'SNOMED CT Concept'
            if concepts[-1].name == "138875005":
                concepts.pop(-1)
            concepts = concepts[-1:]

        return [
            (c >> self.CUI).pop().name
            for c in concepts
        ]

    def get_label(self, term) -> str:
        concept = self.CUI[term]
        if concept is None:
            print(term)
            return "NO_LABEL"

        return concept.label[0]


if __name__ == "__main__":
    U = UMLS(sys.argv[1])
    relationships = U.get_relationships("C0085580", [Types.ExpansionMethod.ancestors])
    print(relationships)
    w = relationships[0]
