from spacy.tokens import Span
import fitz
import langdetect
import spacy
import pickle
import textract
from textract.exceptions import ExtensionNotSupported
import regex as re
import os

models = {"nld": "nl_core_news_lg", "eng": "en_core_web_lg"}

PAGE_LABEL = "PAGES"
BLOCK_LABEL = "BLOCKS"


def extract_doc(filepath):
    """
    Extract text from a doc or docx file in the filepath. Returns the text, spans of start and end token per page
    and the detected language.

    Spans are based on splitting text on 5 newlines (consistent with shift+enter to newpage in docx).

    Parameters
    ----------
    filepath: str
        Path to file

    Returns
    -------
    text, spans, lang
    """

    text = textract.process(filepath).decode()
    if text.strip() == "":
        return "", [], "unknown"

    lang = getlang(text)

    pages = [p for p in re.split(r"[\t\n]{4,5}", text) if p != ""]
    doc = list_texts_to_nlp(spacy.load(models.get(lang, "nl_code_news_lg")), pages)

    return doc.text, get_spans_from_doc(doc, PAGE_LABEL), lang, False


def extract_pdf(filepath):
    """
    Extract text from a PDF document in the filepath. Returns the text, spans of start and end token per page
    and the detected language.

    Parameters
    ----------
    filepath: str
        Path to file

    Returns
    -------
    text, spans, lang
    """

    document = fitz.open(filepath)
    page = document[0] if document.page_count == 1 else document[1]
    text = page.get_text().strip()
    if text == "":
        text = page.get_textpage_ocr(language="nld", dpi=120, full=True).extractText()
    lang = getlang(text)

    doc, scan = fitz_to_nlp(
        spacy.load(models.get(lang, "nl_core_news_lg")), document, lang
    )

    return doc.text, get_spans_from_doc(doc, PAGE_LABEL), lang, scan


def list_texts_to_nlp(model, texts):
    """
    Transform a list of texts to a spacy Doc with a set of spans per text in list.

    Parameters
    ----------
    model: spacy.Model
        Spacy NLP model .e.g 'nl_core_news_lg'
    texts: list
        List of input texts. Text of Doc will be concatenated string of these texts

    Returns
    -------
    Doc, spacy.Doc

    """
    page_spans = []
    idx = 0
    text = ""
    for page in texts:
        text += page
        end = len(text)
        page_spans.append({"start": idx, "end": end, "label": PAGE_LABEL})
        idx = end
    doc = model(text)
    new_spans = [new_span_by_char_idx(doc, x, PAGE_LABEL) for x in page_spans]

    doc.spans[PAGE_LABEL] = new_spans
    return doc


def getlang(text, default="nld"):
    """Helper function to get language of text, returns default if language
    not in 'nl' or 'eng'"""
    lang = langdetect.detect(text)

    if lang == "en":
        return "eng"
    elif lang in ["nl", "af"]:
        return "nld"
    else:
        return default


def fitz_to_nlp(model, fitz_doc, lang="nld"):
    """
    Fitz (PyMuPDF) doc to a spacy doc including a set of spans per page.

    Parameters
    ----------
    model: spacy.Model
        Spacy nlp model
    fitz_doc: fitz.Document
        PyMuPDF document
    lang: str
        Language to use for optional OCR parsing.

    Returns
    -------

    """
    page_spans, block_spans, text, scan = pages_to_spans(fitz_doc, lang=lang)
    doc = model(text)
    page_spans = [new_span_by_char_idx(doc, x, PAGE_LABEL) for x in page_spans]
    # block_spans = [new_span_by_char_idx(doc, x, BLOCK_LABEL) for x in block_spans]
    doc.spans[PAGE_LABEL] = page_spans
    # doc.spans[BLOCK_LABEL] = block_spans
    return doc, scan


def pages_to_spans(fitz_doc, lang):
    """
    Helper function to convert a fitz document to a list of spans per page
    and the final text.

    Parameters
    ----------
    fitz_doc: fitz.Document
        PyMuPDF document
    lang: str
        Language of the document

    Returns
    -------
    tuple
        page_spans (list), block_spans (list), text (str), scan(bool)
    """
    page_spans = []
    block_spans = []
    text = ""
    idx = 0
    scan = False
    for page in fitz_doc.pages():
        page_start = idx
        blocks = [b for b in page.get_text_blocks() if b[-1] == 0]
        if not blocks or (scan and (len(blocks) < 3)):
            page = page.get_textpage_ocr(language=lang, dpi=120, full=True)
            blocks = page.extractBLOCKS()
            if blocks:
                scan = True
        for block in blocks:
            if block[-1] == 0:
                start = idx
                end = idx + len(block[4])
                block_spans.append(
                    dict(start=start, end=end, text=block[4], label=BLOCK_LABEL)
                )
                idx = end
                text += block[4]

        if page_start != end:
            page_spans.append(
                dict(
                    start=page_start,
                    end=end,
                    text=text[page_start:end],
                    label=PAGE_LABEL,
                )
            )
    return page_spans, block_spans, text, scan


