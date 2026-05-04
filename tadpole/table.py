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

    # column - rename the key of a given column
    def rename(self, column, name):
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")
        self.columns = {
            name if k == column else k: v 
            for k, v in self.columns.items()}
        return self
        


    
#columns = 0
#data = Table(columns)
#data.read('https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')
