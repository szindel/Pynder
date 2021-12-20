import langdetect


def safe_langdetect(text):
    try:
        return langdetect.detect(text)
    except Exception as e:
        return ""


def clean_text(text):
    text = text.replace("{", "")
    text = text.replace(")", "")
    text = text.replace("(", "")
    text = text.replace("\n", " ")
    return text


def remove_stopwords(text, set_stopwords):
    return " ".join([word for word in text.split() if word not in set_stopwords])
