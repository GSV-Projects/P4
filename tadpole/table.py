from tadpole.utils.NAliteral import NA
import math
import pandas as pd
import urllib.request
import copy
from tadpole.utils.NAliteral import NA

class Table():
    def __init__(self, columns):
        self.columns = columns
    
    def __repr__(self):
        return f"{self.columns}"

    # Method that reads from a URL and saves it in the table object
    # Returns: 'tbl'
    def read(self, url):
        self._validate_url
        
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
    
    # Reads exactly like above, with the added functionality 
    #   of filling out NA valies based on surrounding values.
    # Returns: 'tbl'
    def readfill(self, url):
        self._validate_url
        
        header_peek = pd.read_csv(url, nrows=1, header=None)
        first_row = header_peek.iloc[0].tolist() 
        has_header = all(isinstance(v, (str)) for v in first_row)
        if has_header:
            df = pd.read_csv(url)
        else:
            df = pd.read_csv(url, header=None)
            df.columns = [f"col{i+1}" for i in range(len(df.columns))]

        # only change made, pandas' ffill and bfill take care of filling NA values
        df = df.ffill().bfill()

        self.columns = df.to_dict(orient="list")
        self.cleanValues(self.columns)
        return self
    
    # Loops through each column and checks whether a value is NA
    # Returns: 'tbl'
    def cleanValues(self, columns):
        self._validate_column
        
        for column in columns:
            self.columns[column] = [self.replaceNaN(v) for v in self.columns[column]]
        return self

    # Replaces missing values with our own literal 'NA'
    # Returns: NA 
    def replaceNaN(self, value):
        if value in ('nan', 'NaN', 'na', 'NAN', 'NA', None, '', 'N/A') or value != value:  # value != value catches float NaN
            return NA
        return value
    
    # Returns a column with NA values replaced with the given value
    # Returns: array 
    def replaceNAvalues(self, column, value):
        self._validate_column(column)
        col = self.columns[column]
        col_type = next((type(v) for v in col if v != NA), None)
        if not isinstance(value, col_type):
            raise Exception(f"Type mismatch")
        new_col = [value if v == NA else v for v in col]
        return new_col
    
    # Rename the key of a given column
    # Returns: 'tbl'
    def rename(self, column, name):
        self._validate_column(column)
        self._validate_key(name)
    
        if column not in self.columns:
            raise Exception(f"Column '{column}' does not exist")
        new_table = copy.deepcopy(self.columns)
        new_table = {
            name if k == column else k: v 
            for k, v in new_table.items()}
        return Table(new_table)
    
    # Appends a given array to the table, with the given name
    # Returns: 'tbl'
    def append(self, array, key = None):
        self._validate_key(key)
        self._validate_uniform
    
        new_table = dict(self.columns)
        if key is None:
            # Get amount of cols, and make new name "colx" where x is the nr of the new col
            key = len(self.columns)
            new_table.update({f'col{key + 1}' : array})
        else:
            # Else, use given name
            new_table.update({key : array})
        
        return new_table

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
        return new_table
    
    # Manipulate existing column as given, 
    #   and append as a new column, possibly with a given key.
    # Returns: 'tbl'
    def mutate(self, expr, key = None):
        self._validate_expression(expr)
    
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

    # Returns the cleaned versoin of the same table, 
    #   excluding the rows with NA or a given value for *all columns*.
    # Returns: 'tbl'
    def filter(self, arg = None):
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time.
        expr = None
        value = None
        if callable(arg): expr = arg
        else: value = arg

        self._validate_uniform
        if not expr == None : self._validate_expression(expr, True)
        
        # Find number of rows through a column, by iterating through it
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
    
    # Returns the cleaned versoin of the same table,
    #   excluding the rows with NA or a given value for a *given column*.
    # Returns: 'tbl'
    def filtercol(self, column, arg = None):
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time.
        expr = None
        value = None
        if callable(arg): expr = arg
        else: value = arg

        self._validate_column(column)
        self._validate_uniform
        if not expr == None : self._validate_expression(expr, True)
        
        # Find number of rows through a column, by iterating through it
        num_rows = len(next(iter(self.columns.values()))) 
        new_table = {col: [] for col in self.columns}

        for i in range(num_rows):
            # Extract the row, we are currently considering
            row = {col: vals[i] for col, vals in self.columns.items()}

            # If any of the values in the row are NA or a given filter param, goto next i
            if any(v is NA for v in row.values()):
                continue
            # If a value was given and equal to the value in the given column for current row, goto next i 
            if value is not None and row[column] == value:
                continue
            # If an expr is given, and expr(row) returns False, goto next i
            if expr is not None and expr(row): # expr(row) is a lambda, returning a bool
                continue
            # Otherwise, all is good, paste row into our new_table
            for col, v in row.items():
                new_table[col].append(v)
    
        return new_table
    
    # Returns the first row in the table
    # Returns: 'tbl'
    def first(self):
        self._validate_table

        row = {col: vals[0] for col, vals in self.columns.items()}
        return row

    # Returns the last row in the table
    # Returns: 'tbl'
    def last(self):
        self._validate_table

        row = {col: vals[-1] for col, vals in self.columns.items()}
        return row
    
    # Sort whole table from one column, 
    #   numerically for numbers or alphabetically for strings.
    # Returns: 'tbl'
    def sort(self, column, o = None):
        self._validate_column(column)
        self._validate_not_empty(column)
        decr_keys = ('decr', 'decrease', 'd', True)
        if o not in decr_keys and o != None:
            raise Exception(f'Final parameter declares use of decreasing order, possible keys: "decr", "decrease", "d" or true, received: {o}')
        
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
    def roundtable(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "roundtable", True)

        col = self.columns[column]
        new_columns = dict(self.columns)
        new_columns[column] = [round(v) if v != NA else v for v in col]
        return Table(new_columns)       
         
    # Given a column, returns an array of the column sorted.
    #   Sorted numerically for numbers and alphabetically for strings.
    # Returns: array
    def sortcol(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
    
        return sorted(self.columns[column])

    # Rounds a column and returns it as an array
    # Returns: array
    def roundcol(self, column):
        self._validate_column(column)
        self._validate_not_empty(column)
        self._validate_number(column, "roundcol", True)

        col = self.columns[column]
        rounded_col = []
        rounded_col = [round(v) if v != NA else v for v in col]
        return rounded_col

    # Returns a column requested by string name
    # Returns: array 
    def getcol(self, column):
        self._validate_table
        self._validate_column(column)
    
        col = self.columns[column]
        return col
    
    # Returns the first column of a table
    # Returns: array 
    def getfirst(self):
        self._validate_table

        key_list = list(self.columns.keys())
        first = key_list[0]
        return self.columns[first]

    # Returns the last column of a table
    # Returns: array 
    def getlast(self):
        self._validate_table
    
        key_list = list(self.columns.keys())
        last = key_list[len(key_list) - 1]
        return self.columns[last]
    
    # Returns array of all keys in a table
    # Returns: array
    def keys(self):
        self._validate_table
    
        keys = []
        for column in self.columns:
            keys.append(column)

        return keys

    # Returns the length of a given column / number of rows in a table
    # Returns: int
    def lencol(self, column):
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
    def frequency(self, column, arg = None): # NOT WORKING - - - - - ! - ! - ! 
        # Reroute arg as either a value or an expr,
        #   as only one of either can be called at a time.
        expr = None
        value = None
        if callable(arg): expr = arg
        else: value = arg

        self._validate_key(column)
        self._validate_expression(expr, True)

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
    def span(self, column):
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
    def stddev(self, column):
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
            raise Exception(f'Column with key {column} does not exist in the given table')
        
    # Ensure table is not empty
    def _validate_table(self):
        if not self.columns:
            raise Exception(f'Cannot find keys of columns, as table is empty')

    # Ensure column in not empty or all NA
    def _validate_not_empty(self, column):
        col = self.columns[column]
        # Check if col is [], None or only contains NA
        if not col or all(cell is NA for cell in col):
            raise Exception(f'Column {column} is empty or only consists of {NA}')
    
    # Ensure the column only contains numbers
    def _validate_number(self, column, method, passNA = None):
        col = self.columns[column]
        # Check for NA specifically
        if (not all(c != NA for c in col)) and passNA != True:
            raise Exception(f'Column {column} may not contain {NA} values to use function {method}') 
        # Check that theyre all numbers
        if not all(isinstance(c, (int, float)) or NA for c in col):
            raise Exception(f'Column {column} must consist only of integers or floats to use function {method}') 
        
    def _validate_uniform(self):
        # Make array of lengths of columns, then check if they're all the same
        num_entries = [len(vals) for vals in self.columns.values()] 
        # set() method turns array into set. If there are more than 
        #   one element in the set, there are several lengths, therefore:
        if len(set(num_entries)) != 1: 
            raise Exception (f'Columns in the same table must be of the same length, current lengths: {num_entries}')

    def _validate_expression(self, expr, is_bool = None):
        # Check if the lambda can even be called
        if not callable(expr):
            raise Exception(f"Expected a callable function/expression, got {type(expr).__name__}")
        
        # Set up a row and try calling the function on the given row
        row = {col: vals[0] for col, vals in self.columns.items()}
        try:
            result = expr(row)
        except Exception as e:
            raise Exception(f"Expression raised an error when called: {e}")    
        
        # Case for frequency and filter, that exprest the expr to return a bool
        if is_bool and not isinstance(result, bool):
            raise Exception(f"Expression must return a boolean, got {type(result).__name__}")


    # Ensure key name is a valid identifier
    def _validate_key(self, key):
        if not key.isidentifier():
            raise Exception(f'Attempted to use an invalid key, {key}, for column')
    
    # Ensure URL is viable and working
    def _validate_url(self, url):
        if url == "":
            raise Exception("URL cannot be empty")
        try: # Establish connection to check validity of URL
            urllib.request.urlopen(url, timeout=5) 
        except urllib.error.URLError as e:
            raise Exception(f"Incorrect URL: '{url}") # If error occurs, URL is incorrect
