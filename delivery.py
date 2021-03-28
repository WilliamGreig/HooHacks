# William Greig - wpg6zmk
# HooHacks 2021
#  RUNK RUNNERS  #
import googlemaps
import re
from twilio.rest import Client


#this is an optimized delivery system

#uses Google Cloud mapping to find optimal route

#an order is the main operation within the program -- it controls when people are provided the actual delivery service
class Order:
    API_KEY = "AIzaSyCRPwmVNsS29-A8w15_8t3bMqTfSBjyHEo"
    gmaps = googlemaps.Client(key=API_KEY)

    def __init__(self, time, products, address, name, phone_number, payment_option):
        self.time = time
        #products/snacks ordered
        self.products = products
        self.address = address
        self.name = name
        self.phone_number = phone_number
        self.payment_option = payment_option
        self.distanceMat = self.distanceMatrix()
        self.distance = self.distanceMat[0]
        self.approximate_delivery_time = self.distanceMat[1]

    #the time for an order is dependent on a few factors:
        #1.) distance between "home base" and the address
        #2.) concurrent orders / load-bearing on deliverers
    #this uses a Google Maps Distance Matrix API

    def distanceMatrix(self):
        #because I'm operating out of 357 Dillard, Charlottesville VA -- that will be the address that I shall use
        #feasbily, we could use lat. and long. of the deliverers (if mobile) and have their addresses be updated automatically
        #however, that's kinda hard to implement in 24hrs
        my_dist = self.gmaps.distance_matrix('357 Dillard Charlottesville VA', self.address, mode="walking")['rows'][0]['elements'][0]
        #distance stored in km
        distance = round(int(my_dist['distance']['value']) / 1000, 2)
        duration = round(int(my_dist['duration']['value']) / 60, 2)
        return (distance, duration)

    #string representation of an order -- dev purposes
    def __str__(self):
        string1 = "     " + self.name + " (" + str(self.phone_number) + ") ordered: " + "\n"
        string2 = "     " + self.products
        return string1 + string2

    #equals method to compare orders to one another
    def __eq__(self, other):
        #sketchy method to compare orders - but it heuristically works
        if other.time == self.time and self.name == other.name:
            return True
        return False

    def calculateTotalPayment(self, database):
        price = 0
        for product in database.product_list:
            #heuristic way to analyze the string of products
            #kinda tired so not the best but gets the job done -- will refactor eventually
            if product.name in self.products:
                price += float(product.cost)
        return price

#Deliverers represent the people who are actively delivering food for the company
class Deliverer:
    load_weight = 2
    proximity_weight = 1

    def __init__(self, name):
        # at any one time, a person should have a list of outgoing orders
        self.name = name[0]
        self.orders = []

        #this is a work in progress - I would like to develop a system to track our deliverers to ensure they're on the right track!
        self.location = 0
        #I would need to launch a mobile application to track their positions -- for future development

    def addOrder(self, order):
        self.orders.append(order)

    def removeOrder(self, order):
        self.orders.remove(order)

    def priority(self):
        #the lower the priority, the better (more free)
        return self.load_weight * len(self.orders) + self.proximity_weight * self.locational_orders()

    def locational_orders(self):
        #approximate distance traveled between orders
        #--> the higher the number, the worse (because it technically means longer delivery times)
        approx_dist = 0
        for x in self.orders:
            approx_dist += x.distance
        return approx_dist

    def calcPriorOrderTime(self, order):
        time_sum = int(order.approximate_delivery_time)
        for orders in self.orders:
            if orders != order:
                time_sum += int(orders.approximate_delivery_time)
        return time_sum

    def route(self):
        route = ""
        old = "357 Dillard Charlottesville VA"
        for x in self.orders:
            new = x.address

        return route

#a delivery system is the overarching system that dictates and controls the processes
class DeliverySystem:
    account_sid = "AC022c08bee628caada3c82ae493341465"
    auth_token = "276075f3565cd6a00deb751393214266"
    twilio_client = Client(account_sid, auth_token)


    #when launching the delivery system, we need the on-shift delivery people
    def __init__(self, onshift_deliverers):
        self.deliverers = []
        if not onshift_deliverers:
            print('No data found.')
        else:
            for row in onshift_deliverers:
                #create a product list
                self.deliverers.append(Deliverer(row))
        self.outgoing_orders = []

    # get the best / free delivery for the next operation (order)
    def getBestDeliv(self):
        #for this algorithm, we shall weight the best delivery with load-bearing (amount of outgoing orders) and proximity basis
        bestDeliv = self.deliverers[0]
        for x in self.deliverers:
            if x.priority() < bestDeliv.priority():
                bestDeliv = x
        return bestDeliv

    #printing delivery system as a whole -- dev purposes
    def printDeliverySystem(self):
        for deliverers in self.deliverers:
            print(deliverers.name + ":")
            for orders in deliverers.orders:
                print(orders)

    #assigns a given order to the "best" fit for an order
    def assignOrder(self, order):
        self.getBestDeliv().addOrder(order)
        self.outgoing_orders.append(order)

    #GREAT FUNCTION!!
    def sendNotification(self, order, database):
        #I don't want to pay a million bajillion dollars for a Twilio subscription... at least not yet
        #I'm using the trial version which only allows registered and manually verified numbers
        #with a subscription, I think it would be easy to scale to other numbers that aren't registered yet!
        try:
            deliverer = self.findDeliverer(order)
            message = self.twilio_client.messages.create(
                body= "Your order has been confirmed. Your Runk Runner is "
                      + deliverer.name + ". Your snack delivery will be with you within " + str(round(deliverer.calcPriorOrderTime(order)) + 1) + " minutes."
                      + ". Your total is $" + str(order.calculateTotalPayment(database)) + ". Thank you for choosing Runk Runners.",
                #constant Twilio account number from which we send our message
                from_="+15312345711",
                #variable number - ONLY VERIFIED ACCOUNTS ON TWILIO (UPGRADE TO SEND OUT AGGREGATED)
                # to="+1" + str(order.phone_number)
            )
        except:
            # print(order.phone_number + " is not a valid phone number.")
            pass

    #set up -- assigns a load of orders before company runtime
    def assignOrders(self, orders):
        for x in orders:
            self.assignOrder(x)

    #finds the Deliverer in which an order was assigned
    def findDeliverer(self, order):
        for x in self.deliverers:
            for orders in x.orders:
                if order == orders:
                    return x
        return None

    #if the order exists, return true
    #otherwise, return false
    def existingOrder(self, order):
        for x in self.outgoing_orders:
            if x == order:
                return True
        return False

    #this 'checks' off an order and removes it from the queue of the Deliverer and on the deliverySystem
    def completeOrder(self, order):
        self.findDeliverer(order).removeOrder(order)
        self.outgoing_orders.remove(order)

    #create an order
    #if it already exists, don't make another
    def createOrder(self, raw_data):
        if raw_data == []:
            return None
        temp = Order(raw_data[0], raw_data[1], raw_data[2], raw_data[3], raw_data[4], raw_data[5])
        if self.existingOrder(temp) == False:
            return temp
        return None

    def updateOrders(self, order_values, database):
        for row in order_values:
            tempOrder = self.createOrder(row)
            #not already created
            if tempOrder is not None:
                #must also be a valid order (don't cut into negative stock)
                if database.validOrder(tempOrder) is True:
                    #we then can add to outgoing order!
                    self.assignOrder(tempOrder)
                    self.sendNotification(tempOrder, database)
                else:
                    print("invalid order")
        #read the orders page and append any that we don't have


