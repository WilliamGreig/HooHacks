from __future__ import print_function
import googlemaps
import re

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]

API_KEY = "AIzaSyCRPwmVNsS29-A8w15_8t3bMqTfSBjyHEo"

gmaps = googlemaps.Client(key=API_KEY)
my_dist = gmaps.distance_matrix('357 Dillard Charlottesville VA', 'Washington Street Charlottesville VA', mode="walking")['rows'][0]['elements'][0]
print(my_dist)
print(my_dist['duration']['text'])

string = "Beef Jerky ($2.5), Protein Bar ($1), Mixed Nuts ($1), Banana ($0.50)"
#helper method to process the gross string given by the Spreadsheet for products
string = re.sub('[1234567890().$,]', '', string)
list_name = ["Beef Jerky",
"Trail Mix",
"Yogurt",
"Protein Bar",
"Mixed Nuts",
"Banana",
"Apple"]
for x in list_name:
    if x in string:
        pass

print(string)

# #TODO: return an array containing the product names in the string
# def cleanProductOrder(strong):
#     arr = []
#     index = 0
#     while (strong.find("(", index, len(strong)) != -1):
#         temp = strong[index:strong.find("(", index)]
#         arr.append(strong[index:strong.find("(", index)])
#         index = strong.find(")", strong.find("(", index))
#     actArr = []
#     for x in arr:
#         print(x)
#         actArr(re.sub('[),]', '', x))
#     return actArr

# for x in cleanProductOrder(string):
#     print(x)
