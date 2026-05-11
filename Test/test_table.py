from tadpole.table import Table, NA

def test_read():
    #Arrange 
    t = Table(None)

    #Act
    result = t.read("https://raw.githubusercontent.com/GSV-Projects/P4/refs/heads/main/tadpole/Simple_example/cooldata.csv")

    #Assert
    assert result == {"make": ["Toyota", "Honda", "Ford", "Tesla", "BMW"], "model": ["Camry", "Civic", "Mustang", "Model 3", "X5"], "year": [2022, 2021, 2023, 2023, 2022]}
    
def test_getcol():
    #Arrange
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.getcol("col1")

    #Assert
    assert result == [1.0, NA, 3.0]
    
def test_getfirst():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.getfirst()

    #Assert
    assert result == [1.0, NA, 3.0]
    
def test_getlast():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.getlast()

    #Assert
    assert result == ["red", "green", "yellow"]

def test_mean():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})
    
    #Act
    result = t.mean("col1")

    #Assert
    assert result == 3

def test_head():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.head("col1")

    #Assert
    assert result == 1.0

def test_tail():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.tail("col2")

    #Assert
    assert result == "yellow"

def test_sum():
    #Arrange
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sum("col1")

    #Assert
    assert result == 9

#def test_frequency(): # vent med
    ##Arrange 
    #t = Table({"col1": [1.0, 5, 3.0, 1.0, 7, 1.0], "col2": ["red", "green", "yellow", "blue", "pink", "rosa"]})
#
    ##Act
    #result = t.frequency("col1", col1 < 4)
#
    ##Assert
    #assert result == 3

def test_filter(): # vent med
    pass
    #Arrange 

    #Act

    #Assert

def test_median():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.median("col1")

    #Assert
    assert result == 5

def test_lowerq():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.lowerq("col1")

    #Assert
    assert result == 1.0

def test_upperq():
    #Arrange 
    t = Table({"col1": [1.0, 5, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.upperq("col1")

    #Assert
    assert result == 3.0

def test_min():
    #Arrange 
    t = Table({"col1": [7.0, 1.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.min("col1")

    #Assert
    assert result == 1.0

def test_max():
    #Arrange
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.max("col1")

    #Assert
    assert result == 7.0


def test_span():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.span("col1")

    #Assert
    assert result == 6

def test_rename():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.rename("col1", "newname")

    #Assert
    assert result.columns == {"newname": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]}

def test_sort():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sort("col1")

    #Assert
    assert result.columns == {"col1": [1.0, 3.0, 7.0], "col2": ["red", "yellow", "green"]}

def test_sort_desc():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sort("col1", "d")

    #Assert
    assert result.columns == {"col1": [7.0, 3.0, 1.0], "col2": ["green", "yellow", "red"]}

def test_sortcol():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sortcol("col1")

    #Assert
    assert result == [1.0, 3.0, 7.0]

def test_sortcol_desc():
    #Arrange 
    t = Table({"col1": [1.0, 7.0, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.sortcol("col1", "d")

    #Assert
    assert result == [7.0, 3.0, 1.0]

def test_round():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.roundtable("col1")

    #Assert
    assert result.columns ==  {"col1": [1, 8, 4], "col2": ["red", "green", "yellow"]}

def test_roundcol():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.roundcol("col1")

    #Assert
    assert result == [1, 8, 4]

def test_keys():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"], "col3": [1,2,3]})

    #Act
    result = t.keys()

    #Assert
    assert result == ["col1","col2","col3"]
    

def test_lencol():
    #Arrange 
    t = Table({"col1": [1.4, 7.5, 3.6], "col2": ["red", "green", "yellow"], "col3": [1,2,3]})

    #Act
    result = t.lenCol("col1")

    #Assert
    assert result == 3
    
def test_replaceNAvalues():
    pass
    # Arrange
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})
    
    # Act
    result = t.replaceNAvalues("col1", 2.0)
    
    # Assert
    assert result == [1.0, 2.0, 3.0]

def test_append():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})
    new_col = [1,2,3]

    #Act
    result = t.append(new_col, "col3")

    #Assert
    assert result == {"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"], "col3": [1,2,3]}
    
def test_remove():
    #Arrange 
    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})

    #Act
    result = t.remove("col2")

    #Assert
    assert result == {"col1": [1.0, NA, 3.0]}

#def test_mutate():
#    #Arrange 
#    t = Table({"col1": [1.0, NA, 3.0], "col2": ["red", "green", "yellow"]})
#
#    #Act
#    result = t.mutate()
#
#    #Assert tbc
    