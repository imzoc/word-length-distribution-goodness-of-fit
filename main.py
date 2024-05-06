from WLD_analyzer import WLD_analyzer

analyzer = WLD_analyzer()

def hypothesis1():
    authors = analyzer.authors
    analyzer.compare_distribution(authors, kind='author')

def hypothesis2(author):
    books = analyzer.books_by_author[author]
    analyzer.compare_distribution(books, kind='book')

hypothesis1()

# matplotlib plots stall the execution of the python script
# and terminate the python script when you close the plot,
# so I ran hypothesis 2 manually for each author (by putting
# a different author first in line on each execution).
hypothesis2('dickens')
hypothesis2('austen')
hypothesis2('tolstoy')
