from tadpole.table import Table, NA


def test_replaceNA():
    # Arrange
    t = Table({"col1": [1.0, NA, 3.0]})
    
    # Act
    result = t.replaceNAvalues("col1", 2.0)
    
    # Assert
    assert result == [1.0, 2.0, 3.0]