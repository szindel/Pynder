import os


class CustomTokenizerWrapper:
    """Class that wraps a default spacy tokenizer with our own mods.

    Essentially this class enables us to start creating a spacy pipeline from paths instead of text files and
    uses the path to set doc_id and contract id attributes. (set these in the main code!)

    example usage:

    import spacy
    from spacy.tokens import Doc
    this adds the _dict_result to the doc: you want to do this very securely (not automatic/looped)
    Doc.set_extension("_dict_results", default={}, force=True)
    Doc.set_extension("doc_id", default='', force=True)
    Doc.set_extension("contract_id", default='', force=True)

    nlp = spacy.load("nl_core_news_lg")
    nlp.tokenizer = CustomTokenizer(nlp.tokenizer)
    """

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, _path):
        with open(_path, "r") as f:
            text = f.read()
        doc = self.tokenizer(text)
        doc._.contract_id, doc._.doc_id = os.path.splitext(_path)[0].split("/")[-2:]
        return doc
