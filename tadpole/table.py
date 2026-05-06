from utils.NAliteral import NA
import math
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
        # Check if the URL is viable and working
        if not url != "":
            raise Exception("URL cannot be empty")
        try: # Establish connection to check validity of URL.
            urllib.request.urlopen(url, timeout=5) 
        except urllib.error.URLError as e:
            raise Exception(f"Incorrect URL: '{url}") # If error occurs, URL is incorrect
        
        # Check if the CSV has headers for each column
        header_peek = pd.read_csv(url, nrows=1, header=None) # Read csv
        first_row = header_peek.iloc[0].tolist() # First row, should hold string of headers
        has_header = all(isinstance(v, (str)) for v in first_row)
        if has_header:
            df = pd.read_csv(url)
        else:
            df = pd.read_csv(url, header=None)
            # If columns have no header, create customs in col1, col2... format
            df.columns = [f"col{i+1}" for i in range(len(df.columns))]

        # Save the CSV columns wise to the columns of the object, and return
        self.columns = df.to_dict(orient="list")
        self.cleanValues(self.columns)
        return self
    
    # tbl - loops through each column and checks whether a value is NA
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
        
    # array - Returns a column requested by string name
    def getcol(self, column):
        col = self.columns[column]
        return col
    
    # array - Returns the first column of a table
    def getfirst(self):
        key_list = list(self.columns.keys())
        first = key_list[0]
        return self.columns[first]

    # array - Returns the last column of a table
    def getlast(self):
        key_list = list(self.columns.keys())
        last = key_list[len(key_list) - 1]
        return self.columns[last]
    
    # number - Returns the mean of all values in a given column
    def mean(self, column):
        col = self.columns[column]
        return sum(col) / len(col)
    
    # var - Returns the first element in a column of the table 
    def head(self, column):
        col = self.columns[column]
        return col[0]
    
    # var - Returns the last element in a column of the table 
    def tail(self, column):
        col = self.columns[column]
        last = len(col) - 1
        return col[last]
    
    # dictionary - Returns the first row in the table
    def first(self):
        row = {col: vals[0] for col, vals in self.columns.items()}
        return row

    # dictionary - Returns the last row in the table
    def last(self):
        row = {col: vals[-1] for col, vals in self.columns.items()}
        return row

    # number - Total sum of all elements in column
    def sum(self, column):
        col = self.columns[column]
        if not all(isinstance(v, (int, float)) for v in col):
            raise Exception("Given type is not a number and cannot be summed")
        return sum(col)
    
    # number - How often some value occurs within a column - WIP
    def frequency(self, column, arg = None): 
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time
        expr = None
        value = None
        if callable(arg): expr = arg
        else: value = arg

        count = 0

        for v in self.columns[column]:
            # If expression was used, increment for each qualifying element
            #   Pass the expression as a dictinoary to accomodate the Eval_dot in the interpreter
            if expr is not None and expr({column: v}): count += 1 
            # If value was used, increment for each element that fulfills
            elif expr is None and v == value: count += 1 
        return count

    # tbl - Returns the cleaned versoin of the same table, excluding the row with NA or a given value
    def filter(self, arg = None): 
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time
        expr = None
        value = None
        if callable(arg): expr = arg
        else: value = arg

        # Make array of lengths of columns, then check if they're all the same
        num_entries = [len(vals) for vals in self.columns.values()] 

        # set() method turns array into set. 
        #   If there are more than one element in the set, there are several lengths, therefore:
        if len(set(num_entries)) != 1: 
            raise Exception (f'Columns in the same table must be of the same length, current lengths: {num_entries}')
        
        # Now that all lengths are the same, find number of rows through a column, by iterating through it
        num_rows = len(next(iter(self.columns.values()))) 
        new_table = {col: [] for col in self.columns}

        for i in range(num_rows):
            # Extract the row, we are currently considering
            row = {col: vals[i] for col, vals in self.columns.items()}

            # If any of the values in the row are NA or a given filter param, goto next i
            if any(v is NA or v == value for v in row.values()):
                continue
            # If an expr is given, and expr(row) returns False, goto next i
            if expr is not None and expr(row): # expr(row) is a lambda, returning a bool
                continue
            # Otherwise, all is good, paste row into our new_table
            for col, v in row.items():
                new_table[col].append(v)
    
        return new_table

    # number - Number at 50% of column 
    def median(self, column):
        col_len = len(self.columns[column])
        if col_len % 2:
            # Length is uneven, return the exact middle element
            return self.columns[column][math.floor(col_len/2)]
        else:
            # Length is even, return the average of the two elements around the middle
            halfway = math.floor(col_len/2)
            print("half ", halfway)
            value = (self.columns[column][halfway] + self.columns[column][halfway - 1]) / 2
            return value

    # number - Number at 25% of column 
    def lowerq(self, column):
        # Find the middle of the column
        col_len = len(self.columns[column])
        mid_idx = math.floor(col_len/2)
        # Using the middle, find the lower half and its length
        lower_half_array = self.columns[column][:mid_idx]
        lower_len = len(lower_half_array)

        if lower_len % 2:
            # Length is uneven, return the exact middle element
            return lower_half_array[math.floor(lower_len/2)]
        else:
            # Length is even, return the average of the two elements around the middle
            quarterway = math.floor(lower_len/2)
            value = (lower_half_array[quarterway] + lower_half_array[quarterway - 1]) / 2
            return value

    # number - Number at 75% og column 
    def upperq(self, column):
        # find the middle of the column
        col_len = len(self.columns[column])
        mid_idx = math.floor(col_len/2)
        # Using the middle, find the upper half and its length.
        #   If col_len is odd, skip median element - even otherwise, then no median to skip
        if col_len % 2:
            upper_half_array = self.columns[column][mid_idx + 1:]
        else:
            upper_half_array = self.columns[column][mid_idx:]
        upper_len = len(upper_half_array)

        if upper_len % 2:
            # Length is uneven, return the exact middle element
            return upper_half_array[math.floor(upper_len/2)]
        else:
            # Length is even, return the average of the two elements around the middle
            quarterway = math.floor(upper_len/2)
            value = (upper_half_array[quarterway] + upper_half_array[quarterway - 1]) / 2
            return value

    # var - Minimum value in column
    def min(self, column):
        col = self.columns[column]
        return min(col)

    # var - Maximum value in column
    def max(self, column):
        col = self.columns[column]
        return max(col)

    # var - Numeral difference from min to max value
    def span(self, column):
        col = self.columns[column]
        return max(col) - min(col)

    # table - round a column to whole integers
    def round(self, column):
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")
        col = self.columns[column]
    
        if not all(isinstance(v, (int, float)) for v in col):
            raise Exception(f"Column '{column}' must only consist of integers or floats")

        self.columns[column] = [round(v) for v in col]
        return self

    def roundcol(self, column):
        col = self.columns[column]
        sorted_col = [round(v) for v in col]
        return sorted_col
    
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
    def sort(self, column, o = None):
        col = self.columns[column]

        # Uses Python 'sorted' which takes the key 'lambda' to ensure it is sorted by values, not indecies
        if((o == 'decr') or (o == 'decrease') or (o == 'd') or (o == True)):
            # decreasing order
            sorted_indices = sorted(range(len(col)), key=lambda i: col[i], reverse=True)
        else: 
            # increasing order
            sorted_indices = sorted(range(len(col)), key=lambda i: col[i])
     
        # Rebuild the table in new order
        self.columns = {k: [v[i] for i in sorted_indices] for k, v in self.columns.items()}
        return self
        
    # array - given a column, returns an array of the column sorted
    # sorted numerically for numbers and alphabetically for strings.
    def sortcol(self, column):
        return sorted(self.columns[column])
    
    # tbl - Appends a given array to the table, wlong with the given name
    def append(self, array, key = None):
        new_table = dict(self.columns)
        if key is None:
            # Get amount of cols, and make new name "colx" where x is the nr of the new col
            key = len(self.columns)
            new_table.update({f'col{key + 1}' : array})
        else:
            # Else, use given name
            new_table.update({key : array})
        
        return new_table

    # tbl - Removes a given column from the table
    def remove(self, column):
        new_table = {}
        for col in self.columns:
            if col == column:
                pass
            else:
                new_table.update({col : self.columns[col]})
        return new_table
    
    # tbl - Manipulate existing column as given, and append as a new column, possibly with a given key
    def mutate(self, expr, key = None):
        new_table = dict(self.columns)
        num_rows = len(next(iter(self.columns.values())))
        new_col = []
        # For reach row we want, contruct the original rows, and call expr on them
        for i in range(num_rows):
            row = {col: vals[i] for col, vals in self.columns.items()}
            new_col.append(expr(row))

        # If no key was given, create a key "colx" where x is its number 
        if key is None:
            key = f"col{len(new_table) + 1}"
        # Otherwise it'll just use the given key
        new_table.update({key: new_col})
        
        return new_table
    
    # number - Returns the value of the squared deviation from the mean
    def variance(self, column):
        # Get values and intialise array for differences in mean and elements
        col = self.columns[column]
        mean = self.mean(column)
        deviations = []
        # For each column, square the difference. The sum of all these is the variance
        for val in col:
            deviations.append((val - mean) ** 2)

        return sum(deviations) / len(col)
    
    # number - The average deviation from the mean
    def stddev(self, column):
        # Get the variance, and return the sqrt (the std dev)
        variance = self.variance(column)

        return math.sqrt(variance)
    
    def fwdfill(self, column):
        col = self.columns[column]
        return col.ffill().bfill()
