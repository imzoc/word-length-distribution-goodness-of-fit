import nltk
from scipy.stats import chisquare
import os
import matplotlib.pyplot as plt
import numpy as np


class WLD_analyzer:
    """ This class assumes that you have a directory with "pre-cleaned"
    text files (i.e. any boilerplate is already removed). This class provides
    the capability to compare word-length distributions between different books
    and also between different authors (represented by all of their books).
    
    Every "comparison" between two or more items of the same kind (i.e. you
    can only compare authors to authors, books to books, apples to apples and
    oranges to oranges) includes a chi square goodness-of-fit test for the
    entire distribution and graphs the word-length distributions of each item
    against each other.
    
    The three methods you'll find most useful are compare and compare_all_by.
    """

    def __init__(self, dir_name='./texts'):
        """ __init__ automatically reads in, tokenizes, and stores the
        tokenized text for all files following 'title-author.txt' in dir_name.
        dir_name is ./texts by default
        """
        self.tokenized_texts = {}
        self.books_by_author = {'common-all': []}
        self.authors = []
        for filename in filter(lambda f: ('-' in f and f.endswith('.txt')), os.listdir(dir_name)):
            title, author = filename.replace('.txt', '').split('-')
            self.authors += [author]

            if author not in self.books_by_author.keys():
                self.books_by_author[author] = []
            self.books_by_author[author] += [title]
            self.books_by_author['common-all'] += [title]

            full_filename = os.path.join(dir_name, filename)
            with open(full_filename, 'r', encoding='utf-8') as file:
                self.tokenized_texts[title] = nltk.word_tokenize(file.read())
    
    def compare_distribution(self, names=None, kind=None):
        """Takes a list of items (authors or books). Compare them with a
        chi square goodness-of-fit test and graph them. """
        if kind == 'author' and not names:
            names = self.authors
        if kind == 'book' and not names:
            names = self.tokenized_texts.keys()
            
        # Do a chi square on author averages
        wld_lists = {name: self._wld_list(name, kind) for name in names}
        self.chi_square(wld_lists)

        # Do a graph
        wlds = {name: self._wld(name, kind) for name in names}
        self.graph(wlds)
        
    def graph(self, wlds):
        """ Takes a dictionary of {name: wld} and graphs each wld
        on top of all of the others, with a legend mapping to name. """
        for name, wld in wlds.items():
            wld_range = range(max(wld.keys()))
            plt.plot(wld_range,[wld.freq(i) for i in wld_range], label = name)
        plt.grid()
        plt.legend()
        plt.show()

    def chi_square(self, wld_lists):
        """ This method takes a dictionary of {name: wld_list}.
        It runs a chi-square goodness-of-fit test on each wld list,
        computing an "expected" wld list for the wld_list if it came
        from an average wld across all wld lists.
        """
        self.ensure_no_zeros(wld_lists)

        common_wld_list = self._common_wld_list(wld_lists.values())
        for name, wld_list in wld_lists.items():
            expected_wld_list = self._expected_wld_list(wld_list, common_wld_list)

            chi_value, p_value = chisquare(wld_list, expected_wld_list)
            print(f"{name} chisq:{chi_value}, p:{p_value}\n")

    def _tokens_from_name(self, name, kind):
        if kind == 'book':
            return self.tokenized_texts[name]
        elif kind == 'author':
            return sum(
                [self.tokenized_texts[book] for book in self.books_by_author[name]], []
            )
        else:
            raise ValueError(f"Kind must be 'book' or 'author', not {kind}")

    def _wld_list(self, name, kind):
        """ Takes the name of a book or author and a specification of
        whether it is a book or author. It then returns a word-length
        distribution in the form of a list (i.e. the first element is
        the number of 1-length words and so on) for that book or author.
        """
            
        wld = self._wld(name, kind)

        return [wld.get(word_length, 0) for word_length in wld.keys()]
    
    def _wld(self, name, kind):
        """ Takes a tokenized list of words and returns a word-length
        distribution of it. """
        tokenized_text = self._tokens_from_name(name, kind)
        return nltk.FreqDist([len(word) for word in tokenized_text])

    def ensure_no_zeros(self, wld_lists, smallest_acceptable_count=10):
        """ For a given dictionary of wld lists, cut each wld_list off at
        a point that ensures no zeros will corrupt the chi square test.
        This means the first word-length with a count less than some
        acceptable cutoff count (10 counts seems reasonable).
        For example, if the the first word-length that doesn't appear in
        each wld list at least 10 times is 15, cut all wld lists off at 15. 

        Lists are mutable, so this is done in-place.
        """
        max_idx = min([len(wld_list) for wld_list in wld_lists.values()]) - 1
        cutoff_idx = 0
        while cutoff_idx <= max_idx and\
          all(wld_list[cutoff_idx] >= smallest_acceptable_count for wld_list in wld_lists.values()):
            cutoff_idx += 1

        for key in wld_lists.keys():
            wld_lists[key] = wld_lists[key][:cutoff_idx]

    def _common_wld_list(self, wld_lists):
        """ Takes a list of wld lists (assumed to all be the same length)
        and computes a common wld list (i.e. sum all of the word-lengths
        in each wld list and return the totals)
        """
        word_length_range = range(len(list(wld_lists)[0]))

        common_wld_list = []
        for word_length in word_length_range:
            common_wld_list.append(0)
            for wld_list in wld_lists:
                if word_length < len(wld_list):
                    common_wld_list[-1] += wld_list[word_length]

        return common_wld_list

    def _expected_wld_list(self, wld_list, common_wld_list):
        """ This method returns an "expected" wld list for wld_list
        if it came from an the same distribution as common_wld_list.
        That is, return the common word-length distribution list, but
        with wld_list's number of observations.
        
        This method assumes that wld_list has no zeros in it, and cuts
        off all word-lengths beyond those in wld_list (if the common
        wld list records longer words that wld_list records). """
        common_wld_list = common_wld_list[:len(wld_list)]
        multiplier = sum(wld_list) / sum(common_wld_list)
        expected_wld_list = [round(count * multiplier) for count in common_wld_list]

        # Change the most frequently-occurring word length so that the total count in
        # each wld list is the same. Rounding can create small differences in total count
        # between wld lists, so this is important.
        expected_wld_list[np.argmax(expected_wld_list)] += sum(wld_list) - sum(expected_wld_list)
        return expected_wld_list

