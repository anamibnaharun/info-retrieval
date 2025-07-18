import unittest
from document import Document
import test_wrapper

import os

test_dir = os.path.dirname(__file__)
stopword_file_path = os.path.join(test_dir, "englishST.txt")


class TestTask2StopWords(unittest.TestCase):
    def test_stopwords_from_file_basic(self):
        doc = Document(0, "Test", "The fox jumps over the lazy dog",
                       ["the", "fox", "jumps", "over", "the", "lazy", "dog"],
                       author="Test", origin="Some random collection")


        with open(stopword_file_path, "r") as f:
            stopwords = set([line.strip().replace(' ', '') for line in f])
        test_wrapper.remove_stopwords_by_list(doc, stopwords)

        self.assertEqual(doc.filtered_terms, ["fox", "jumps", "lazy", "dog"])

    def test_stopwords_from_file_case_insensitive(self):
        doc = Document(1, "CaseTest", "The QUICK brown fox IN", ["The", "QUICK", "brown", "fox", "IN"],
                       author="Test", origin="Some random collection")
        with open(stopword_file_path, "r") as f:
            stopwords = set([line.strip().replace(' ', '') for line in f])
        test_wrapper.remove_stopwords_by_list(doc, stopwords)

        self.assertEqual(doc.filtered_terms, ["quick", "brown", "fox"])

    def test_stopwords_by_frequency(self):
        d1 = Document(0, "D1", "a a a a a b", ["a", "a", "a", "a", "a", "b"], "Author", "Source")
        d2 = Document(1, "D2", "c d e f", ["c", "d", "e", "f"], "Author", "Source")
        d3 = Document(2, "D3", "a f g", ["a", "f", "g"], "Author", "Source")

        test_wrapper.remove_stopwords_by_frequency(d3, [d1, d2, d3], 0.1, 0.9)
        self.assertIsInstance(d3.filtered_terms, list)
        self.assertTrue(all(isinstance(t, str) for t in d3.filtered_terms))
        self.assertNotIn("a", d3.filtered_terms)  # a is very frequent
        self.assertNotIn("g", d3.filtered_terms)  # g is very rare
