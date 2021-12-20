from collections import Counter


def calc_normalized_count(text, list_words_of_interest):
    """Function that returns the normalized count (on doc length) of a set of target words.

    Args:
        text: str
        list_words_of_interest: list

    Returns: float
    """
    dict_count = Counter(text.split())
    return sum([dict_count[w] for w in list_words_of_interest]) / len(text)
