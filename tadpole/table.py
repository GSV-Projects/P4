import math
import pandas as pd
import urllib.request
import os
import copy
from lark import Token
from tadpole.utils.NAliteral import NA
from tadpole.utils.exceptions import TadpoleException
from urllib.parse import urlparse
from tabulate import tabulate

class Table():
    def __init__(self, columns):
        self.columns = columns
    
    def __str__(self):
        return tabulate(self.columns, headers="keys", tablefmt="fancy_outline")
    
    # Auxiliary function to get line number in case of exception
    def get_pos(self, node):
        # Token has the attribute "line" - See Lark token documentation
        if isinstance(node, Token):
            return node.line

        # If its not a token but tree, go through tree until a token is found to get line
        if hasattr(node, "children"):
            for child in node.children:
                line = self.get_pos(child)
                if line is not None:
                    return line

    # Method that reads from a URL and saves it in the table object
    # Returns: 'tbl'
    def read(self, path):
        if (self.is_url(path)): # If path leads to URL, call function that reads from URL
            df = self.read_from_url(path)
        else: # Else, read from filepath
            df = self.read_from_file(path)

        # Save the CSV columns wise to the columns of the object, and return
        self.columns = df.to_dict(orient="list")
        # Insert our NA_literal for missing values
        self.clean_values()
        return self
    
    # Reads exactly like above, with the added functionality 
    #   of filling out NA values based on surrounding values.
    # Returns: 'tbl'
    def read_fill(self, path):
        if (self.is_url(path)): 
            self._validate_url(path)
            df = self.read_from_url(path)
        else:
            df = self.read_from_file(path)

        # Only change made, pandas' ffill and bfill take care of filling NA values
        df = df.ffill().bfill()

        self.columns = df.to_dict(orient="list")
        self.clean_values()
        return self
    
    def read_from_url(self, url):
        self._validate_url(url)

        # Check if the CSV has headers for each column
        header_peek = pd.read_csv(url, nrows=1, header=None) # Read csv
        first_row = header_peek.iloc[0].tolist() # First row, should hold string of headers
        has_header = all(isinstance(v, (str)) for v in first_row) # Boolean, does all entries have a header?
        if has_header:
            df = pd.read_csv(url)
        else: # If columns have no header, create customs in col1, col2... format
            df = pd.read_csv(url, header=None)
            df.columns = [f"col{i+1}" for i in range(len(df.columns))]
        
        # Return pandas dataframe
        return df
    
    # Function that reads CSV with pandas library from a filepath
    def read_from_file(self, path):
        self._validate_filepath(path)

        header_peek = pd.read_csv(path, nrows=1, header=None)
        first_row = header_peek.iloc[0].tolist()
        has_header = all(isinstance(v, str) for v in first_row)

        if has_header:
            df = pd.read_csv(path)
        else:
            df = pd.read_csv(path, header=None)
            df.columns = [f"col{i+1}" for i in range(len(df.columns))]

        return df
        
    # Helper function to check if the parsed string is a URL
    # Returns: boolean
    def is_url(self, url):
        # Use urlparse library which segments the segment into URL chunks
        result = urlparse(url)
        
        # If it contains any of these strings, it is a URL
        return result.scheme in ("http", "https", "ftp")
    
    # Loops through each column and checks whether a value is NA
    # Returns: 'tbl'
    def clean_values(self):
        for column in self.columns:
            self.columns[column] = [self.replace_nan(v) for v in self.columns[column]]

        return self

    # Replaces missing values with our own literal 'NA'
    # Returns: NA 
    def replace_nan(self, value):
        if value in ('nan', 'NaN', 'na', 'NAN', 'NA', None, '', 'N/A') or value != value:  # value != value catches float NaN
            return NA
        
        return value
    
    # Returns a column with NA values replaced with the given value
    # Returns: array 
    def replace_na_values(self, column, value):
        self._validate_column(column)

        col = self.columns[column]
        col_type = next((type(v) for v in col if v != NA), None)

        if not isinstance(value, col_type):
            raise TadpoleException(f"Column '{column}' expects values of type '{col_type.__name__}', but received '{type(value).__name__}'")
        
        new_col = [value if v == NA else v for v in col]
        self.columns[column] = new_col

        return Table(self.columns)
    
    # Rename the key of a given column
    # Returns: 'tbl'
    def rename(self, column, key):
        self._validate_column(column)
        self._validate_key(key)
    
        if column not in self.columns:
            raise TadpoleException(f"Column '{column}' does not exist")
        
        new_table = copy.deepcopy(self.columns)
        new_table = {
            key if k == column else k: v for k, v in new_table.items()}
        
        return Table(new_table)
    
    # Appends a given array to the table, with the given name
    # Returns: 'tbl'
    def append(self, array, key = None):
        self._validate_key(key)
        self._validate_uniform()
        self._validate_length(array)
    
        new_table = dict(self.columns)
        if key is None:
            # Get amount of cols, and make new name "colx" where x is the nr of the new col
            key = len(self.columns)
            new_table.update({f'col{key + 1}' : array})
        else:
            # Else, use given name
            new_table.update({key : array})
        
        return Table(new_table)

    # Removes a given column from the table
    # Returns: 'tbl'
    def remove(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
    
        new_table = {}
        for col in self.columns:
            if col == column:
                pass
            else:
                new_table.update({col : self.columns[col]})

        return Table(new_table)
    
    # Manipulate existing column as given, 
    #   and append as a new column, possibly with a given key.
    # Returns: 'tbl'
    def mutate(self, column, expr, key = None):
        self._validate_expression(expr)
        self._validate_number(str(column), "mutate")
        if not key == None: self._validate_key(key)
    
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
        
        return Table(new_table)

    # Returns the cleaned version of the same table, excluding the rows with NA,
    #   but including those with the given value or fulfilling an expression for *all columns*.
    # Returns: 'tbl'
    def filter_all(self, param = None):
        # Reroute param as either a value or an expr,
        #   as only one of either can be called at a time.
        expr = None
        value = None
        if callable(param): expr = param # Param is callable if evaluator dot rule deems it a lambda expression
        else: value = param

        self._validate_uniform()
        if not expr == None : self._validate_expression(expr, True)
        
        # Find number of rows through a column, by iterating through it
        num_rows = len(next(iter(self.columns.values()))) 
        new_table = {col: [] for col in self.columns}

        for i in range(num_rows):
            # Extract the row, we are currently considering
            row = {col: vals[i] for col, vals in self.columns.items()}

            # If any of the values in the row are NA, goto next i
            if any(v is NA for v in row.values()):
                continue

            # If the value of the column matches the given value, append row
            if any(v == value for v in row.values()):
                for col, v in row.items():
                    new_table[col].append(v)
            
            # If an expr is given, and expr(row) returns True, goto next i
            if expr is not None and expr(row):
                for col, v in row.items():
                    new_table[col].append(v)
            
            # If no expr or value is given to be filtered out, append row.
            if value is None and expr is None:
                for col, v in row.items():
                    new_table[col].append(v)
    
        return Table(new_table)
    
    # Returns the cleaned version of the same table,
    #   excluding the rows with NA or a given value for a *given column*.
    # Returns: 'tbl'
    def filter_col(self, column, param = None):
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time.
        expr = None
        value = None
        if callable(param): expr = param # Param is callable if evaluator dot rule deems it a lambda expression
        else: value = param

        self._validate_column(column)
        self._validate_uniform()
        if not expr == None : self._validate_expression(expr, True)
        
        # Find number of rows through a column, by iterating through it
        num_rows = len(next(iter(self.columns.values()))) 
        new_table = {col: [] for col in self.columns}

        for i in range(num_rows):
            # Extract the row, we are currently considering
            row = {col: vals[i] for col, vals in self.columns.items()}

            # If the values in the row is NA, goto next i
            if row[column] is NA:
                continue

            # If a value was given and equal to the value in the given column for current row, append row 
            if value is not None and row[column] == value:
                for col, v in row.items():
                    new_table[col].append(v)
            
            # If an expr is given, and expr(row) evaluates to true, append row
            if expr is not None and expr(row): # expr(row) is a lambda, returning a bool. NB: It is a lamba function if the param is an expression.
                for col, v in row.items():
                    new_table[col].append(v)
            
            # If no expr or value is given to be filtered out, append row.
            if value is None and expr is None:
                for col, v in row.items():
                    new_table[col].append(v)

        return Table(new_table)
    
    # Given a column and index, returns the given cell
    # Returns: int / float / str / bool
    def cell(self, column, index):
        self._validate_table()
        self._validate_column(column)
    
        # Adjust index to indexing from 1
        index = index - 1
        col = self.columns[column]
        if index < 0 or index > len(col)-1:
            raise TadpoleException(f'Index: {index+1} out of bounds, must be between 1 and {len(col)}')
        
        # Return entry in cell of given column
        return col[index]
    
    # Returns the first row in the table
    # Returns: 'tbl'
    def first_row(self):
        self._validate_table()

        row = {col: vals[0] for col, vals in self.columns.items()}

        return Table(row)

    # Returns the last row in the table
    # Returns: 'tbl'
    def last_row(self):
        self._validate_table()

        row = {col: vals[-1] for col, vals in self.columns.items()}

        return Table(row)
    
    # Returns the row given from the index
    # Returns: 'tbl'
    def get_row(self, index):
        self._validate_table()
        
        # Ensure given 'index' parameter is an integer
        if not isinstance(index, int):
            raise TadpoleException(f'Given index must be an integer, was given {index}')
        
        # Adjust to 0-based indexing
        index = index - 1
        
        # Get amount of rows
        num_rows = len(next(iter(self.columns.values())))
        if index < 0 or index >= num_rows:
            raise TadpoleException(f'Index {index + 1} is out of bounds for table with {num_rows} rows')
        
        row = {col: [vals[index]] for col, vals in self.columns.items()}

        return Table(row)
    
    # Sort whole table from one column, 
    #   numerically for numbers or alphabetically for strings.
    # Returns: 'tbl'
    def sort(self, column, o = None):
        self._validate_column(column)
        self._validate_not_empty(column)
        decr_keys = ('decr', 'decrease', 'd')
        if o not in decr_keys and o != None:
            raise TadpoleException(f'Final parameter declares use of decreasing order, possible keys: "decr", "decrease" or "d" but received: {o}')
        
        new_table = copy.deepcopy(self.columns)
        col = new_table[column]

        # Uses Python 'sorted' which takes the key 'lambda' to ensure it is sorted by values, not indecies
        if(o in decr_keys):
            # Decreasing order
            sorted_indices = sorted(range(len(col)), key=lambda i: col[i], reverse=True)
        else: 
            # Increasing order
            sorted_indices = sorted(range(len(col)), key=lambda i: col[i])
     
        # Rebuild the table in new order
        new = {k: [v[i] for i in sorted_indices] for k, v in new_table.items()}

        return Table(new)

    # Round a column to whole integers and return the whole
    # Returns: 'tbl'
    def round_table(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "roundtable", True)

        col = self.columns[column]
        new_columns = dict(self.columns)
        new_columns[column] = [round(v) if v != NA else v for v in col]
        print("new_columns: ", type(Table(new_columns)))

        return Table(new_columns)       
         
    # array - Given a column, returns an array of the column sorted.
    #   Sorted numerically for numbers and alphabetically for strings.
    def sort_col(self, column,  o = None):
        self._validate_column(column)
        self._validate_not_empty(column)

        decr_keys = ('decr', 'decrease', 'd')
        if o not in decr_keys and o != None:
            raise TadpoleException(f'Final parameter declares use of decreasing order, possible keys: "decr", "decrease" or "d" but received: {o}')
    
        if(o in decr_keys):
            # Decreasing order
            return sorted(self.columns[column], reverse=True)
        else: 
            # Increasing order
            return sorted(self.columns[column])

    # Rounds a column and returns it as an array
    # Returns: array
    def round_col(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "roundcol", True)

        col = self.columns[column]
        rounded_col = []
        rounded_col = [round(v) if v != NA else v for v in col]

        return rounded_col
    
    # Returns the first column of a table
    # Returns: array 
    def first_col(self):
        self._validate_table()

        key_list = list(self.columns.keys())
        first = key_list[0]

        return self.columns[first]

    # Returns the last column of a table
    # Returns: array 
    def last_col(self):
        self._validate_table()
    
        key_list = list(self.columns.keys())
        last = key_list[len(key_list) - 1]

        return self.columns[last]
    
        # Returns a column requested by string name
    # Returns: array 
    def get_col(self, column):
        self._validate_table()
        self._validate_column(column)
    
        col = self.columns[column]

        return col
    
    # Returns array of all keys in a table
    # Returns: array
    def keys(self):
        self._validate_table()
    
        keys = []
        for column in self.columns:
            keys.append(column)

        return keys

    # Returns the length of a given column / number of rows in a table
    # Returns: int
    def len_col(self, column):
        self._validate_column(column)
    
        return len(self.columns[column])
    
    # Returns the first element in a column of the table 
    # Returns: int / float / str / bool
    def head(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
    
        col = self.columns[column]

        return col[0]
    
    # Returns the last element in a column of the table 
    # Returns: int / float / str / bool
    def tail(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)

        col = self.columns[column]
        last = len(col) - 1

        return col[last]
    
    # number - Returns the mean of all values in a given column
    # Returns: number
    def mean(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "mean")
    
        col = self.columns[column]

        return sum(col) / len(col)

    # Total sum of all elements in column
    # Returns: float
    def sum(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "sum")

        col = self.columns[column]

        return sum(col)
    
    # How often some value occurs within a column
    # Returns: float
    def frequency(self, column, param):
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time.
        expr = None
        value = None
        if callable(param): expr = param
        else: value = param

        self._validate_column(column)
        if not expr == None: self._validate_expression(expr, True)

        count = 0

        for v in self.columns[column]:
            # If expression was used, increment for each qualifying element.
            #   Pass the expression as a dictinoary to accomodate the Eval_dot in the interpreter.
            if expr is not None and expr({column: v}): count += 1 
            # If value was used, increment for each element that fulfills
            elif expr is None and v == value: count += 1 

        return count
    
    # Number at 50% of column 
    # Returns: float
    def median(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "median")
    
        col_len = len(self.columns[column])
        if col_len % 2:
            # Length is uneven, return the exact middle element
            return self.columns[column][math.floor(col_len/2)]
        else:
            # Length is even, return the average of the two elements around the middle
            halfway = math.floor(col_len/2)
            value = (self.columns[column][halfway] + self.columns[column][halfway - 1]) / 2

            return value

    # Number at 25% of column 
    # Returns: float 
    def lowerq(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "lowerq")
    
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

    # Number at 75% og column 
    # Returns: float
    def upperq(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "upperq")
    
        # find the middle of the column
        col_len = len(self.columns[column])
        mid_idx = math.floor(col_len/2)
        # Using the middle, find the upper half and its length.
        #   If col_len is odd, skip median element - even otherwise, then no median to skip.
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

    # Minimum value in column
    # Returns: float
    def min(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "min")
    
        col = self.columns[column]

        return min(col)

    # Maximum value in column
    # Returns: float
    def max(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "max")
    
        col = self.columns[column]

        return max(col)

    # Numeral difference from min to max value
    # Returns: float
    def range(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "span")
    
        col = self.columns[column]

        return max(col) - min(col)
    
    # Returns the value of the squared deviation from the mean
    # Returns: float
    def variance(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "variance")
    
        # Get values and intialise array for differences in mean and elements
        col = self.columns[column]
        mean = self.mean(column)
        deviations = []

        # For each column, square the difference.
        #   The sum of all these is the variance.
        for val in col:
            deviations.append((val - mean) ** 2)

        return sum(deviations) / len(col)
    
    # The average deviation from the mean
    # Returns: float
    def std_dev(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "stddev")

        # Get the variance, and return the sqrt (the std dev)
        variance = self.variance(column)

        return math.sqrt(variance)
    
    # --- ERROR HANDLING --- #
    
    # Ensure the column exists in the table
    def _validate_column(self, column):
        if column not in self.columns:
            raise TadpoleException(f'Column "{column}" does not exist in table. Available columns: {list(self.columns.keys())}')
        
    # Ensure table is not empty
    def _validate_table(self):
        if not self.columns:
            raise TadpoleException(f'Cannot find keys of columns, as table is empty')

    # Ensure column in not empty or all NA
    def _validate_not_empty(self, column):
        col = self.columns[column]
        # Check if col is [], None or only contains NA
        if not col or all(cell is NA for cell in col):
            raise TadpoleException(f'Column {column} is empty or only consists of {NA}')
    
    # Ensure the column only contains numbers
    def _validate_number(self, column, method, passNA = None):
        col = self.columns[column]
        # Check for NA specifically
        if (not all(c != NA for c in col)) and passNA != True:
            raise TadpoleException(f'Column {column} may not contain {NA} values to use function {method}') 
        # Check that theyre all numbers
        if not all(isinstance(c, (int, float)) for c in col):
            raise TadpoleException(f'Column {column} must consist only of integers or floats to use function {method}') 
        
    # Ensure all columns in a table are the same length
    def _validate_uniform(self):
        # Make array of lengths of columns, then check if they're all the same
        num_entries = [len(vals) for vals in self.columns.values()] 
        # set() method turns array into set. If there are more than 
        #   one element in the set, there are several lengths, therefore:
        if len(set(num_entries)) != 1: 
            raise TadpoleException (f'Columns in the same table must be of the same length, current lengths: {num_entries}')
        
    # Ensures the array sent is the same length as the columns of the table
    def _validate_length(self, array):
        # Get key to index and get length of a column
        keys = self.keys()
        column_entries = len(self.columns[keys[0]])
        array_entries = len(array)

        # If the column and array do not have matching lengths, throw an error
        if column_entries != array_entries:
            raise TadpoleException (f'Column must be of the same length as in the table, current lengths: {column_entries} : {array_entries}')

    # Ensure the expression sent is viable and returns a boolean
    def _validate_expression(self, expr, is_bool = None):
        # Check if the lambda can even be called
        if not callable(expr):
            raise TadpoleException(f"Expected a callable function/expression, got {type(expr).__name__}")
        
        # Set up the first row which entry is NOT NA and try calling the function on the given row
        row = {col: next((v for v in vals if v is not NA), None) for col, vals in self.columns.items()}
        try:
            result = expr(row)
        except TadpoleException as e:
            raise TadpoleException(f"Expression raised an error when called: {e}")    
        
        # Case for frequency and filters, that expects the expr to return a bool.
        #   Other functions that call this, where is_bool = None, may evaluate to other types than bool.
        if is_bool and not isinstance(result, bool):
            raise Exception(f"Expression must return a boolean, got {type(result).__name__}")

    # Ensure key name is a valid identifier
    def _validate_key(self, key):
        if not key.isidentifier():
            raise Exception(f'Attempted to use an invalid key, {key}, for column')
        if key in self.columns:
            raise Exception(f'Key: {key} already exists in this table')
    
    # Ensure URL is viable and working
    def _validate_url(self, url):
        if url == "":
            raise Exception("URL cannot be empty")
        try: # Establish connection to check validity of URL
            urllib.request.urlopen(url, timeout=5) 
        except urllib.error.URLError as e:
            raise Exception(f"Incorrect URL: '{url}") # If error occurs, URL is incorrect
        
    # Ensure filepath is viable
    def _validate_filepath(self, path):
        if path == "":
            raise Exception("Path cannot be empty")
        # Use 'os' library to check that a filepath leads to a file and not a directory
        if not os.path.isfile(path):
            raise Exception(f"No file found at path: '{path}'")
