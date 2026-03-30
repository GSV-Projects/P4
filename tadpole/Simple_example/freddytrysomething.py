import csv as csv

class dataframe: #infer types, juster kolonner så de er lige lange
    def __init__(self, data):
        self.data = data

    def read(self, filename):
        with open(filename, mode ='r') as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                print(lines)


df = dataframe(20)

mydict = {
    "make" : ["Toyota", "honda"],
    "model" : ["civic", None],
    "year" : [2002, "2021"]
}

#print(mydict)

data = '2002'

