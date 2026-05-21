# P4
## Collaborators

- Frederik Sperling Schacksen (https://github.com/FrederikSperling)
- Mathias Østerskov Kejser (https://github.com/GakkiOne)
- David Henning Bach (https://github.com/DrMachoo)
- Mads Møller Pedersen (https://github.com/MadsMoneyCrank)
- Victoria Myrup Pedersen (https://github.com/Venil0u)
- William Strandby Bauer (https://github.com/TheGingong)

## Introduction
Tadpole is a DSL designed for university students with little to no programming experience. The language consists of a parser/lexer, build with Lark, a type-checker and evaluator. Included in the language is a set of predefined functions for extracting and manipulating data from files in CSV format.

## How To Run The Program
To start coding in Tadpole, perform one of the following steps while in a virtual environment (venv):
```python
clone -> pip install -r requirements.txt -> python -m filename.tad 
clone -> pip install -e . -> tadpole filename.tad
pip install git+https://github.com/GSV-Projects/P4.git@"release_version" -> tadpole filename.tad
```
To run all tests in the program:
```python
pip install pytest
python -m pytest
```

## List of predefined functions
Below a list of all predefined functions for this iteration can be seen. These are called using the dot notation "." on a table. For each, the return type of the function is indicated. The first parameter for each function is table, which is automatically sent when the dot "." notation is used on a table:
| Function Name | Description | Parameter | Returns |
|---|---|---|---|
| read | Function that reads from either a URL or filepath to a file in CSV format and inserts into a table. | Table, URL/filepath | Table |
| readfill | Function that reads from either a URL or filepath to a file in CSV format and inserts into a table, replacing empty values with the NA literal. | Table, URL/filepath | Table |
| replaceNA | Function that replaces all NA literals with a given value. | Table, Column, Value | Array |
| rename | Function that renames a given column in a table. | Table, Column, Name | Table |
| append | Function that, given an array, appends it to an existing table as a column, with a name if a key is given. | Table, Array, **Name** | Table |
| remove | Function that, given a column, removes it from the table. | Table, Column | Table |
| mutate | Function that, given an expression containing a column, `+`, `-`, `*`, `/`, `^` and a value, appends a new column of the result with a name if a key is given. | Table, Column, Expression | Table |
| filterall | Function that, given no parameter, will filter out any rows containing any NA values. If given some parameter that is an expression or value, will filter out any rows that do not fulfill the expression or are not equal to the parameter. | Table, **Parameter** | Table |
| filtercol | Function that, given a column and no parameter, will filter out any rows whose entries for that column are NA. If given a column and some parameter, that is an expression or a value, will filter out any rows whose entries for that column do not fulfill the expression or are not equal to the parameter. | Table, Column, **Parameter** | Table |
| firstrow | Function that returns the first row, which consists of all columns with only the first cell. | Table | Table |
| lastrow | Function that returns the last row, which consists of all columns with only the last cell. | Table | Table |
| getrow | Function that, given an index, returns the given row, consisting of all columns and their cell on the given index. | Table, Index | Table |
| sort | Function that sorts a whole table in increasing order from one column, rearranging all columns so entries are still aligned. If third parameter is given as `d`, `decr`, `decreasing` or `True`, it sorts in decreasing order. | Table, Column, **Order** | Table |
| sort | Function that given a column returns a sorted array of the column in increasing order. If third parameter is given as `d`, `decr`, `decreasing` or `True`, it sorts in decreasing order. | Table, Column, **Order** | Array |
| round | Function that rounds a column to whole integers and returns the whole table. | Table, Column | Table |
| roundcol | Function that rounds a column and returns it as an array. | Table, Column | Array |
| getcol | Function that given a column name, returns the column as an array. | Table, Column | Array |
| getfirst | Function that returns the first column of a table as an array. | Table | Array |
| getlast | Function that returns the last column of a table as an array. | Table | Array |
| keys | Function that returns an array of all key values in a table. | Table | Array |
| length | Function that returns an integer indicating the length of columns, also given the amount of rows in a table. | Table, Column | Integer |
| cell | Function that returns the entry in a cell given a column and index. | Table, Column, Index | Integer / Float / String / Bool |
| head | Function that given a column returns the first entry. | Table, Column | Integer / Float / String / Bool |
| tail | Function that given a column returns the last entry. | Table, Column | Integer / Float / String / Bool |
| mean | Function that given a column of numbers, returns the mean value. | Table, Column | Float |
| sum | Function that given a column of numbers, returns the sum of all values. | Table, Column | Float |
| frequency | Function that, given a column and some parameter, that is an expression or a value, will count the frequency of entries in that column which fulfill the expression or are equal to the value. | Table, Column, Parameter | Integer |
| median | Function that returns the value at index 50% of a column. | Table, Column | Float |
| lowerq | Function that returns the value at index 25% of a column. | Table, Column | Float |
| upperq | Function that returns the value at index 75% of a column. | Table, Column | Float |
| min | Function that given a column of numbers returns the smallest value. | Table, Column | Float |
| max | Function that given a column of numbers returns the biggest value. | Table, Column | Float |
| span | Function that given a column of numbers returns the difference from the smallest and biggest entry. | Table, Column | Float |
| variance | Function that returns the squared deviation from the mean of a column of numbers. | Table, Column | Float |
| stddev | Function that returns the average deviation from the mean value. | Table, Column | Float |
