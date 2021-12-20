# standard library

# non-standard library
from spacy.language import Language
from spacy.matcher import Matcher
import re

# custom code
from pynder.utils.similarity import Vectorizer
from pynder.utils.occurance import calc_normalized_count
from pynder.enums import ResultMatch
from pynder.decorators import add_error_handling_for_class_method


class BasePipelineComponent:
    """Main parent class of all subsequent BaseClasses.

    Allowing for a centralized __call__ function used as default in all other classes.
    """

    def __init__(self, bLoopOverSpans: bool = True):
        self.bLoopOverSpans = bLoopOverSpans

    @add_error_handling_for_class_method
    def __call__(self, doc):
        if self.bLoopOverSpans:

            # analyze_text returns a ResultMatch which we can sum due to __radd__.
            doc._._dict_results[self.name] = sum(
                [
                    self.analyze_doc(span, doc._.doc_id, i_page_number)
                    for i_page_number, span in enumerate(doc.spans["PAGES"])
                ]
            )

        else:
            doc._._dict_results[self.name] = self.analyze_doc(doc, None)
        return doc

    def analyze_doc(self, doc, doc_id, i_page_number=None):
        """Main analyze function which will be called on every span/doc and returning the ResultMatch object.

        Mind you: doc_id is a doc level attribute, not span hence we need to pass this explicitly.

        Args:
            doc: Spacy.Doc
            doc_id: Spacy.Doc.id
            i_page_number: int

        Returns: ResultMatch
        """
        raise NotImplementedError


class BaseRegex(BasePipelineComponent):
    """Base class for the regex matchers."""

    def __init__(
        self,
        nlp: Language,
        name: str,
        list_regex_patterns: list,
        bLoopOverSpans: bool = True,
        *args,
        **kwargs
    ):
        self.pattern = re.compile("|".join(list_regex_patterns))
        self.name = name  # used to store result
        self.bLoopOverSpans = bLoopOverSpans
        super().__init__(bLoopOverSpans)

    def analyze_doc(self, doc, doc_id, i_page_number=None):
        tuple_matches = tuple(self.pattern.findall(doc.text))
        return (
            ResultMatch(
                bResult=True,
                tMatches=(tuple_matches,),
                tPage_nr=(i_page_number,),
                tDocIds=(doc_id,),
            )
            if tuple_matches
            else ResultMatch(False)
        )


class BaseTFIDF(BasePipelineComponent):
    """Base class for the Term Frequency - Inverse document frequency matchers."""

    def __init__(
        self,
        nlp: Language,
        name: str,
        i_threshold,
        list_source_texts,
        bLoopOverSpans: bool = False,
    ):
        self.i_threshold = i_threshold
        self.list_source_texts = list_source_texts
        self.vectorizer = Vectorizer()
        self.name = name
        self.bLoopOverSpans = (
            bLoopOverSpans  # mmm maybe this should be a pipeline parameter?
        )
        super().__init__(bLoopOverSpans)

    def analyze_doc(self, doc, doc_id, i_page_number=None):
        similarity_score, best_match = self.vectorizer.get_similarity_score(
            list_source_texts=self.list_source_texts, target_text=doc.text
        )
        return (
            ResultMatch(
                bResult=True,
                tMatches=(best_match,),
                tPage_nr=(i_page_number,),
                tDocIds=(doc._.doc_id,),
            )
            if similarity_score > self.i_threshold
            else ResultMatch(False)
        )


class BaseSpacyMatcher(BasePipelineComponent):
    """Base class for the Spacy build in pattern matchers."""

    def __init__(
        self, nlp: Language, name: str, list_patterns: list, bLoopOverSpans: bool = True
    ):
        _matcher = Matcher(nlp.vocab)
        _matcher.add("key", list_patterns)
        self.matcher = _matcher
        self.name = name
        self.bLoopOverSpans = (
            bLoopOverSpans  # mmm maybe this should be a pipeline parameter?
        )
        super().__init__(bLoopOverSpans)

    def analyze_doc(self, doc, doc_id, i_page_number=None):
        matches = self.matcher(doc, as_spans=True)

        return (
            ResultMatch(
                bResult=True,
                tMatches=(matches,),
                tPage_nr=(i_page_number,),
                tDocIds=(doc_id,),
            )
            if matches
            else ResultMatch(False)
        )


class BaseNormalizedCounter(BasePipelineComponent):
    """Base class for the Spacy build in pattern matchers."""

    def __init__(
        self,
        nlp: Language,
        name: str,
        iThreshold,
        list_words_of_interest,
        bLoopOverSpans: bool = True,
    ):
        self.iThreshold = iThreshold
        self.list_words_of_interest = list_words_of_interest
        self.name = name
        self.bLoopOverSpans = (
            bLoopOverSpans  # mmm maybe this should be a pipeline parameter?
        )
        super().__init__(bLoopOverSpans)

    def analyze_doc(self, doc, doc_id, i_page_number=None):
        normalized_score_count = calc_normalized_count(
            doc.text, self.list_words_of_interest
        )

        return (
            ResultMatch(
                bResult=True,
                tMatches=([doc.text[:100]],),  # return only first 100 chars
                tPage_nr=(i_page_number,),
                tDocIds=(doc_id,),
            )
            if normalized_score_count > self.iThreshold
            else ResultMatch(False)
        )
