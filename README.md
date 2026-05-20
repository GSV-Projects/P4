# P4
## Collaborators

- Frederik Sperling Schacksen (https://github.com/FrederikSperling)
- Mathias Østerskov Kejser (https://github.com/GakkiOne)
- David Henning Bach (https://github.com/DrMachoo)
- Mads Møller Pedersen (https://github.com/MadsMoneyCrank)
- Victoria Myrup Pedersen (https://github.com/Venil0u)
- William Strandby Bauer (https://github.com/TheGingong)

## Introduction
Tadpole is a GPL designed for university students with little to no programming experience. The language consists of a parser/lexer, build with Lark, a type-checker and evaluator. Included in the language is a set of predefined functions for extracting and manipulating data from files in CSV format.

## How To Run The Program
To start coding in Tadpole, perform one of the following steps while in a virtual environment (venv):
```python
clone -> pip install -r requirements.txt -> python -m filename.tad 
clone -> pip install -e . -> tadpole filename.tad
pip install git+https://github.com/GSV-Projects/P4.git@"release_version" -> tadpole filename.tadvv
```
To run all tests in the program:
```python
pip install pytest
python -m pytest
```

## List of predefined functions
Below a list of all predefined functions for this iteration can be seen. These are called using the dot notation "." on a table. For each, the return type of the function is indicated:
```python
    "read" :        ('tbl'),    
    "readfill" :    ('tbl'),
    "replaceNA" :   ('tbl'),    
    "rename" :      ('tbl'),    
    "append" :      ('tbl'),    
    "remove" :      ('tbl'),    
    "mutate" :      ('tbl'),    
    "filterall" :   ('tbl'),
    "filtercol" :   ('tbl'),
    "firstrow" :    ('tbl'),
    "lastrow" :     ('tbl'),
    "getrow" :      ('tbl'),
    "sort" :        ('tbl'),    
    "round" :       ('tbl'),  
    "sortcol" :     ([]),     
    "roundcol" :    ([]),       
    "getcol" :      ([]),       
    "getfirst" :    ([]),       
    "getlast" :     ([]),       
    "keys" :        ([]),       
    "length" :      (int),     
    "cell" :        ((int, float, str, bool)),
    "head" :        ((int, float, str, bool)),
    "tail" :        ((int, float, str, bool)),
    "mean" :        (float),      
    "sum" :         (float),    
    "frequency" :   (int),    
    "median" :      (float),    
    "lowerq" :      (float),    
    "upperq" :      (float),    
    "min" :         (float),    
    "max" :         (float),    
    "span" :        (float),    
    "variance":     (float),    
    "stddev":       (float)
```
