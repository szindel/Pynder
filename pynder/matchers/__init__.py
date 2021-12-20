from .questions_P import *  # this actually initializes the matchers
from .questions_P import __all_init_P_questions__


map_questions_to_matcher_class = {"q8": Question8, "q27": Question27, "q41": Question41}


def get_matcher_class(str_question):
    return map_questions_to_matcher_class[str_question]
