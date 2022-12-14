# snap-umls-clusters

[Project Google Site](https://sites.google.com/view/zeina-master-project2021/)

clusterize the [SNAP-IV ADHD questions](https://medicine.usask.ca/documents/psychiatry/snap-iv-form.pdf) based on Unified Medical Language System (UMLS) terms and expanded UMLS terms present in them. 


Thesis Supervisors:

* [Dr. Mohammad Maree ](https://scholar.google.com/citations?user=CoVmYzcAAAAJ&hl=en)
* [Dr. Mohammad Herzallah](https://scholar.google.com/citations?user=TPIc7J8AAAAJ&hl=en)
* [Dr. Joman Natsheh](https://scholar.google.com/citations?user=M6WwVyEAAAAJ&hl=en)


## Clustering

* Feature matrix
* Sillhouete determines the best number of clusters, after evaluating multiple values, where `2 <= N < 12`


## Visualization

* NetworkX graphs depicting CUI terms that usually appear on the same sentences. 
* Distance matrices: reordered to match clusters.
* Feature matrices: reordered to match clusters.

# Usage

## Setup

* Install requirements:
`pip install -r requirements.txt`

* Install scispacy model:

`pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_md-0.4.0.tar.gz`

* Download the UMLS Metathesaurus (login required). Place it on the base directory.

`https://download.nlm.nih.gov/umls/kss/2021AA/umls-2021AA-metathesaurus.zip`

## Execute

`python main.py SNAP_IV_Long_with_Scoring.pdf`

[![DOI](https://zenodo.org/badge/403273392.svg)](https://zenodo.org/badge/latestdoi/403273392)

