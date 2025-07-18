"""
Helper module for IR processing logic: downloading collections, tokenizing, stopword removal, and search.
"""

import re
import urllib.request
from typing import List

from document import Document


# --- Helper code for Porter stemming ---
VOWELS = "aeiou"


def _is_consonant(word: str, i: int) -> bool:
    if i < 0:
        i += len(word)
    ch = word[i]
    if ch in VOWELS:
        return False
    if ch == "y":
        return False if i == 0 else not _is_consonant(word, i - 1)
    return True


def _measure(word: str) -> int:
    """Return the measure (m) of a word as defined in the Porter algorithm."""
    m = 0
    i = 0
    length = len(word)
    while i < length:
        while i < length and _is_consonant(word, i):
            i += 1
        if i >= length:
            break
        while i < length and not _is_consonant(word, i):
            i += 1
        m += 1
    return m


def _contains_vowel(word: str) -> bool:
    return any(not _is_consonant(word, i) for i in range(len(word)))


def _doublec(word: str) -> bool:
    return len(word) >= 2 and word[-1] == word[-2] and _is_consonant(word, len(word) - 1)


def _cvc(word: str) -> bool:
    if len(word) < 3:
        return False
    if not (_is_consonant(word, -1) and not _is_consonant(word, -2) and _is_consonant(word, -3)):
        return False
    return word[-1] not in "wxy"


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


def stem_term(term: str) -> str:
    """Stem a single term using a simplified Porter algorithm."""
    word = term.lower()

    # Step 1a
    if word.endswith("sses"):
        word = word[:-2]
    elif word.endswith("ies"):
        word = word[:-2]
    elif word.endswith("ss"):
        pass
    elif word.endswith("s"):
        word = word[:-1]

    # Step 1b
    if word.endswith("eed"):
        stem = word[:-3]
        if _measure(stem) > 0:
            word = word[:-1]
    elif word.endswith("ed"):
        stem = word[:-2]
        if _contains_vowel(stem):
            word = stem
            if word.endswith(("at", "bl", "iz")):
                word += "e"
            elif _doublec(word) and word[-1] not in "lsz":
                word = word[:-1]
            elif _measure(word) == 1 and _cvc(word):
                word += "e"
    elif word.endswith("ing"):
        stem = word[:-3]
        if _contains_vowel(stem):
            word = stem
            if word.endswith(("at", "bl", "iz")):
                word += "e"
            elif _doublec(word) and word[-1] not in "lsz":
                word = word[:-1]
            elif _measure(word) == 1 and _cvc(word):
                word += "e"

    # Step 1c
    if word.endswith("y") and _contains_vowel(word[:-1]):
        word = word[:-1] + "i"

    # Step 2 (partial)
    if word.endswith("er") and _measure(word[:-2]) > 0:
        word = word[:-2]

    # Step 4 (partial for 'ion')
    if word.endswith("ion") and len(word) > 4 and word[-4] in "st" and _measure(word[:-3]) > 1:
        word = word[:-3]

    return word


def stem_terms(terms: list[str]) -> list[str]:
    """Stem a list of terms."""
    return [stem_term(t) for t in terms]


def update_document_stems(doc: Document) -> None:
    """Update the stem-related term lists of a Document."""
    doc._stemmed_terms = stem_terms(doc.terms)
    ft = doc.filtered_terms
    filtered = ft() if callable(ft) else ft
    doc._filtered_stemmed_terms = stem_terms(filtered)


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
        update_document_stems(doc)
        docs.append(doc)
    return docs


def linear_boolean_search(
    term: str,
    collection: list[Document],
    stopword_filtered: bool = False,
    stemmed: bool = False,
) -> list[tuple[int, Document]]:
    """Perform a linear Boolean search: return (score, doc) for each document."""
    term_cmp = stem_term(term) if stemmed else term.lower()
    results: list[tuple[int, Document]] = []
    for doc in collection:
        if stopword_filtered:
            ft = doc.filtered_terms
            terms_list = ft() if callable(ft) else ft
            if stemmed:
                if not doc._filtered_stemmed_terms:
                    doc._filtered_stemmed_terms = stem_terms(terms_list)
                tokens = doc._filtered_stemmed_terms
            else:
                tokens = [t.lower() for t in terms_list]
        else:
            terms_list = doc.terms
            if stemmed:
                if not doc._stemmed_terms:
                    doc._stemmed_terms = stem_terms(terms_list)
                tokens = doc._stemmed_terms
            else:
                tokens = [t.lower() for t in terms_list]

        found = any(tok == term_cmp for tok in tokens)
        score = 1 if found else 0
        if stemmed:
            if found:
                results.append((score, doc))
        else:
            results.append((score, doc))
    return results


def vector_space_search(
    query: str,
    collection: list[Document],
    stopword_filtered: bool = False,
    stemmed: bool = False,
) -> list[tuple[float, Document]]:
    """Simple vector space search using term overlap as score."""
    query_terms = tokenize(query)
    if stemmed:
        query_terms = stem_terms(query_terms)
    query_terms = [t.lower() for t in query_terms]

    results: list[tuple[float, Document]] = []
    for doc in collection:
        if stopword_filtered:
            ft = doc.filtered_terms
            terms_list = ft() if callable(ft) else ft
        else:
            terms_list = doc.terms
        if stemmed:
            terms_list = stem_terms(terms_list)
        terms_list = [t.lower() for t in terms_list]
        score = sum(1 for t in query_terms if t in terms_list)
        results.append((float(score), doc))
    return results


def precision_recall(retrieved: set[int], relevant: set[int]) -> tuple[float, float]:
    """Compute precision and recall."""
    if not retrieved:
        precision = 0.0
    else:
        precision = len(retrieved & relevant) / len(retrieved)
    if not relevant:
        recall = 0.0
    else:
        recall = len(retrieved & relevant) / len(relevant)
    return precision, recall
