from WLD_analyzer import WLD_analyzer

analyzer = WLD_analyzer()

def hypothesis1():
    authors = analyzer.authors
    analyzer.compare_distribution(authors, kind='author')

def hypothesis2(author):
    books = analyzer.books_by_author[author]
    analyzer.compare_distribution(books, kind='book')

hypothesis2('dickens')