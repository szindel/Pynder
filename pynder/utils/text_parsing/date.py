import numpy as np
from num2words import num2words as n2w
import re
import unidecode
import string
from datetime import datetime as dt
import nltk
import regex
from spacy.tokens import Span
import locale
from .utils import overwrite_spans


def get_date_entities(doc, date, label, lang="nl"):
    if lang == "nl":
        locale.setlocale(locale.LC_ALL, "nl_NL")

        date_variations = [
            dt.strftime(date, "%d-%m-%Y"),
            dt.strftime(date, "%d/%m/%Y"),
            dt.strftime(date, "%d %B %Y"),
            dt.strftime(date, "%-d %B %Y"),
            dt.strftime(date, "%-d %-m %Y"),
            dt.strftime(date, "%-d %-m %y"),
            dt.strftime(date, "%-d %-m '%y"),
            dt.strftime(date, "%d-%b-%Y"),
        ]
    else:
        date_variations = [
            dt.strftime(date, "%m-%d-%Y"),
            dt.strftime(date, "%m/%d/%Y"),
            dt.strftime(date, "%B %d %Y"),
            dt.strftime(date, "%B %-d %Y"),
            dt.strftime(date, "%-m %-d %Y"),
            dt.strftime(date, "%-m %-d %y"),
            dt.strftime(date, "%-m %-d '%y"),
            dt.strftime(date, "%d-%b-%Y"),
        ]

    new_ents = []

    for date_type in date_variations:
        pattern = f"{date_type}".lower()
        for match in re.finditer(pattern, doc.text.lower()):
            start, end = match.span()
            span = doc.char_span(start, end)
            if span is not None:
                new_ent = Span(doc, span.start, span.end, label=label)
                new_ents.append(new_ent)

    original_ents = list(doc.ents)
    new_ents.extend(original_ents)

    doc.ents = overwrite_spans(new_ents)
    return doc


def _build_ocr_err_dict():
    """
    Create dictionary to fix known OCR errors.
    :return: Dictionary
    """

    err_dict = {
        "negcnticnhondcrdeencnnegentig": "negentienhonderdeenennegentig",
        "neoentienhondorritachtio": "negentienhonderdtachtig",
        "negcnticnhondcrd": "negentienhonderd",
        "neaenenzestia": "negenenzestig",
        "twaaduizand": "tweeduizend",
        "twintia": "twintig",
        "tachtia": "tachtig",
        "neoentien": "negentien",
        "negcnticn": "negentien",
        "neaentien": "negentien",
        "hegentien": "negentien",
        "zevenig": "zeventig",
        "zestio": "zestig",
        "zestia": "zestig",
        "viiftia": "vijftig",
        "zesentwin-": "zesentwintig",
        "hondcrd": "honderd",
        "bèta len": "betalen",
        "beta len": "betalen",
    }
    return err_dict


def build_translation_dict(language="nl"):
    """
    Makes dictionaries to translate dutch dates written out in text to numerical values

    :return: tuple
    """
    num_dict = {
        "".join(unidecode.unidecode(n2w(n, lang=language, to="year")).split(" ")): n
        for n in range(1900, 2500)
    }
    for n in range(1, 1001):
        num_dict[unidecode.unidecode(n2w(n, lang=language))] = n
    if language == "nl":
        m_dict = dict(
            januari=1,
            februari=2,
            maart=3,
            april=4,
            mei=5,
            juni=6,
            juli=7,
            juii=7,
            augustus=8,
            september=9,
            oktober=10,
            november=11,
            december=12,
        )
    elif language == "en":
        m_dict = dict(
            january=1,
            february=2,
            march=3,
            april=4,
            may=5,
            june=6,
            july=7,
            juiy=7,
            augustus=8,
            september=9,
            october=10,
            november=11,
            december=12,
        )

    return m_dict, num_dict


