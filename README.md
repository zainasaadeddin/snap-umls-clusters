# snap-umls-clusters
clusterize sentences based on UMLS terms and expanded UMLS terms present in them


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
