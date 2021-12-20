from spacy.language import Language
from pynder.utils.text_parsing.text_parsers import (
    load_bare_spans_from_file,
    set_spans_to_doc,
)
import os


@Language.factory("load_page_spans")
class LoadPageSpans:
    def __init__(self, nlp: Language, name: str, basepath: str):
        self.name = name  # used to store result
        self.basepath = basepath

    def __call__(self, doc):
        path = os.path.join(self.basepath, doc._.contract_id, doc._.doc_id + ".pickle")
        spans = load_bare_spans_from_file(path)
        doc = set_spans_to_doc(doc, spans, "PAGES")
        return doc
