from typing import List, Tuple, Dict
import re
import spacy

from scispacy.linking import EntityLinker as UmlsEntityLinker

from . import Types

sentence_cache = Dict[str, List[Tuple[str, float]]]


def initialize_model():
    """

    This model detects UMLS entries in each entity of the input text.
    CUI and SCORE only.

    """
    nlp = spacy.load("en_core_sci_md")

    nlp.add_pipe(
        "scispacy_linker",
        config={
            "resolve_abbreviations": True,
            "linker_name": "umls"
        })

    return nlp


def locate_umls_entities(model: spacy.language.Language,
                         sentence: str) -> List[Tuple[str, float]]:
    pass


def process_sentence(model: spacy.language.Language,
                     sentence: Types.Sentence) -> sentence_cache:
    doc = model(sentence.text)
    found_entities: sentence_cache = {}
    for entity in doc.ents:
        umls = entity._.umls_ents
        if umls:
            entity_text = str(entity)
            if entity_text not in found_entities.keys():
                found_entities[entity_text] = []
            found_entities[entity_text] += umls

    return found_entities


def filter_term_scores(sentences: List[Types.Sentence]):
    """
    Keep only the CUI matches that have a score of 1.0.
    If no matches have 1.0, keep the best.

    (Inplace)
    """
    for sentence in sentences:
        for token, umls_terms in sentence.umls_entities.items():
            if not umls_terms:
                continue
            best_score = max([score for term, score in umls_terms])
            sentence.umls_entities[token] = [
                (name, score)
                for (name, score) in umls_terms
                if score >= best_score
            ]


# DEPRECATED?
def umls_to_token_mapping(sentences: List[Types.Sentence],
                          expansion_relationships: Dict[str, str]) -> Dict[str, str]:
    """
    Maps all umls terms to their original sentence tokens.

    """
    mapping: Dict[str, str] = {}

    for sentence in sentences:
        for token, umls_terms in sentence.umls_entities.items():
            for umls_term, _ in umls_terms:
                try:
                    original = mapping[umls_term]
                    if original != token:
                        print(f"UMLS term {umls_term}\n\t"
                              f"maps to different tokens: {original} & {token}.")
                except KeyError:
                    pass
                mapping[umls_term] = token

    for umls_term, expanded in expansion_relationships.items():
        for k in expanded:
            mapping[k] = mapping[umls_term]

    return mapping


def compile_umls_name_mapping(map_a: Dict[str, str],
                              map_b: Dict[str, str]) -> Dict[str, str]:
    """
    Compose an UMLS entity to name from multiple mappings.
    Try to use the definition on the first map,
    then fallback to to the second if not found.

    """

    bad_ids = [None, "NO_LABEL"]
    final_map: Dict[str, str] = {}
    for name in map_a:
        try:
            final_map[name] = map_a[name]
            continue
        except KeyError:
            final_map[name] = map_b[name]
            continue

        definition = map_b[name] if map_a[name] in bad_ids else map_a[name]
        final_map[name] = definition

    return final_map
