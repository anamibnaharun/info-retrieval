# Information Retrieval - Practical Task 2
# Wrapper for Unit Tests
# Version 1.0 (2025-05-24)

# You must implement this file so that the test suite can run your code.
# This file acts as a bridge between your individual implementation and the expected interface.

# You are free to organize your own code however you want - but make sure
# that the following three functions are importable and behave as specified below.

from document import Document
from re import Pattern
from porter_stemmer import PorterStemmer
from my_module import precision_recall



def remove_stopwords_by_list(doc: Document, stopwords: set[str]):
    """
    Remove stopwords from the given document and store the result in doc.filtered_terms.
    
    implementation must:
    - Take a Document object and a set of stop words
    - Filter out the stop words from doc.terms
    - Store the cleaned list in doc.filtered_terms
    - Leave doc.terms and doc.raw_text unchanged

    Parameters:
        doc: The document to clean
        stopwords: The stop words to remove
    """

    # The following code is an example. It can be replaced to see it how you see fit:
    from my_module import remove_stop_words
    doc.filtered_terms = remove_stop_words(doc.terms, stopwords)


def remove_stopwords_by_frequency(doc, collection: list[Document], common_frequency: float, rare_frequency: float):
    """
    Remove stopwords from the given document and store the result in doc.filtered_terms.

    implementation must:
    - Take a Document object and a set of stop words
    - Filter out the stop words from doc.terms
    - Store the cleaned list in doc.filtered_terms
    - Leave doc.terms and doc.raw_text unchanged

    Parameters:
        doc: The document to clean
        collection: A collection of documents to use as a reference
        common_frequency: The frequency at which a term is "too common" to hold meaningful semantics.
        rare_frequency: The frequency at which a term is "too rare" to help finding a document.
    """

    # The following code is an example. It  may replace it how you see fit:
    # from my_module import remove_stopwords
    # remove_stopwords_by_frequency(doc, collection, common_frequency, rare_frequency)

    from my_module import remove_stop_words_by_frequency
    doc.filtered_terms = remove_stop_words_by_frequency(doc.terms, collection, low_freq=rare_frequency, high_freq=common_frequency)


def load_documents_from_url(url: str, author: str, origin: str, start_line: int, end_line: int,
                            search_pattern: Pattern[str]) -> list[Document]:
    """
    Download a text from the given URL, extract stories/chapters and return them as Document objects.

    Your implementation must:
    - Download the text file at the given URL
    - Split it into individual stories (each a Document)
    - Fill in all Document fields: title, raw_text, terms, author, origin (URL)
    - Return a list of Document instances

    Parameters:
        url (str): The URL to the Project Gutenberg text file
        author (str): The author name to assign to each document
        origin: The title of the containing collection, to assign to each document
        start_line: Line number from where to start searching
        end_line: Line number until which to search
        search_pattern: RE pattern where the 1st capture group contains the title and the 2nd the text of the document


    Returns:
        list[Document]: List of parsed documents
    """

    # The following code is an example. You may replace it how you see fit:
    from my_module import load_collection_from_url
    return load_collection_from_url(url, search_pattern, start_line, end_line, author, origin)



# PR03 Implementation
def linear_boolean_search(term, collection, stopword_filtered=False, stemmed=False):
    from my_module import linear_boolean_search
    return linear_boolean_search(term, collection, stopword_filtered, stemmed)

def vector_space_search(query, collection, stopword_filtered=False, stemmed=False):
    from my_module import vector_space_search
    return vector_space_search(query, collection, stopword_filtered, stemmed)

stemmer = PorterStemmer()
def stem_term(term):
    return stemmer.stem(term)
