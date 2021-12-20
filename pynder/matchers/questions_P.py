# standard library
from typing import Tuple

# non-standard library
from spacy.language import Language
from spacy.lang.en import English
from spacy.lang.nl import Dutch

# custom code
from .base_class_matchers import (
    BaseRegex,
    BaseTFIDF,
    BaseSpacyMatcher,
    BaseNormalizedCounter,
)

__all__ = [
    "Question8",
    "Question13",
    "Question17",
    "Question20",
    "Question23",
    "Question27",
    "Question28",
    "Question31",
    "Question41",
    "Question42",
    "Question51",
]
__all_init_P_questions__ = [
    "q8",
    "q13",
    "q17",
    "q20",
    "q23",
    "q27",
    "q28",
    "q31",
    "q41",
    "q42",
    "q51",
]


@Dutch.factory("q8")
class Question8(BaseRegex):
    def __init__(self, nlp: Language, name: str):
        super().__init__(nlp, name, [r"tussen\ *(?s)(.*?dossiernummer\ *\d*)"])


@Dutch.factory("q13")
class Question13(BaseRegex):
    def __init__(self, nlp: Language, name: str):
        super().__init__(
            nlp,
            name,
            [
                r"wie is de hoofddienstverlener\?(.*?)land",
                r"dossiernummer\ *\d*\ *en(?s)(.*?dossiernummer\ *\d*)",
            ],
        )


@Dutch.factory("q17")
class Question17(BaseRegex):
    def __init__(self, nlp: Language, name: str):
        super().__init__(nlp, name, [r".{200}onbepaalde\s{1,10}tijd.{200}"])


@Dutch.factory("q20")
class Question20(BaseRegex):
    """ """

    def __init__(self, nlp: Language, name: str):
        super().__init__(nlp, name, [r".{40}exit.{1,5}plan.{40}"])


@Dutch.factory("q23")
class Question23(BaseRegex):
    """
    vrij basale regex, zoekn op opzegtermijn en 100 token voor en na. Maar omdat dit vaak lastig ligt wordt dit waarschijnlijk
    het stuk tekst geven waar het eventueel in staat. Heeft nog fine tuning nodig uiteindelijk. Waarschijnlijk andere
    synoniemen ook. Alleen op opzegtermijn kreeg ik 32% hits oid.
    """

    def __init__(self, nlp: Language, name: str):
        super().__init__(nlp, name, [r".{100}opzegtermijn.{100}"])


@Dutch.factory("q27")
class Question27(BaseSpacyMatcher):
    """
    Notes: Hey some random notes of Question 27:
    We found that A and B worked but C didn't! Mind blown!
    """

    def __init__(self, nlp: Language, name: str):
        list_patterns = [
            [{"LEMMA": "betaal"}, {"LEMMA": "termijn"}],
            [{"LEMMA": "betaal"}, {"LEMMA": "afspraken"}],
            [{"LOWER": "betaaltermijn"}],
            [{"LEMMA": "facturering"}],
        ]
        super().__init__(nlp, name, list_patterns)


@Dutch.factory("q28")
class Question28(BaseSpacyMatcher):
    """
    Notes: Hey some random notes of Question 27:
    We found that A and B worked but C didn't! Mind blown!
    """

    def __init__(self, nlp: Language, name: str):
        list_patterns = [
            [{"LEMMA": "factuur"}, {"LEMMA": "afspraken"}],
            [{"LEMMA": "factuur"}, {"LEMMA": "voorwaarden"}],
            [{"LOWER": "factureringsvoorwaarden"}],
            [{"LOWER": "facturering"}],
            [{"LOWER": "betaling"}],
        ]
        super().__init__(nlp, name, list_patterns)


@Dutch.factory("q31")
class Question31(BaseRegex):
    """
    voor wijzigingen in AIV en om versie van AIV eruit te krijgen.
    zoekt naar vormen van wijzig en aanvulling voor of na algemene inkoopvoorwaarde. Ook mag daar niet teveel tekens (100)
    tussen zitten. Andere regex zoekt specieke naar woord versie, dan een maand, en dan 4 cijferig getal wat het jaar is.
    """

    def __init__(self, nlp: Language, name: str):
        super().__init__(
            nlp,
            name,
            [
                r".(?:wijzig.{1,5}|aanvull.{1,5}).{1,100}algemene.{1,10}inkoopvoorwaarde |algemene.{1,10}inkoopvoorwaarde.{1,100}(?:wijzig.{1,5}|aanvull.{1,5})",
                r"(versie\s{1,5}\w{4,10}\s{1,5}\d{4}).{1,100}?(algemene.*?inkoopvoorwaarden)",
            ],
        )


@Dutch.factory("q41")
class Question41(BaseTFIDF):
    def __init__(self, nlp: Language, name: str):
        super().__init__(
            nlp, name, i_threshold=0.51, list_source_texts=["test1", "test2", "test3"]
        )


@Dutch.factory("q42")
class Question42(BaseNormalizedCounter):
    def __init__(self, nlp: Language, name: str):
        super().__init__(
            nlp, name, iThreshold=0.001, list_words_of_interest=["risk", "risico"]
        )


@Dutch.factory("q51")
class Question51(BaseRegex):
    """
    pattern voor de BIVC code, Bas heeft in mail gezet dat echt specifiek bivc formulier erbij moet staan. Dus kijken
    welke format die heeft wat uit deze regex komt, dat nog niet bekeken. Als er alsnog een code uit wordt gehaald
    maar niet op formulier dan is het geel.
    """

    def __init__(self, nlp: Language, name: str):
        super().__init__(nlp, name, [r".{50}bivc.{1,20}?\d.*?\d.*?\d.*?\d?.{50}"])
