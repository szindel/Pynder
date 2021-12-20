import spacy
from pynder.matchers import __all_init_P_questions__
from pynder.custom_pipeline_components import CustomTokenizerWrapper

import unittest
import pytest
from spacy.tokens import Doc

Doc.set_extension("_dict_results", default={}, force=True)
Doc.set_extension("doc_id", default="", force=True)
Doc.set_extension("contract_id", default="", force=True)


class TestsPipelineInit(unittest.TestCase):
    def test_init_custom_components(self):

        nlp = spacy.blank("nl")

        for question in __all_init_P_questions__:
            print(f"Info - adding step: {question} to the pipeline")
            nlp.add_pipe(question)

        docs = list(
            nlp.pipe(
                ["test", "random text", "tussen etc etc dossiernummer"],
                n_process=1,  # oke MASIVE overhead.. only run this when texts -> inf
            )
        )
        assert docs

    def init_custom_tokenizer(self):
        nlp = spacy.blank("nl")
        nlp.tokenizer = CustomTokenizerWrapper(nlp.tokenizer)
        assert nlp
