import traceback


def add_error_handling_for_class_method(func):
    """Decorator providing error handeling for the __Call__ class method in every custom pipeline run.

    Args:
        func: __call__ method

    Returns: spacy.Doc

    """

    def wrapper(self, doc, *args, **kwargs):
        try:
            return func(self, doc, *args, **kwargs)
        except Exception:
            print(f"Error occured in: {self}, {doc._.contract_id}, {doc._.doc_id}")
            traceback.print_exc
            return doc

    return wrapper
