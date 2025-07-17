"""
Helper module for IR processing logic: downloading collections, tokenizing, stopword removal, and search.
"""

import re
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
    term: str, collection: list[Document], stopword_filtered: bool = False
) -> list[tuple[int, Document]]:
    """Perform a linear Boolean search: return (score, doc) for each document."""
    term_lower = term.lower()
    results: list[tuple[int, Document]] = []
    for doc in collection:
        if stopword_filtered:
            ft = doc.filtered_terms
            # support filtered_terms as method or list attribute
            terms_list = ft() if callable(ft) else ft
        else:
            terms_list = doc.terms
        # case-insensitive matching
        found = any(t.lower() == term_lower for t in terms_list)
        score = 1 if found else 0
        results.append((score, doc))
    return results
