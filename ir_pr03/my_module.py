"""
Helper module for IR processing logic: downloading collections, tokenizing, stopword removal, and search.
"""

import re
import math
import urllib.request
from typing import List

from document import Document


def download_text(url: str) -> str:
    """Download text from the given URL and return it as a string"""
    with urllib.request.urlopen(url) as response:
        raw = response.read()
    return raw.decode("utf-8")


def slice_text_lines(text: str, start: int, end: int) -> str:
    """Extract lines from start to end (exclusive) and return as a single string"""
    lines = text.splitlines()
    selected = lines[start:end]
    return "\n".join(selected)


## Not gonna use it. Will be handled by regex.
def split_stories(text: str, separator: str) -> list[str]:
    """Split the full text into individual story chunks using a separator string"""
    # TODO: split text based on separator
    raise NotImplementedError("split_stories is not yet implemented")


## Not gonna use it. Will be handled by regex.
def extract_title_and_body(story: str, pattern: re.Pattern) -> tuple[str, str]:
    """Use regex pattern to extract (title, body) from a story chunk"""
    # TODO: apply pattern to story and return groups
    raise NotImplementedError("extract_title_and_body is not yet implemented")


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase terms, splitting on non-word characters"""
    tokens = re.findall(r"\w+", text.lower())
    return tokens


def remove_stop_words(terms: list[str], stopwords: set[str]) -> list[str]:
    """Remove stopwords from a list of terms (case-insensitive)"""
    sw = {w.lower() for w in stopwords}
    filtered = []
    for t in terms:
        t_l = t.lower()
        if t_l not in sw:
            filtered.append(t_l)
    return filtered


def remove_stop_words_by_frequency(
    terms: list[str], collection: list[Document], low_freq: float, high_freq: float
) -> list[str]:
    """Remove terms whose document frequency is <= low_freq or >= high_freq"""
    # compute document frequencies
    df: dict[str, int] = {}
    total = len(collection)
    for doc in collection:
        uniq = {t.lower() for t in doc.terms}
        for t in uniq:
            df[t] = df.get(t, 0) + 1
    filtered = []
    for t in terms:
        t_l = t.lower()
        freq = df.get(t_l, 0) / total if total > 0 else 0
        if low_freq < freq < high_freq:
            filtered.append(t_l)
    return filtered


##############################
# Stemming (Porter algorithm) #
##############################

def _cons(word: str, i: int) -> bool:
    ch = word[i]
    if ch in "aeiou":
        return False
    if ch == "y":
        if i == 0:
            return True
        return not _cons(word, i - 1)
    return True


def _measure(word: str) -> int:
    m = 0
    i = 0
    length = len(word)
    while True:
        while i < length and _cons(word, i):
            i += 1
        if i >= length:
            return m
        i += 1
        while i < length and not _cons(word, i):
            i += 1
        m += 1
        if i >= length:
            return m


def _contains_vowel(word: str) -> bool:
    return any(not _cons(word, i) for i in range(len(word)))


def _double_consonant(word: str) -> bool:
    return len(word) >= 2 and word[-1] == word[-2] and _cons(word, len(word) - 1)


def _cvc(word: str) -> bool:
    if len(word) < 3:
        return False
    if (
        _cons(word, -1)
        and not _cons(word, -2)
        and _cons(word, -3)
        and word[-1] not in "wxy"
    ):
        return True
    return False


def stem_term(term: str) -> str:
    """Stem a single term using the Porter stemming algorithm."""

    word = term.lower()
    if len(word) <= 2:
        return word

    #################################
    # Step 1a
    #################################
    if word.endswith("sses"):
        word = word[:-2]
    elif word.endswith("ies"):
        word = word[:-2]
    elif word.endswith("ss"):
        pass
    elif word.endswith("s"):
        word = word[:-1]

    #################################
    # Step 1b
    #################################
    flag = False
    if word.endswith("eed"):
        base = word[:-3]
        if _measure(base) > 0:
            word = base + "ee"
    elif word.endswith("ed"):
        base = word[:-2]
        if _contains_vowel(base):
            word = base
            flag = True
    elif word.endswith("ing"):
        base = word[:-3]
        if _contains_vowel(base):
            word = base
            flag = True

    if flag:
        if word.endswith(("at", "bl", "iz")):
            word += "e"
        elif _double_consonant(word) and not word.endswith(("l", "s", "z")):
            word = word[:-1]
        elif _measure(word) == 1 and _cvc(word):
            word += "e"

    #################################
    # Step 1c
    #################################
    if word.endswith("y") and _contains_vowel(word[:-1]):
        word = word[:-1] + "i"

    #################################
    # Step 2
    #################################
    step2_map = {
        "ational": "ate",
        "tional": "tion",
        "enci": "ence",
        "anci": "ance",
        "izer": "ize",
        "abli": "able",
        "alli": "al",
        "entli": "ent",
        "eli": "e",
        "ousli": "ous",
        "ization": "ize",
        "ation": "ate",
        "ator": "ate",
        "alism": "al",
        "iveness": "ive",
        "fulness": "ful",
        "ousness": "ous",
        "aliti": "al",
        "iviti": "ive",
        "biliti": "ble",
        "xflurti": "xti",
    }
    for suffix, repl in step2_map.items():
        if word.endswith(suffix):
            base = word[: -len(suffix)]
            if _measure(base) > 0:
                word = base + repl
            break

    #################################
    # Step 3
    #################################
    step3_map = {
        "icate": "ic",
        "ative": "",
        "alize": "al",
        "iciti": "ic",
        "ical": "ic",
        "ful": "",
        "ness": "",
    }
    for suffix, repl in step3_map.items():
        if word.endswith(suffix):
            base = word[: -len(suffix)]
            if _measure(base) > 0:
                word = base + repl
            break

    #################################
    # Step 4
    #################################
    step4_list = [
        "al",
        "ance",
        "ence",
        "er",
        "ic",
        "able",
        "ible",
        "ant",
        "ement",
        "ment",
        "ent",
        "ion",
        "ou",
        "ism",
        "ate",
        "iti",
        "ous",
        "ive",
        "ize",
    ]
    for suffix in step4_list:
        if word.endswith(suffix):
            base = word[: -len(suffix)]
            if suffix == "ion" and base and base[-1] not in "st":
                continue
            if _measure(base) > 1:
                word = base
            break

    #################################
    # Step 5a
    #################################
    if word.endswith("e"):
        base = word[:-1]
        m = _measure(base)
        if m > 1 or (m == 1 and not _cvc(base)):
            word = base

    #################################
    # Step 5b
    #################################
    if _measure(word) > 1 and _double_consonant(word) and word.endswith("l"):
        word = word[:-1]

    return word


def stem_terms(terms: list[str]) -> list[str]:
    return [stem_term(t) for t in terms]


def load_collection_from_url(
    url: str,
    search_pattern: re.Pattern,
    start_line: int,
    end_line: int,
    author: str,
    origin: str,
) -> List[Document]:
    """
    Download a plain-text file from the given URL, extract individual stories or chapters,
    and return a list of Document objects.

    Parameters:
        url: URL of the text file to download
        search_pattern: regex with two capture groups (title and story body)
        start_line: Line number to start reading from (0-based index)
        end_line: Line number to end reading (exclusive)
        author: Author name to assign to each document
        origin: Source title to assign to each document

    Returns:
        List[Document]: Parsed Document instances for each story
    """
    # download full text and slice to desired lines
    full_text = download_text(url)
    sliced = slice_text_lines(full_text, start_line, end_line)
    docs: list[Document] = []
    # find all matches for title and body
    for idx, match in enumerate(search_pattern.finditer(sliced)):
        title = match.group(1).strip()
        body = match.group(2).strip()
        # flatten newlines in body
        raw_text = " ".join(body.splitlines()).strip()
        terms = tokenize(raw_text)
        doc = Document(
            document_id=idx,
            title=title,
            raw_text=raw_text,
            terms=terms,
            author=author,
            origin=origin,
        )
        docs.append(doc)
    return docs


def linear_boolean_search(
    term: str,
    collection: list[Document],
    stopword_filtered: bool = False,
    stemmed: bool = False,
) -> list[tuple[int, Document]]:
    """Perform a linear Boolean search: return (score, doc) for each document."""

    query = stem_term(term.lower()) if stemmed else term.lower()
    results: list[tuple[int, Document]] = []
    for doc in collection:
        if stopword_filtered:
            ft = doc.filtered_terms
            terms_list = ft() if callable(ft) else ft
        else:
            terms_list = doc.terms

        if stemmed:
            terms_list = [stem_term(t) for t in terms_list]

        found = any(t.lower() == query for t in terms_list)
        score = 1 if found else 0
        if stemmed:
            if found:
                results.append((score, doc))
        else:
            results.append((score, doc))
    return results

def precision_recall(retrieved, relevant):
    """Calculate precision and recall given retrieved and relevant document IDs."""
    retrieved_set = set(retrieved)
    relevant_set = set(relevant)
    if not retrieved_set or not relevant_set:
        return 0.0, 0.0
    intersection = retrieved_set & relevant_set
    precision = len(intersection) / len(retrieved_set) if retrieved_set else 0.0
    recall = len(intersection) / len(relevant_set) if relevant_set else 0.0
    return precision, recall


##############################
# Vector Space Model Search  #
##############################

def _build_inverted_index(
    docs: list[Document], stopword_filtered: bool, stemmed: bool
) -> tuple[list[dict[str, int]], dict[str, int]]:
    """Return term frequencies per doc and document frequencies."""

    doc_tfs: list[dict[str, int]] = []
    df: dict[str, int] = {}

    for doc in docs:
        if stopword_filtered:
            ft = doc.filtered_terms
            terms = ft() if callable(ft) else ft
        else:
            terms = doc.terms

        if stemmed:
            terms = [stem_term(t) for t in terms]

        tf: dict[str, int] = {}
        for t in terms:
            tl = t.lower()
            tf[tl] = tf.get(tl, 0) + 1
        for term in tf.keys():
            df[term] = df.get(term, 0) + 1
        doc_tfs.append(tf)

    return doc_tfs, df


def vector_space_search(
    query: str,
    collection: list[Document],
    stopword_filtered: bool = False,
    stemmed: bool = False,
) -> list[tuple[float, Document]]:
    """Search using the vector space model with tf-idf weighting."""

    if not collection:
        return []

    doc_tfs, df = _build_inverted_index(collection, stopword_filtered, stemmed)

    N = len(collection)

    # preprocess query
    q_terms = query.lower().split()
    if stemmed:
        q_terms = [stem_term(t) for t in q_terms]

    q_tf: dict[str, int] = {}
    for t in q_terms:
        q_tf[t] = q_tf.get(t, 0) + 1

    max_tf = max(q_tf.values()) if q_tf else 1

    # compute query vector weights
    q_vec: dict[str, float] = {}
    for term, freq in q_tf.items():
        tf_weight = 0.5 + 0.5 * freq / max_tf
        idf_weight = math.log(N / df.get(term, 1)) if term in df else 0.0
        q_vec[term] = tf_weight * idf_weight

    q_norm = math.sqrt(sum(v * v for v in q_vec.values()))

    results: list[tuple[float, Document]] = []

    for doc, tf in zip(collection, doc_tfs):
        vec: dict[str, float] = {}
        for term, f in tf.items():
            idf_w = math.log(N / df[term]) if df[term] else 0.0
            vec[term] = f * idf_w

        d_norm = math.sqrt(sum(v * v for v in vec.values()))

        # compute dot product
        dot = 0.0
        for term, weight in q_vec.items():
            dot += weight * vec.get(term, 0.0)

        score = dot / (d_norm * q_norm) if d_norm and q_norm else 0.0
        results.append((score, doc))

    return results
