# William Greig - wpg6zmk
# HooHacks 2021
#  RUNK RUNNERS  #

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient import discovery
from HooHacks2021.delivery import DeliverySystem

#first, let's set up a database - we're gonna use Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]

API_KEY = "AIzaSyCRPwmVNsS29-A8w15_8t3bMqTfSBjyHEo"

SPREADSHEET_ID = '1Rj-WbitWO1xyLriXawHa94vYr6jXqALO9qnA1ttEJCo'
SAMPLE_RANGE_NAME = 'Product Page!A2:C'


global creds

#next, let's create some items so we can track and do easy manipulations
class Product:
    def __init__(self, row):
        self.name = row[0]
        self.supply = row[1]
        self.cost = row[2]

    def __str__(self):
        return self.name + " ($" + self.cost + ")" + ": " + self.supply

    #this is a row representation needed to append and update a Google spreadsheet
    def dataRep(self):
        return [self.name, self.supply, self.cost]

#next, let's create a localized database to track the products and whatnot
class BackendDatabase:

    def __init__(self, values):
        #this is just the contents of the spreadsheet -- potentially could implement faster data structure?
        self.product_list = []
        if not values:
            print('No data found.')
        else:
            for row in values:
                #create a product list
                self.product_list.append(Product(row))

    #returns Product from given list of Products given a Product name
    def findProduct(self, name):
        for x in self.product_list:
            if x.name == name:
                return x
        return None

    #we can add products of the spreadsheet
    def addProduct(self, name, supply, cost):
        #if the product already exists, just add to the supply
        temp = self.findProduct(name)
        if temp == None:
            self.product_list.append(Product(name, supply, cost))
        else:
            temp.supply = temp.supply + supply

    #prints database for developer (me!)
    def printDatabase(self):
        for x in self.product_list:
            print(x)

    #this method updates itself using the current information
    def update(self):
        service = discovery.build('sheets', 'v4', credentials=creds)
        data = []
        #indexing starts at 2 for this program
        index = 2
        for prod in self.product_list:
            data_range = "A" + str(index) + ":C" + str(index)
            temp_dict = {"range": data_range,
                         "values": [prod.dataRep()]}
            data.append(temp_dict)

        #create data request to post and update the spreadsheet using the data that we've created locally
        batch_update_values_request_body = {
              "data": data,
              "valueInputOption": "USER_ENTERED"
        }

        request = service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=batch_update_values_request_body)
        response = request.execute()
        #bonus cool points: integrate a Google Script to reupdate and reorganize --> use for website too

    def computeDelivery(self):
        pass

# Credit to: https://developers.google.com/sheets/api/quickstart/python?authuser=1

#this is the main structural loop for the server
"""
Functionally:
1.) sets up all necessary creditials for the spreadsheet
2.) creates the underlying data structures used to house data, organize workflow, and general operations
3.) loops through program to operate a company!
"""

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    global creds
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    #create the database
    database = BackendDatabase(values)

    #suggest the delivery people
    deliverySystem = DeliverySystem()
    database.printDatabase()


main()