def new_span_by_char_idx(doc, x, label):
    """Helper function to transform spans with character indices to spacy.Span objects with token indices."""
    sp = doc.char_span(x["start"], x["end"], alignment_mode="contract")
    if sp is None:
        sp = doc.char_span(x["start"], x["end"], alignment_mode="expand")
    if sp is None:
        raise IndexError("No spans found")
    return Span(doc, sp.start, sp.end, label=label)


def load_bare_spans_from_file(path):
    """Helper function to load spans from file (pickle)"""
    with open(path, "rb") as file:
        spans = pickle.load(file)

    return spans


def save_bare_spans_from_file(obj, path):
    """Helper function to saves spans to file (pickle)"""
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def set_spans_to_doc(doc, bare_spans, label):
    """Helper function to add spans in list(dict) form to spacy.Doc"""
    new_spans = [Span(doc, x["start"], x["end"], label=x["label"]) for x in bare_spans]
    doc.spans[label] = new_spans
    return doc


def get_spans_from_doc(doc, label):
    """Helper function to convert form spacy.Doc.spans to spans in list(dict) form"""
    spans = doc.spans[label]
    bare_spans = [dict(start=s.start, end=s.end, label=s.label_) for s in spans]
    return bare_spans


def extract_file(path, uuid=None, contract_id=None, output_basepath=None):
    """
    Extract a file from document in path.
    If all uuid, contract_id and output_basepath are filled in the files will be saved. Otherwise text and spans
    are also returned.

    Saves extracted text to path build up from output_basepath, contract_id, 'text', and uuid.
    Saves extracted spans to path build up from output_basepath, contract_id, 'spans', and uuid (as pickle).

    Returns the detected language, error and extension of the file and whether or not the file was OCR'd.

    Parameters
    ----------
    path: str
        Path to file
    uuid: str
    contract_id: str
    output_basepath: str

    Returns
    -------
    text: str (optional)
        Text of the file. Only returned if any of uuid. contract_id or output_basepath == None.
    spans: list (optional)
         Spans of pages of file. Only returned if any of uuid. contract_id or output_basepath == None.
    lang: str
        Language detected, '' if none found
    error: str
        Error message if file was not able to extract, '' if no error
    ext: str
        Extension of the file (without '.')
    scan: int
        -1 for unknown (in case of error), 0 for False, 1 for True
    """
    error = ""
    scan = -1
    ext = path.split(".")[-1]
    if ext.lower() == ".ds_store":
        return None

    try:
        if ext.lower() == "pdf":
            text, spans, lang, scan = extract_pdf(filepath=path)
        elif ext.lower() in ["doc", "docx"]:
            text, spans, lang, scan = extract_doc(filepath=path)
        else:
            try:
                text, spans, lang, scan = extract_doc(filepath=path)
            except ExtensionNotSupported:
                text = ""
                spans = []
                lang = "unknown"
                error = f"Extension {ext} not supported"

        if text.strip() == "":
            raise NotImplementedError("Empty text extracted")
    except Exception as e:
        text = ""
        spans = []
        lang = "unknown"
        error = str(e)

    if text == "":
        return lang, error, ext, -1

    if not any([x is None for x in [uuid, contract_id, output_basepath]]):
        if not os.path.isdir(os.path.join(output_basepath, "text", contract_id)):
            os.mkdir(os.path.join(output_basepath, "text", contract_id))
        if not os.path.isdir(os.path.join(output_basepath, "span", contract_id)):
            os.mkdir(os.path.join(output_basepath, "span", contract_id))

        if text != "":
            with open(
                os.path.join(output_basepath, "text", contract_id, uuid + ".txt"), "w"
            ) as file:
                file.write(text)

            with open(
                os.path.join(output_basepath, "span", contract_id, uuid + ".pickle"),
                "wb",
            ) as file:
                pickle.dump(spans, file)

        return lang, error, ext, int(scan)
    else:
        return text, spans, error, ext, int(scan)
