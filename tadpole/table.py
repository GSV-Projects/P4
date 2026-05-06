import csv
import pandas as pd
import urllib.request
from utils.NAliteral import NA

class Table():
    def __init__(self, columns):
        self.columns = columns
    
    def __repr__(self):
        return f"{self.columns}"

    # Method that reads from a URL and saves it in the table object.
    def read(self, url):
        #Check if the URL is viable and working.
        if not url != "":
            raise Exception("URL cannot be empty")
        print("Her", url)
        try: # Establish connection to check validity of URL.
            urllib.request.urlopen(url, timeout=5) 
        except urllib.error.URLError as e:
            raise Exception(f"Incorrect URL: '{url}") # If error occurs, URL is incorrect.
        
        # Check if the CSV has headers for each column
        header_peek = pd.read_csv(url, nrows=1, header=None) # Read csv.
        first_row = header_peek.iloc[0].tolist() # First row, should hold string of headers.
        has_header = all(isinstance(v, (str)) for v in first_row)
        if has_header:
            df = pd.read_csv(url)
        else:
            df = pd.read_csv(url, header=None)
            # If columns have no header, create customs in col1, col2... format
            df.columns = [f"col{i+1}" for i in range(len(df.columns))]

        # Save the CSV columns wise to the columns of the object, and return.
        self.columns = df.to_dict(orient="list")
        self.cleanValues(self.columns)
        return self
    
    # Table - loops through each column and checks whether a value is NA
    def cleanValues(self, columns):
        for column in columns:
            self.columns[column] = [self.replaceNaN(v) for v in self.columns[column]]
        return self

    # var - replaces missing values with our own literal 'NA'
    def replaceNaN(self, value):
        if value in ('nan', 'NaN', 'na', 'NAN', 'NA', None, '', 'N/A') or value != value:  # value != value catches float NaN
            return NA
        return value
    
    def replaceNAvalues(self, column, value):
        for key in self.columns[column]:
            if key == NA:
                self.columns[column] = value
        return self
    
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

    # table - round a column to whole integers
    def round(self, column):
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")
        col = self.columns[column]
    
        if not all(isinstance(v, (int, float)) for v in col):
            raise Exception(f"Column '{column}' must only consist of integers or floats")

        self.columns[column] = [round(v) for v in col]
        return self

    # column - rename the key of a given column
    def rename(self, column, name):
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")
        self.columns = {
            name if k == column else k: v 
            for k, v in self.columns.items()}
        return self
    
    # array - returns array of all keys in a table
    def keys(self):
        keys = []
        for column in self.columns:
            keys.append(column)

        return keys

    # var - returns the length of a given column / number of rows in a table
    def lenCol(self, column):
        return len(self.columns[column])
    
    # table - sort whole table from one column, numerically for numbers or
    # alphabetically for strings.
    def sort(self, column):
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")
        
        col = self.columns[column]

        # Uses Python 'sorted' which takes the key 'lambda' to ensure it is sorted by values, not indecies
        sorted_indices = sorted(range(len(col)), key=lambda i: col[i])
        # Rebuild the table in new order
        self.columns = {k: [v[i] for i in sorted_indices] for k, v in self.columns.items()}
        return self
        
    # array - given a column, returns an array of the column sorted
    # sorted numerically for numbers and alphabetically for strings.
    def sortcol(self, column):
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")

        return sorted(self.columns[column])