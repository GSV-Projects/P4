class NA_literal():
    def __repr__(self): #__repr__ Gør bare sådan at vores instans a klassen printes som NA i stedet for object#02... gør det bare pænere
        return "NA"

NA = NA_literal()

class NA_type():
    pass
na_type = NA_type()