class Table():
    def __init__(self, columns):
        self.columns = columns
    
    def __repr__(self):
        return f"{self.columns}"
        
    # array - returns a column requested by string name
    def getcol(self, column):
        col = self.columns[column]
        return col
    
    # array - returns the first column of a table
    def getfirst(self):
        key_list = list(self.columns.keys())
        first = key_list[0]
        return self.columns[first]

    # array - returns the last column of a table
    def getlast(self):
        key_list = list(self.columns.keys())
        last = key_list[len(key_list) - 1]
        return self.columns[last]
    
    # number - returns the mean of all values in a given column
    def mean(self, column):
        col = self.columns[column]
        return sum(col) / len(col)
    
    # var?? - returns the first element in a column of the table - WIP
    def first(self, column):
        col = self.columns[column]
        return col[0]
    
    # var?? - returns the last element in a column of the table - WIP 
    def last(self, column):
        col = self.columns[column]
        last = len(col) - 1
        return col[last]

    # number - total sum of all elements in column
    def sum(self, column):
        col = self.columns[column]
        if not all(isinstance(v, (int, float)) for v in col):
            raise Exception("Given type cannot be summed")
        return sum(col)
    
    # number - how often some value occurs within a column - WIP
    def frequency(self, column, val):
        pass

    # tbl - returns the cleaned versoin of the same table, excluding the given column
    def filter(self, column = None):
        new_table = {}

        # for hver række (index)
        for i in len(self.columns.column):
            for col in self.columns:
                if col[i] is NA:
                    pass

        # for col in self.columns:
        #     if col == column:
        #         pass
        #     else:
        #         new_table.update({col : self.columns[col]})
        # return new_table

    # number - number at 50% of column summation
    def median(self, column):
        pass

    # number - number at 25% of column summation
    def lowerq(self, column):
        pass

    # number - number at 75% og column summation
    def upperq(self, column):
        pass

    # number?? - minimum value in column
    def min(self, column):
        col = self.columns[column]
        # min = col[0]
        # for i in col:
        #     if col[i] < min:
        #         min = col[i]
        # return min

        return min(col)

    # number?? - maximum value in column
    def max(self, column):
        col = self.columns[column]
        # max = col[0]
        # for i in col:
        #     if col[i] > max:
        #         min = col[i]
        # return min

        return max(col)

    # var - numeral difference from min to max value
    def span(self, column):
        col = self.columns[column]
        return max(col) - min(col)