from typing import List, Tuple, Dict
import itertools

from . import Types


def merge_umls_terms_with_expansion(sentence_scored_terms,
                                    ExpandedTerms,
                                    keep_original=True) -> Dict[int, List[Tuple[str, float]]]:
    return {
        index: apply_expanded_terms(
            terms,
            ExpandedTerms,
            keep_original
        )
        for index, terms in sentence_scored_terms.items()
    }


def apply_expanded_terms(
        original_terms: List[Tuple[str, float]],
        ExpandedTerms,
        keep_original=True
):
    """

    For a given list of UMLS terms, append
    the expanded terms that belong to the list.
    This is done by checking the expanded terms that belong
    to each term as described in the ExpandedTerms dictionary.

    """

    expansion = []
    for term, score in original_terms:
        expansion += [
            (expanded_term, score)
            for expanded_term in ExpandedTerms[term]
        ]

    if keep_original:
        expansion = original_terms + expansion

    return list(set(expansion))


def get_all_subgroup(cui_database: Dict[str, Types.CUIRecord],
                     group_name: Types.ExpansionMethod):

    group = [
        getattr(cui, group_name.name)
        for cui in cui_database.values()
    ]

    w = itertools.chain.from_iterable(group)

    return set(w)


def extract_names(scored_terms: List[Tuple[str, float]]) -> List[str]:
    return [x[0] for x in scored_terms]
