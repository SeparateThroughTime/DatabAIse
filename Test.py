from pandas import DataFrame
import pandas

first = """{
    "1": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2] FROM [Tabelle1];", "text": false},
    "2": {"statement": "SELECT [Auflistung aller Spalten] FROM [Tabelle1];", "text": false},
    "3": {"statement": "SELECT [Tabelle1].[Spalte1] FROM [Tabelle1];", "text": true},
    "4": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2] FROM [Tabelle1];", "text": true},
    "5": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2], [Tabelle1].[Spalte3] FROM [Tabelle1];", "text": true},
    "6": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2], [Tabelle1].[Spalte3], [Tabelle1].[Spalte4] FROM [Tabelle1].[Tabelle1];", "text": true}
}"""

second = """{
    "1": {"statement": "SELECT [Tabelle].[Spalte1], [Tabelle1].[Spalte2] FROM [Tabelle1];", "text": false},
    "2": {"statement": "SELECT [Auflistung aller Spalten] FROM [Tabelle1] join t2 and do stuff;", "text": false},
    "3": {"statement": "SELECT [Tabelle1].[Spalte1] FROM [Tabelle1];", "text": true},
    "4": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2] FROM [Tabelle1];", "text": true},
    "5": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2], [Tabelle1].[Spalte3] FROM [Tabelle1];", "text": false},
    "6": {"statement": "SELECT [Tabelle1].[Spalte1], [Tabelle1].[Spalte2], [Tabelle1].[Spalte3], [Tabelle1].[Spalte4] FROM [Tabelle1].[Tabelle1];", "text": true}
}"""

print(DataFrame.compare(pandas.read_json(first), pandas.read_json(second), 1).to_string())
print(DataFrame.compare(pandas.read_json(first), pandas.read_json(second), 0).to_string())