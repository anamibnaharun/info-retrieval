# # Contains a unified class definition for a document.
# # The implementation of this class may be altered, but the original public attributes/methods are accessible.
# # E. g. filtered_terms() may be changed to use to online filtering.

from porter_stemmer import PorterStemmer

MAX_PREVIEW_SIZE = 10

class Document(object):
    def __init__(self, document_id=None, title="", raw_text="", terms=None, author="", origin=""):
        if terms is None:
            terms = []
        self.document_id = document_id
        self.title = title
        self.raw_text = raw_text
        self.terms = terms
        # self._filtered_terms = []
        self.filtered_terms = []
        self._stemmed_terms = None
        self._filtered_stemmed_terms = None
        self.author = author
        self.origin = origin

    def __str__(self):
        shortened_content = (self.raw_text[:MAX_PREVIEW_SIZE] +
                             "...") if len(self.raw_text) > MAX_PREVIEW_SIZE else self.raw_text
        return 'D' + str(self.document_id).zfill(3) + ': ' + self.title + '("' + shortened_content + '")'

    # def filtered_terms(self):
    #     return self._filtered_terms

    def stemmed_terms(self):
        if self._stemmed_terms is None:
            stemmer = PorterStemmer()
            self._stemmed_terms = stemmer.stem_terms(self.terms)
        return self._stemmed_terms

    # def filtered_stemmed_terms(self):
    #     if self._filtered_stemmed_terms is None:
    #         stemmer = PorterStemmer()
    #         self._filtered_stemmed_terms = stemmer.stem_terms(self._filtered_terms)
    #     return self._filtered_stemmed_terms
    
    def filtered_stemmed_terms(self):
        if self._filtered_stemmed_terms is None:
            stemmer = PorterStemmer()
            self._filtered_stemmed_terms = stemmer.stem_terms(self.filtered_terms)
        return self._filtered_stemmed_terms