def date_from_string(
    in_string,
    m_dict=None,
    num_dict=None,
    with_extra=False,
    verbose=False,
    language="nl",
):
    """
    :param in_string: the numbers written in words
    :param m_dict: dictionary of months
    :param num_dict: number dictionary
    :param bool with_extra: if True the parser can handle extra words around the date
        e.g.: vandaag is twee januari tweeduizendenacht de datum
        it will ignore the words around it.
        NB: It cannot handle words WITHIN the date:
        e.g.: deze zin twee januari van het jaar tweeduizendvier gaat kapot
    :param bool verbose: print statements
    :return: output date in %d/%m/%Y  format
    """

    if m_dict is None:
        m_translator, translator = build_translation_dict(language)
    else:
        m_translator, translator = m_dict, num_dict

    in_string = in_string.translate(str.maketrans("", "", string.punctuation))

    # split string into three parts
    words = in_string.split()
    months = [m for m in words if m in m_translator.keys()]

    if len(months) > 1:
        if verbose:
            print("**** More than one month found **** CHECK")
            print(unidecode.unidecode(in_string))
    if not months:
        if verbose:
            print("*** No months found *** CHECK")
            print(unidecode.unidecode(in_string))
        raise KeyError

    to_translate = in_string.split(months[0])
    m = re.search("om.*uur", to_translate[1])
    if m is not None:
        trim = m.start()
        to_translate = [to_translate[0], to_translate[1][:trim]]

    to_translate = [s.strip() for s in to_translate]
    to_translate = [s.replace("-", "").replace("—", "") for s in to_translate]
    # print(to_translate)

    # transl = translate.Translator(to_lang='en', from_lang='nl')
    # print (list(translator.keys())[40:50])
    if with_extra:
        # adding 'en' just so we can have it in the dict
        translator["en"] = "-"
        w_num1 = [unidecode.unidecode(x) for x in to_translate[0].split(" ")]
        w_numind = np.where(
            [True if n in translator.keys() else False for n in w_num1]
        )[0]
        # cut_at = np.max(np.argwhere(w_numind))
        # remove everything that is not a number word or 'en'
        w_num1 = np.array(w_num1)[w_numind].tolist()
        w_num1 = ["".join([s for s in word if s.isalpha()]) for word in w_num1]
        w_num1 = "".join([n for n in w_num1])
        num1 = translator[w_num1]

        w_num2 = [unidecode.unidecode(x) for x in to_translate[1].split(" ")]
        w_numind = np.where(
            [True if n in translator.keys() else False for n in w_num2]
        )[0]
        # cut_at = np.max(np.argwhere(w_numind)) + 1
        w_num2 = np.array(w_num2)[w_numind].tolist()
        w_num2 = ["".join([s for s in word if s.isalpha()]) for word in w_num2]
        w_num2 = "".join([n for n in w_num2])
        try:
            num2 = translator[str(w_num2)]
        except KeyError:
            print(w_num2)
            num2 = translator[str(re.sub("(?<=d)en", "", w_num2))]
    else:
        w_num1 = unidecode.unidecode(to_translate[0].replace(" ", ""))
        w_num1 = "".join([s for s in w_num1 if s.isalpha()])
        num1 = translator[w_num1]
        w_num2 = unidecode.unidecode(to_translate[1].replace(" ", ""))
        w_num2 = "".join([s for s in w_num2 if s.isalpha()])
        # translate year. If fails we try to remove 'en'
        try:
            num2 = translator[str(w_num2)]
        except KeyError:
            num2 = translator[str(re.sub("(?<=d)en", "", w_num2))]

    try:
        output = dt.strptime(f"{num1}/{m_translator[months[0]]}/{num2}", "%d/%m/%Y")
    except ValueError:
        # Failed to parse number, save not as datetime
        output = f"{num1}/{m_translator[months[0]]}/{num2}"

    return output


def find_written_date(txt, as_text=False, backuptext="", verbose=False):
    """
    Function to find dates that are written out in words (in dutch) such as
    'negen januari tweeduizend en zes'.

    :param str txt: Input text to find the date in
    :param bool as_text: if True, the text will not be parsed to a datetime.date. Default value is False
    :param str backuptext: Backup input text to search
    :param str verbose: Print statements or not
    :return: list of datetime.datetime or strings
    """
    # initialize list of dates
    dates = []

    # get translations dicts for days, years and months
    m_dict, n_dict = build_translation_dict()
    months = [k for k in m_dict.keys()]
    days = [k for k, v in n_dict.items() if v < 32]
    years = [k for k, v in n_dict.items()]

    nlstopwords = nltk.corpus.stopwords.words("dutch")
    # and 'en' for dates like tweeduizend en zeven
    years.append("en")

    # regex pattern inclyding list of optional months and days
    pattern = r"(\L<days>)[\W*\s]*(\L<months>{i<=1})[\W\s]*(\L<years>{i<=1}\s*)*"

    # text cleaning
    txt = str(txt).lower()
    txt = unidecode.unidecode(txt)
    if verbose:
        print(txt)
    words = txt.split(" ")
    if verbose:
        print(words)
    words = ["".join([w for w in word if w.isalpha()]) for word in words]
    if verbose:
        print(words)
    words = [w for w in words if len(w) > 1 and w]
    if verbose:
        print(words)
    words = [
        w
        for w in words
        if (len(w) > 3 or w in nlstopwords or w in n_dict.keys() or w in m_dict.keys())
    ]
    if verbose:
        print("Longer than 3, or number or month or stopword")
        print(words)
    txt = " ".join(words)

    for number in days[:9]:
        txt = re.sub(rf"{number}[\s\W]*en[\s\W]t", f"{number}ent", txt)

    # get common OCR mistakes and correct for them
    ocr_replacements = _build_ocr_err_dict()
    for k, v in ocr_replacements.items():
        txt = re.sub(k, v, txt)

    # use regex to find dates
    for m in regex.finditer(pattern, txt, days=days, months=months, years=years):
        if verbose:
            print(m.group())
        day = txt[m.start(1) : m.end(1)].strip()
        month = txt[m.start(2) : m.end(2)].strip().replace(" ", "")
        oyear = txt[m.end(2) : m.end()].strip()
        year = re.sub(" en$", "", re.sub(" ten$", "", oyear)).replace(" ", "")

        # if not as_text we parse dates to number and to datetime.date
        if not as_text:
            try:
                day = n_dict[day]
            except KeyError:
                pass
            try:
                month = m_dict[month]
            except KeyError:
                pass
            try:
                year = n_dict[year]
            except KeyError:
                # years are tricky, so we correct for some common mistakes
                # negentienhonderdenzeven should be negentienhonderzeven, so correct for it
                try:
                    ind = year.find("den")

                    if ind > 0:
                        year = year[: ind + 1] + year[ind + 3 :]
                    year = n_dict[year]
                except (KeyError, IndexError):
                    try:
                        # sometimes there is a t at te end, so try without last letter
                        year = n_dict[year[:-1]]
                    except KeyError:
                        if backuptext:
                            backup_dates = find_written_date(backuptext, as_text=True)
                            if backup_dates and month < 10:
                                backup_years = [
                                    int(n_dict[d[0]["year"]]) for d in backup_dates
                                ]
                                year = min(backup_years)
                        else:
                            pass
                    pass
                pass
            try:
                date = dt(year=year, month=month, day=day)
                dates.append(date)
            except TypeError:
                # if all fails, we return the date as a string
                as_text = True
        if as_text:
            dates.append([{"day": day, "month": month, "year": year}])
    return dates
