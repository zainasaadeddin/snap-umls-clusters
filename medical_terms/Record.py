from typing import List, Dict
import os
import json

from . import Types


def write_csv(sentences: List[Types.Sentence]):
    pass


def write_clusters(clusters: Dict[str, List[Types.Sentence]]):
    pass


def load_list(filepath: str) -> List[str]:
    with open(filepath) as f:
        return [
            w.strip() for w in f.read().splitlines()
        ]


def manage_cached_cui_name_map(UMLS, cuis):
    """
    Load and write local json caches containing remote
    UMLS results.

    """
    cache_file = "cui-name-cache.json"
    missing = []

    if os.path.isfile(cache_file):
        data = json.load(open(cache_file))
        missing = [cui for cui in cuis if cui not in data.keys()]
        if not missing:
            return data
        data.update(UMLS.fetch_batch_information(missing))

    if not missing:
        data = UMLS.fetch_batch_information(cuis)

    json.dump(data, open(cache_file, 'w'), indent=2)

    return data

def manage_cached_sentences():
    cache_file = "sentence-cache.json"
