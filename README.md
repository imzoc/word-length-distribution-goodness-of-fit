The WLD_analyzer class in WLD_analyzer.py assumes that you have a directory with "pre-cleaned"
    text files (i.e. any boilerplate is already removed). This class provides
    the capability to compare word-length distributions between different books
    and also between different authors (represented by all of their books).
    
The main helpful method in the class is compare. "comparison" is done between two or more items of the same kind (i.e. you
    can only compare authors to authors, books to books)
    includes a chi square goodness-of-fit test for the
    entire distribution and graphs the word-length distributions of each item
    against each other.

The paper contains an analysis of the books in ./texts/. It might be helpful to check it out
to get a better idea of what the WLD_analyzer class is useful for. main.py contains the code I ran for
testing my hypotheses, for reproducibility.
