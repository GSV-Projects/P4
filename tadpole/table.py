from utils.NAliteral import NA
import math
import csv
import pandas as pd
import urllib.request

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
        print(first_row)
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
    
    # var - returns the first element in a column of the table 
    def first(self, column):
        col = self.columns[column]
        return col[0]
    
    # var - returns the last element in a column of the table 
    def last(self, column):
        col = self.columns[column]
        last = len(col) - 1
        return col[last]

    # number - total sum of all elements in column
    def sum(self, column):
        col = self.columns[column]
        if not all(isinstance(v, (int, float)) for v in col):
            raise Exception("Given type is not a number and cannot be summed")
        return sum(col)
    
    # number - how often some value occurs within a column - WIP
    def frequency(self, column, val):
        count = 0
        for v in self.columns[column]:
            if v == val: count += 1
        return count

    # tbl - returns the cleaned versoin of the same table, excluding the row with NA or a given value
    def filter(self, value = None):
        # make array of lengths of columns, then check if they're all the same
        num_entries = [len(vals) for vals in self.columns.values()] 
        # set() method turns arrya into set. 
        # If there are more than one element in teh set, there are several lengths, therefore:
        if len(set(num_entries)) != 1: 
            raise Exception (f'Columns in the same table must be of the same length, current lengths: {num_entries}')
        
        # Now that all lengths are the same, find number of rows through a column, by iterating through it
        num_rows = len(next(iter(self.columns.values()))) 
        new_table = {col: [] for col in self.columns}

        for i in range(num_rows):
            # Extract the row, we are currently considering
            row = {col: vals[i] for col, vals in self.columns.items()}

            # if none of the values in the row are NA or a given filter param, proceed
            if not any(v is NA or v == value for v in row.values()):
                # then paste it into our new_table
                for col, v in row.items():
                    new_table[col].append(v)
    
        return new_table

    # number - number at 50% of column 
    def median(self, column):
        col_len = len(self.columns[column])
        if col_len % 2:
            # length is uneven, return the exact middle element
            return self.columns[column][math.floor(col_len/2)]
        else:
            # length is even, return the average of the two elements around the middle
            halfway = math.floor(col_len/2)
            print("half ", halfway)
            value = (self.columns[column][halfway] + self.columns[column][halfway - 1]) / 2
            return value

    # number - number at 25% of column 
    def lowerq(self, column):
        # find the middle of the column
        col_len = len(self.columns[column])
        mid_idx = math.floor(col_len/2)
        # using the middle, find the lower half and its length
        lower_half_array = self.columns[column][:mid_idx]
        lower_len = len(lower_half_array)

        if lower_len % 2:
            # length is uneven, return the exact middle element
            return lower_half_array[math.floor(lower_len/2)]
        else:
            # length is even, return the average of the two elements around the middle
            quarterway = math.floor(lower_len/2)
            value = (lower_half_array[quarterway] + lower_half_array[quarterway - 1]) / 2
            return value

    # number - number at 75% og column 
    def upperq(self, column):
        # find the middle of the column
        col_len = len(self.columns[column])
        mid_idx = math.floor(col_len/2)
        # using the middle, find the upper half and its length
        # if col_len is odd, skip median element - even otherwise, then no median to skip
        if col_len % 2:
            upper_half_array = self.columns[column][mid_idx + 1:]
        else:
            upper_half_array = self.columns[column][mid_idx:]
        upper_len = len(upper_half_array)

        if upper_len % 2:
            # length is uneven, return the exact middle element
            return upper_half_array[math.floor(upper_len/2)]
        else:
            # length is even, return the average of the two elements around the middle
            quarterway = math.floor(upper_len/2)
            value = (upper_half_array[quarterway] + upper_half_array[quarterway - 1]) / 2
            return value

    # var - minimum value in column
    def min(self, column):
        col = self.columns[column]
        return min(col)

    # var - maximum value in column
    def max(self, column):
        col = self.columns[column]
        return max(col)

    # var - numeral difference from min to max value
    def span(self, column):
        col = self.columns[column]
        return max(col) - min(col)
    
    # tbl - appends a given array to the table, wlong with the given name
    def append(self, key, array):
        new_table = dict(self.columns)
        print("table ", key)
        new_table.update({key : array})
        
        return new_table

    # tbl - removes a given column from the table
    def remove(self, column):
        new_table = {}
        for col in self.columns:
            if col == column:
                pass
            else:
                new_table.update({col : self.columns[col]})
        return new_table