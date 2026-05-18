from tadpole.table import Table, NA
# Tests for all predefined functions in the Table class, to ensure they work as intended.

# Function that tests whether a given url successfully parses data to the table type.
def test_read():
    #Arrange 
    t = Table(None)

    #Act
    result = t.read("https://raw.githubusercontent.com/GSV-Projects/P4/refs/heads/main/Test/read_test.csv")

    #Assert
    expected = {"maker": ["Toyota", "Honda", "Ford", "Tesla", "BMW"], "model": ["Camry", "Civic", "Mustang", "Model 3", "X5"], "year": [2022, 2021, 2023, 2023, 2022]}
    assert result.columns == expected

def test_read_from_file():
    #Arrange 
    t = Table(None)

    #Act
    result = t.read("Test/read_test.csv")

    #Assert
    expected = {"maker": ["Toyota", "Honda", "Ford", "Tesla", "BMW"], "model": ["Camry", "Civic", "Mustang", "Model 3", "X5"], "year": [2022, 2021, 2023, 2023, 2022]}
    assert result.columns == expected
    
# Test for getter function that returns a column as an array.
def test_getcol():
    #Arrange
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.get_col("col1")

    #Assert
    assert result == [1.0, NA, 3.0]
    
# Function that returns the first column of a given table.
def test_firstcol():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.first_col()

    #Assert
    assert result == [1.0, NA, 3.0]
    
# Function that returns the last column of a given table.
def test_lastcol():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.last_col()

    #Assert
    assert result == ["red", "green", "yellow"]

# Function that given a column, returns the mean as a float/integer.
def test_mean():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})
    
    #Act
    result = t.mean("col1")

    #Assert
    assert result == 3

# Function that returns the first element of a given column.
def test_head():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.head("col1")

    #Assert
    assert result == 1.0

# Function that returns the last element of a given column.
def test_tail():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.tail("col2")

    #Assert
    assert result == "yellow"

# Function that returns a sum of a column in the shape of a float/integer.
def test_sum():
    #Arrange
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sum("col1")

    #Assert
    assert result == 9

# Function that counts the amount of times a given value occurs in a column.
def test_frequency_value():
    # Arrange
    t = Table({"col1": [1.0, 2.0, 3.0, 1.0]})

    # Act
    result = t.frequency("col1", lambda row: row["col1"] == 1)

    # Assert
    assert result == 2

# Function that counts the amount of times a given value occurs in a column, through an expression.
def test_frequency():
    # Arrange
    t = Table({"col1": [1.0, 2.0, 3.0, 1.0]})

    # Act
    result = t.frequency("col1", lambda row: row["col1"] > 2)

    # Assert
    assert result == 1

# Function that filters values given an expression, out of the column.
def test_filter():
    # Arrange
    t = Table({"col1": [1.0, 2.0, 3.0, 1.0]})

    # Act
    result = t.filter(lambda row: row["col1"] == 1)

    # Assert
    assert result == {"col1": [2.0, 3.0]}

# Test for whether the median is returned.
def test_median():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.median("col1")

    #Assert
    assert result == 5

# Test for whether the lower quartile is returned.
def test_lowerq():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.lowerq("col1")

    #Assert
    assert result == 1.0

# Test for whether the upper quartile is returned.
def test_upperq():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.upperq("col1")

    #Assert
    assert result == 3.0

# Test whether the function successfully returns the lowest value of a column.
def test_min():
    #Arrange 
    t = Table({"col1": [7.0, 1.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.min("col1")

    #Assert
    assert result == 1.0

# Test whether the function successfully returns the highest value of a column.
def test_max():
    #Arrange
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.max("col1")

    #Assert
    assert result == 7.0

# Test whether the function successfully returns the range between highest and lowest value.
def range():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.range("col1")

    #Assert
    assert result == 6

# Tests whether rename successfully renames a column in a given table.
def test_rename():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.rename("col1", "newname")

    #Assert
    assert result.columns == {"newname": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]}

# Checks whether sort successfully sorts a table depending on a column, in ascending order.
def test_sort():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sort("col1")

    #Assert
    assert result.columns == {"col1": [1.0, 3.0, 7.0], "col2": ["red", "yellow", "green"]}

# Checks whether sort successfully sorts a table depending on a column, in descending order.
def test_sort_desc():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sort("col1", "d")

    #Assert
    assert result.columns == {"col1": [7.0, 3.0, 1.0], "col2": ["green", "yellow", "red"]}

# Checks whether sort successfully sorts a column, in ascending order.
def test_sortcol():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sort_col("col1")

    #Assert
    assert result == [1.0, 3.0, 7.0]

# Checks whether sort successfully sorts a column, in ascending order.
def test_sortcol_desc():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sort_col("col1", "d")

    #Assert
    assert result == [7.0, 3.0, 1.0]

# Ensures round successfully returns a table with columns rounded to whole numbers.
def test_round():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.round_table("col1")

    #Assert
    assert result.columns ==  {"col1": [1, 8, 4], "col2": ["red", "green", "yellow"]}

# Ensures roundcol returns a column rounded.
def test_roundcol():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.round_col("col1")

    #Assert
    assert result == [1, 8, 4]

# Ensures an array of table keys is returned.
def test_keys():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "colors": ["red", "green", "yellow"], "col3": [1,2,3]})

    #Act
    result = t.keys()

    #Assert
    assert result == ["col1","colors","col3"]
    
# Function that ensures lencol returns the right length of a column.
def test_lencol():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"], "col3": [1,2,3]})

    #Act
    result = t.len_col("col1")

    #Assert
    assert result == 3
    
# Function that ensures NA values are replaced with given value.
def test_replaceNAvalues():
    pass
    # Arrange
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})
    
    # Act
    result = t.replace_na_values("col1", 2.0)
    
    # Assert
    assert result == [1.0, 2.0, 3.0]

# Ensures append successfully appends a column to an existing table.
def test_append():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})
    new_col = [1,2,3]

    #Act
    result = t.append(new_col, "col3")

    #Assert
    assert result == {"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"], "col3": [1,2,3]}
    
# Ensures remove successfully removes a column from an existing table.
def test_remove():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.remove("col2")

    #Assert
    assert result == {"col1": [1.0, NA, 3.0]}

# Ensures mutate successfully creates a new column from the given expression/lambda expression.
def test_mutate():
    # Arrange
    t = Table({"col1": [1.0, 2.0, 3.0], "col2": [4.0, 5.0, 6.0]})

    # Act
    result = t.mutate("col1", lambda row: row["col1"] + 2, "sum")

    # Assert
    assert result == {
        "col1": [1.0, 2.0, 3.0],
        "col2": [4.0, 5.0, 6.0],
        "sum": [3.0, 4.0, 5.0]
    }

# Ensures stddev returns the right standard deviation.
def test_stddev():
    # Arrange
    t = Table({"col1": [1.0, 2.0, 3.0, 4.0, 5.0, 10.0]})

    # Act
    result = t.std_dev("col1")

    # Assert
    assert result == 2.91070819942883