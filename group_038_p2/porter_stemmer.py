import re

class PorterStemmer:
    """
    Porter Stemming Algorithm (1980), as a reusable class.
    """

    def __init__(self):
        self.vowels = "aeiou"

    def is_consonant(self, word, i):
        ch = word[i]
        if ch in self.vowels:
            return False
        if ch == 'y':
            if i == 0:
                return True
            else:
                return not self.is_consonant(word, i - 1)
        return True

    def measure(self, stem):
        n = 0
        prev_c = False
        for i in range(len(stem)):
            curr_c = self.is_consonant(stem, i)
            if i == 0:
                prev_c = curr_c
                continue
            if not prev_c and curr_c:
                n += 1
            prev_c = curr_c
        return n

    def contains_vowel(self, stem):
        for i in range(len(stem)):
            if not self.is_consonant(stem, i):
                return True
        return False

    def ends_with_double_consonant(self, word):
        return (len(word) >= 2 and
                word[-1] == word[-2] and
                self.is_consonant(word, len(word) - 1))

    def ends_cvc(self, word):
        if len(word) < 3:
            return False
        if (self.is_consonant(word, -1) and
            not self.is_consonant(word, -2) and
            self.is_consonant(word, -3)):
            ch = word[-1]
            return ch not in "wxy"
        return False

    def stem(self, word):
        word = word.lower()
        if len(word) <= 2:
            return word

        # Step 1a
        if word.endswith('sses'):
            word = word[:-2]
        elif word.endswith('ies'):
            word = word[:-2]
        elif word.endswith('ss'):
            pass
        elif word.endswith('s'):
            word = word[:-1]

        # Step 1b
        flag_1b = False
        if word.endswith('eed'):
            stem = word[:-3]
            if self.measure(stem) > 0:
                word = word[:-1]
        elif word.endswith('ed'):
            stem = word[:-2]
            if self.contains_vowel(stem):
                word = stem
                flag_1b = True
        elif word.endswith('ing'):
            stem = word[:-3]
            if self.contains_vowel(stem):
                word = stem
                flag_1b = True
        if flag_1b:
            if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
                word += 'e'
            elif self.ends_with_double_consonant(word):
                if word[-1] not in 'lsz':
                    word = word[:-1]
            elif self.measure(word) == 1 and self.ends_cvc(word):
                word += 'e'

        # Step 1c
        if word.endswith('y'):
            stem = word[:-1]
            if self.contains_vowel(stem):
                word = stem + 'i'

        # Step 2
        step2list = {
            'ational': 'ate',
            'tional': 'tion',
            'enci': 'ence',
            'anci': 'ance',
            'izer': 'ize',
            'abli': 'able',
            'alli': 'al',
            'entli': 'ent',
            'eli': 'e',
            'ousli': 'ous',
            'ization': 'ize',
            'ation': 'ate',
            'ator': 'ate',
            'alism': 'al',
            'iveness': 'ive',
            'fulness': 'ful',
            'ousness': 'ous',
            'aliti': 'al',
            'iviti': 'ive',
            'biliti': 'ble',
            'logi': 'log'
        }
        for key in step2list:
            if word.endswith(key):
                stem = word[:-len(key)]
                if self.measure(stem) > 0:
                    word = stem + step2list[key]
                break

        # Step 3
        step3list = {
            'icate': 'ic',
            'ative': '',
            'alize': 'al',
            'iciti': 'ic',
            'ical': 'ic',
            'ful': '',
            'ness': ''
        }
        for key in step3list:
            if word.endswith(key):
                stem = word[:-len(key)]
                if self.measure(stem) > 0:
                    word = stem + step3list[key]
                break

        # Step 4
        step4list = [
            'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement',
            'ment', 'ent', 'ion', 'ou', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize'
        ]
        for key in step4list:
            if word.endswith(key):
                stem = word[:-len(key)]
                if key == 'ion':
                    if len(stem) > 0 and stem[-1] in 'st':
                        if self.measure(stem) > 1:
                            word = stem
                    continue
                if self.measure(stem) > 1:
                    word = stem
                break

        # Step 5a
        if word.endswith('e'):
            stem = word[:-1]
            m = self.measure(stem)
            if m > 1:
                word = stem
            elif m == 1 and not self.ends_cvc(stem):
                word = stem

        # Step 5b
        if self.measure(word) > 1 and self.ends_with_double_consonant(word) and word.endswith('l'):
            word = word[:-1]

        return word

    def stem_terms(self, terms):
        return [self.stem(term) for term in terms]
