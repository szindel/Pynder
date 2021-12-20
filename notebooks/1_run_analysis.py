# -*- coding: utf-8 -*-
# +
from typing import Tuple
from collections.abc import Iterable

import spacy
from pynder.utils.occurance import calc_normalized_count
from pynder.utils.similarity import Vectorizer
from dataclasses import dataclass

from pynder.matchers import __all_init_P_questions__
from pynder.custom_pipeline_components import LoadPageSpans, CustomTokenizerWrapper
from pynder.enums import ResultMatch

try:
    nlp = spacy.load("nl_core_news_lg")
except OSError:
    # !python -m spacy download nl_core_news_lg
    nlp = spacy.load("nl_core_news_lg")

import os
import pandas as pd

# %reload_ext autoreload
# %autoreload 2

# +
# custom spacy components
project_path = "/Users/szindel/Projects/pynder/data/"
contract_id = 27848
folder_contract = os.path.join(project_path, "text", str(contract_id))
folder_span = os.path.join(project_path, "span")
path_df_sql = os.path.join(project_path, "df_sql.csv")
assert os.path.isdir(folder_contract)

df_meta = pd.read_csv(path_df_sql, sep=";")
paths = [
    os.path.join(folder_contract, p + ".txt")
    for p in df_meta.loc[
        (df_meta.loc[:, "contract_id"] == 27848)
        & (df_meta.loc[:, "language"] == "nld"),
        "file_uuid",
    ]
]

# +
from spacy.tokens import Doc

# IMPORTANT! perhaps we want to add this to BasePipeline class?
# this adds the _dict_result to the doc.. you do not want to do this at runtime..
Doc.set_extension("_dict_results", default={}, force=True)
Doc.set_extension("doc_id", default="", force=True)
Doc.set_extension("contract_id", default="", force=True)

# Add the component to the pipeline and configure it
# nlp = spacy.blank("nl")

nlp.tokenizer = CustomTokenizerWrapper(nlp.tokenizer)

nlp.add_pipe("load_page_spans", first=True, config={"basepath": folder_span})

for question in __all_init_P_questions__:
    print(f"Info - adding step: {question} to the pipeline")
    nlp.add_pipe(question)
# -

docs = list(
    nlp.pipe(
        paths[:3], n_process=1  # oke MASIVE overhead.. only run this when texts -> inf
    )
)

for doc in docs:
    print(doc._._dict_results)
    print("\n")
