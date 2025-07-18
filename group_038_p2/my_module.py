from document import Document
from re import Pattern
import urllib.request
import re
from typing import Pattern
import string
from collections import defaultdict, Counter
import math
from porter_stemmer import PorterStemmer

def remove_stop_words(terms: list[str], stopwords: set[str]) -> list[str]:
    """
    Filters out stop words from a list of terms (case-insensitive, punctuation removed).
    """
    translator = str.maketrans('', '', string.punctuation)
    return [
        term.lower().translate(translator)
        for term in terms
        if term.lower().translate(translator) not in stopwords
    ]


def remove_stop_words_by_frequency(
    terms: list[str],
    collection: list[Document],
    low_freq: float,
    high_freq: float
) -> list[str]:
    """
    Filters out common and rare terms based on frequency thresholds.
    Returns a cleaned list of terms from `terms`.
    """
    # Clean and count terms across collection
    translator = str.maketrans('', '', string.punctuation)
    cleaned_collection_terms = []

    for doc in collection:
        cleaned = [term.lower().translate(translator) for term in doc.terms]
        cleaned_collection_terms.extend(cleaned)

    total_terms = len(cleaned_collection_terms)
    term_freqs = Counter(cleaned_collection_terms)

    # Build stopword set from high and low frequency thresholds
    stopwords = set()
    for term, count in term_freqs.items():
        freq = count / total_terms
        if freq >= high_freq or freq <= low_freq:
            stopwords.add(term)

    # Now clean the input terms from the current doc
    return [
        term.lower().translate(translator)
        for term in terms
        if term.lower().translate(translator) not in stopwords
    ]


# Previous Version
# There might have some problem with the test cases
def load_collection_from_url(
    url: str,
    search_pattern: Pattern[str],
    start_line: int,
    end_line: int,
    author: str,
    origin: str
) -> list[Document]:
    """
    Download a text from the given URL, extract, and return them as Document objects.
    """
    # Download text from the URL
    with urllib.request.urlopen(url) as response:
        raw_text = response.read().decode('utf-8')

    # Extract lines within the specified range
    lines = raw_text.splitlines()
    selected_text = "\n".join(lines[int(start_line):int(end_line)])

    # Use the regex pattern to extract (title, body) pairs
    matches = re.findall(search_pattern, selected_text)

    documents = []
    for i, (title, body) in enumerate(matches):
        # Normalize whitespace and tokenize
        raw_text = body.replace("\n", " ").strip()
        terms = re.findall(r'\b\w+\b', raw_text.lower())

        # Construct Document object
        doc = Document(
            document_id=i,
            title=title.strip(),
            raw_text=raw_text,
            terms=terms,
            author=author,
            origin=origin
        )
        documents.append(doc)

    return documents


## PR03 Implementation

def linear_boolean_search(term, collection, stopword_filtered=False, stemmed=False):
    stemmer = PorterStemmer()
    if stemmed:
        query_term = stemmer.stem(term)
    else:
        query_term = term.lower()

    results = []
    for doc in collection:
        if stemmed and stopword_filtered:
            if hasattr(doc, "filtered_stemmed_terms") and isinstance(doc.filtered_stemmed_terms, list):
                terms_to_search = doc.filtered_stemmed_terms
            else:
                terms_to_search = doc.filtered_stemmed_terms()
        elif stemmed:
            if hasattr(doc, "stemmed_terms") and isinstance(doc.stemmed_terms, list):
                terms_to_search = doc.stemmed_terms
            else:
                terms_to_search = doc.stemmed_terms()
        elif stopword_filtered:
            # Fix: handle both list and method for filtered_terms (test sets .filtered_terms as list)
            if hasattr(doc, "filtered_terms") and isinstance(doc.filtered_terms, list):
                terms_to_search = doc.filtered_terms
            else:
                terms_to_search = doc.filtered_terms()
        else:
            terms_to_search = [t.lower() for t in doc.terms]

        found = any(t == query_term for t in terms_to_search)
        if stemmed:
            if found:
                results.append((1, doc))
        else:
            results.append((1 if found else 0, doc))
    return results


def vector_space_search(query: str, collection: list, stopword_filtered: bool = False, stemmed: bool = False):
    """
    Vector Space Model search with tf-idf weights and inverted index.
    Returns ranked list of (score, Document).
    """
    stemmer = PorterStemmer()

    # Select document terms according to options
    def get_terms(doc):
        if stemmed and stopword_filtered:
            return doc.filtered_stemmed_terms()
        elif stemmed:
            return doc.stemmed_terms()
        elif stopword_filtered:
            return doc.filtered_terms()
        else:
            return doc.terms

    # Process query
    query_terms = query.lower().split()
    if stemmed:
        query_terms = [stemmer.stem(t) for t in query_terms]
    # You may want to filter stopwords for query as well, if required

    # Build inverted index and document term counts
    N = len(collection)
    doc_term_counts = []
    df = Counter()
    for doc in collection:
        terms = get_terms(doc)
        counts = Counter(terms)
        doc_term_counts.append(counts)
        for term in set(terms):
            df[term] += 1

    # Compute tf-idf vectors for docs and query
    scores = []
    for doc, doc_counts in zip(collection, doc_term_counts):
        doc_vec = []
        query_vec = []
        all_terms = set(query_terms)
        for term in all_terms:
            tf = doc_counts[term]
            idf = math.log((N + 1) / (df[term] + 1)) + 1  # +1 smoothing
            doc_tf_idf = tf * idf
            doc_vec.append(doc_tf_idf)

            qtf = query_terms.count(term)
            query_tf_idf = qtf * idf
            query_vec.append(query_tf_idf)
        # Cosine similarity
        num = sum(d*q for d, q in zip(doc_vec, query_vec))
        denom = math.sqrt(sum(d*d for d in doc_vec)) * math.sqrt(sum(q*q for q in query_vec))
        score = num / denom if denom > 0 else 0.0
        scores.append((score, doc))
    return scores


def precision_recall(retrieved: set, relevant: set) -> tuple:
    """
    Computes precision and recall given sets of retrieved and relevant document ids.

    Parameters:
        retrieved (set): The set of retrieved document ids.
        relevant (set): The set of relevant document ids.

    Returns:
        (precision, recall): tuple of floats
    """
    if not retrieved:
        precision = 0.0
    else:
        precision = len(retrieved & relevant) / len(retrieved)

    if not relevant:
        recall = 0.0
    else:
        recall = len(retrieved & relevant) / len(relevant)

    return (precision, recall)
