class Table():
    def __init__(self, columns):
        self.columns = columns
    
    def __repr__(self):
        return f"{self.columns}"
    
    #def reader
    
    # col (array?) - returns a column requested by string name
    def getcol(self, column):
        pass
    
    # number - returns the mean of all values in a given column
    def mean(self, column):
        col = self.columns[column]
        return sum(col) / len(col)
    
    # array - returns the first column of the table
    def first(self, column):
        #return self.columns[column][0]
        pass
    
    # array - returns the last column of the table
    def last(self, column):
        pass
    
    # number - total sum of all elements in column
    def sum(self, column):
        # col = self.columns[column]
        # if not all(isinstance(v, (int, float)) for v in col):
        #     raise Exception("Given type cannot be summed")
        # return sum(col)
        pass
    
    # number - how often some value occurs within a column
    def frequency(self, column):
        pass

    # tbl - returns the cleaned versoin of the same table, excluding the given column
    def filter(self, column):
        pass

    # number - number at 50% of column summation
    def median(self, column):
        pass

    # number - number at 25% of column summation
    def lowerq(self, column):
        pass

    # number - number at 75% og column summation
    def upperq(self, column):
        pass

    # var - minimum value in column
    def min(self, column):
        pass

    # var - maximum value in column
    def max(self, column):
        pass

    # var - numeral difference from min to max value
    def span(self, column):
        pass