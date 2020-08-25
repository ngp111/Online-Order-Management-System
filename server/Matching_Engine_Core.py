#!/usr/bin/env python
# coding: utf-8


import heapq


class Stock:
    
    def __init__(self, ID):
        
        self.ID = ID
        self.buy_orders = list()
        self.sell_orders = list()


class Order:
    def __init__(self,user_id, order_id, stock_id, quantity, price, timestamp, all_orders_index):
        self.user_id = user_id
        self.order_id = order_id
        self.stock_id = stock_id
        self.quantity = quantity
        self.price = price
        self.timestamp = timestamp
        self.status = "pending"
        self.all_orders_index = all_orders_index

    def compare_timestamp(self, ts1, ts2) :

        
        time1 = ts1[0:4] + ts1[4:6] + ts1[6:8] + ts1[9:11] + ts1[12:14] + ts1[15:17] + ts1[18:20]
        time2 = ts2[0:4] + ts2[4:6] + ts2[6:8] + ts2[9:11] + ts2[12:14] + ts2[15:17] + ts2[18:20]
        time1 = int(time1)
        time2 = int(time2)
        if (time1 < time2) : 
            return True
        else :
            return False             
        
    #Comparetor function for heap
    def __lt__(self, other):
        if (self.price > other.price):
            return False
        elif (self.price < other.price):
            return True
        else:
            if self.compare_timestamp(self.timestamp , other.timestamp):
                return True
            else :
                return False
            
    def order_executed(self):
        self.status = "executed"
        
    def set_price(self, price):
        self.price = price
        
    def set_quantity(self, quantity):
        self.quantity = quantity
        
    def order_cancelled(self):
        self.status = "cancelled"


class Transaction:
    def __init__(self, transaction_id, buyer_id, seller_id, security_id, quantity, price):
        self.transaction_id = transaction_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.security_id = security_id
        self.quantity = quantity
        self.price = price

#Initialize the stocks
amzn = Stock("amzn")
apple = Stock("apple")
google = Stock("google")

#Add the stocks to the stock_list
stock_list = [amzn, apple, google]

#A list containing all the orders placed till date
all_orders = list()

#Function to find the stock in the stock list and return it
def get_stock(stock_list, stock_ID):

    i = 0
    flag = 0
    for i in range(len(stock_list)):
        if stock_list[i].ID == stock_ID:
            flag = 1
            break
    
    if flag == 0 :
        return None
    return stock_list[i]

#Function to find the order in the stock lists and change the price and quantity
def search_stock_and_change(stock, order_id, price, quantity):
    
    flag = 0
    
    for order in stock.buy_orders:
        if order.order_id == order_id:
            order.set_price(-price)
            order.set_quantity(quantity)
            flag = 1
            break
            
    if (flag == 0):
        for order in stock.sell_orders:
            if order.order_id == order_id:
                order.set_price(price)
                order.set_quantity(quantity)
                break


#Search for the order in stock lists and remove it
def search_stock_and_remove(stock, order_id):
    
    flag = 0
    
    for order in stock.buy_orders:
        if order.order_id == order_id:
            stock.buy_orders.remove(order)
            flag = 1
            break
            
    if (flag == 0):
        for order in stock.sell_orders:
            if order.order_id == order_id:
                stock.sell_orders.remove(order)
                break


#Return the index of the order, if present, in the all_orders list. If not present, return -1
def search_for_order(all_orders, order_id):

    i = 0
    flag = 0
    for i in range(len(all_orders)):
        if all_orders[i].order_id == order_id:
            flag = 1
            break
            
    if (flag == 0):
        return None
    else:
        return all_orders[i]

#Match the order with another order. The arguments are as defined in the document
def match(argument):

    #Return list,  which contains all the response dictionaries
    ret_list = list()

    #Extract relevant information
    order_id = argument["Order ID"]
    order_type = argument["Order type"]
    return_order_id = argument["Return Order ID"]

    #If it is not cancel order request
    if (order_id != 3) :
        stock_id = argument["Security ID"]

    #Get the stock from the list of stocks
    stock = get_stock(stock_list, stock_id)

    if (stock == None) :
        return ret_list

    #If the order is not a cancel order
    if (order_type != 3):

        #Extract relevant information
        user_id = argument["User ID"]
        quantity = argument["Order Qty"]
        offer_price = argument["Price"]
        time_stamp = argument["Time stamp"]
    
        #Get the list of buy orders corresponding to the stock
        buy_orders = stock.buy_orders

        #Get the list of sell orders corresponding to the stock
        sell_orders = stock.sell_orders

    #If the order is of type "New order bid" or "New offer ask"
    if (order_type == 0 or order_type == 1):
        
        #If the order is a bid        
        if (order_type == 0) :
            
            #Make a new buy order       
            order = Order(user_id, order_id, stock_id, quantity, -offer_price, time_stamp, len(all_orders))
            
            #Append the order to the buy orders list
            buy_orders.append(order)
            
        else:
            
            #Make a new sell order            
            order = Order(user_id, order_id, stock_id, quantity, offer_price, time_stamp, len(all_orders))
            
            #Append the order to the sell orders list
            sell_orders.append(order)
            
        #The dictionary corresponding to acceptance of the buy / sell order is appended to the return list
        ret_list.append({"Response" : 0, "Order ID" : return_order_id})
        
        #Append the order to the global list of all orders
        all_orders.append(order)
        
    #Order is for amending an already placed order
    elif (order_type == 2):
        
        #Search for the order in the list of all orders. If not present, return None        
        order = search_for_order(all_orders, order_id)
        
        #If order is found
        if (order is not None):
        
            #If the status of the order is executed
            if (order.status == "executed") :
                
                #Append the dictionary containing report for rejection to the return list
                ret_list.append({"Response" : 4, "Order ID" : return_order_id, "Reason" : "Order has been already executed, no changes possible"})
                
                #Return the return list. Nothing else to be done
                return ret_list
            
            #If the status of the order is cancelled
            elif (order.status == "cancelled") :

                #Append the dictionary containing report for rejection to the return list
                ret_list.append({"Response" : 4, "Order ID" : return_order_id, "Reason" : "Order has already been cancelled, no more changes possible"})

                #Return the return list. Nothing else to be done
                return ret_list

            #If the order is still valid
            else :
                
                #Set the new price for the order
                order.set_price(-offer_price)
                
                #Set the new quantity for the order
                order.set_quantity(quantity)
                
                #Change the respective values from the lists of the corresponding stock
                search_stock_and_change(stock, order_id, offer_price, quantity)
                
                #Append the dictionary containing report for successful amendment of the order to the return list
                ret_list.append({"Response" : 1, "Order ID" : order_id})

        #If the order was not found
        else :

            #Append the dictionary containing report for order not found to return list
            ret_list.append({"Response" : 4, "Order ID" : return_order_id, "Reason" : "Order with given ID does not exist"})

            #Return the return list. Nothing else to be done
            return ret_list

    #If the order type is cancel order 
    else:
        
        #Get the required order
        order = search_for_order(all_orders, order_id)

        #If the order exists
        if (order is not None):
        
            #If the order has already been executed
            if (order.status == "executed"):
                
                #Append the dictionar containing report for already already executed to return list
                ret_list.append({"Response" : 5, "Order ID" : return_order_id})
                
                #Return the return list. Nothing else to be done
                return ret_list
            
            else :
                
                #Search for the order in the stock lists and remove the order from them
                search_stock_and_remove(stock, order_id)
                
                #Cancel the order
                order.order_cancelled()
                
                #Append the dictionary containing report for order successfully cancelled
                ret_list.append({"Response" : 2, "Order ID" : return_order_id})
                
                #Return the return list. Nothing else to be done
                return ret_list

        #If order is not found
        else :
            
            #Append the dictionary containing report for order not found
            ret_list.append({"Response" : 2, "Order ID" : return_order_id, "Reason" : "Order with given ID does not exist"})

            #Return the return list. Nothing else to be done
            return ret_list
        
    #If any of the lists are empty, do nothing
    if (len(buy_orders) == 0 or len(sell_orders) == 0):
        
        #Return the return list. Nothing else to be done
        return ret_list
            
    #Convert the buy orders list and sell orders list into heaps
    heapq.heapify(buy_orders)
    heapq.heapify(sell_orders)

    #Get the top of both the heaps. These are to be matched for a transaction to be successful
    top_of_buy = heapq.heappop(buy_orders)
    top_of_buy.price = -top_of_buy.price
    top_of_sell = heapq.heappop(sell_orders)

    #Keep looping while a transaction is possible
    while(top_of_buy.price >= top_of_sell.price):

        #If the buy quantity is less than the sell quantity
        if (top_of_buy.quantity < top_of_sell.quantity):

            #Modify the quantity of top of sell
            top_of_sell.quantity = top_of_sell.quantity - top_of_buy.quantity

            #Append the dictionary containing report for fill order executed to return list
            ret_list.append({"Response" : 6, "Order ID" : top_of_buy.order_id, "Security ID" : stock_id, "Order Qty" : top_of_buy.quantity, "Price" : top_of_sell.price})
            
            #Append the dictionary containing report for partial fill order executed to return list
            ret_list.append({"Response" : 7, "Order ID" : top_of_sell.order_id, "Security ID" : stock_id, "Order Qty" : top_of_buy.quantity, "Price" : top_of_sell.price})
            
            #Update the all_orders list
            all_orders[top_of_sell.all_orders_index].quantity = top_of_sell.quantity
            
            #Update the all_orders list            
            all_orders[top_of_buy.all_orders_index].order_executed()
            
            #If more buy orders exist
            if (len(buy_orders) != 0) :
                
                #Get the next top of heap
                top_of_buy = heapq.heappop(buy_orders)
                top_of_buy.price = -top_of_buy.price
                
                
            #If no more buy orders
            else : 
                
                #Push the top of sell orders back into the heap
                heapq.heappush(sell_orders, top_of_sell)
                        
                #Return the return list. Nothing else to be done
                return ret_list
            
        #If buy quantity is greater than sell quantity
        elif(top_of_buy.quantity > top_of_sell.quantity):
            
            #Update the quantity of top of buy
            top_of_buy.quantity = top_of_buy.quantity - top_of_sell.quantity
            
            #Append the dictionary containing report for fill order executed to return list
            ret_list.append({"Response" : 6, "Order ID" : top_of_sell.order_id, "Security ID" : stock_id, "Order Qty" : top_of_sell.quantity, "Price" : top_of_sell.price})
            
            #Append the dictionary containing report for partial fill order executed to return list
            ret_list.append({"Response" : 7, "Order ID" : top_of_buy.order_id, "Security ID" : stock_id, "Order Qty" : top_of_sell.quantity, "Price" : top_of_sell.price})
            
            #Update the all_orders list
            all_orders[top_of_buy.all_orders_index].quantity = top_of_buy.quantity
            
            #Update the all_orders list
            all_orders[top_of_sell.all_orders_index].order_executed()
            
            #If more sell orders exist
            if (len(sell_orders) != 0):
            
                #Get the new top of heap
                top_of_sell = heapq.heappop(sell_orders)
                
            #If no more sell orders
            else:
                
                #Push the top of buy orders back into the heap
                top_of_buy.price = -top_of_buy.price
                heapq.heappush(buy_orders, top_of_buy)
                
                #Return the return list. Nothing else to be done        
                return ret_list

        #If buy and sell quantity is equal    
        else:
            
            #Append the dictionary containing report for fill order executed to return list
            ret_list.append({"Response" : 6, "Order ID" : top_of_sell.order_id, "Security ID" : stock_id, "Order Qty" : top_of_sell.quantity, "Price" : top_of_sell.price})
            
            #Append the dictionary containing report for fill order executed to return list
            ret_list.append({"Response" : 6, "Order ID" : top_of_buy.order_id, "Security ID" : stock_id, "Order Qty" : top_of_buy.quantity, "Price" : top_of_sell.price})
            
            #Update the all_orders list
            all_orders[top_of_buy.all_orders_index].order_executed()

            #Update the all_orders list
            all_orders[top_of_sell.all_orders_index].order_executed()
            
            #If more buy and sell orders exist
            if (len(sell_orders) != 0 and len(buy_orders) != 0):
            
                #Get next top of buy heap
                top_of_buy = heapq.heappop(buy_orders)
                
                top_of_buy.price = -top_of_buy.price

                #Get next to pf sell heap
                top_of_sell = heapq.heappop(sell_orders)
                
            #If no more buy orders exist
            elif (len(buy_orders) == 0):
                
                #Push top of sell heap back into heap
                heapq.heappush(sell_orders, top_of_sell)
                
                #Return the return list. Nothing else to be done
                return ret_list
                        
            #If no more sell orders exist
            elif (len(sell_orders) == 0):
                
                #Push top of buy heap back into heap                
                top_of_buy.price = -top_of_buy.price
                heapq.heappush(buy_orders, top_of_buy)
                
                #Return the return list. Nothing else to be done        
                return ret_list
                        
            #If no more buy and sell orders exist
            else :
                
                #Return the return list. Nothing else to be done
                return ret_list

    #Push top of buy heap back into heap     
    top_of_buy.price = -top_of_buy.price
    heapq.heappush(buy_orders, top_of_buy)

    #Push top of sell heap back into heap
    heapq.heappush(sell_orders, top_of_sell)
    
    #Return the return list. Owari da.
    return ret_list

#Returns the list of top n open orders in both the buy and sell lists of the required stock
def give_top_n(required_stock, n):
    
    push_list = list()

    #Return list, contains dictionaries, each containing information about an order
    return_list = list()
            
    #Get the required stock
    stock = get_stock(stock_list, required_stock)
    
    #Get the buy orders and sell orders lists of the stock
    buy_orders_list = stock.buy_orders
    sell_orders_list = stock.sell_orders
    
    #Get the lengths of both the lists
    no_of_buy = len(buy_orders_list)
    no_of_sell = len(sell_orders_list)
    
    '''
    no_of_buy_pops : number of elements to be popped from the buy heap
    no_of_sell_pops : number of elements to be popped from the sell heap
    no_of_sell_nulls : number of elements to be appended as NULL
    no_of_sell_nulls : number of elements to be appended as NULL

    '''

    if (n <= no_of_buy):
        no_of_buy_pops = n
        no_of_buy_nulls = 0

    else:
        no_of_buy_pops = no_of_buy
        no_of_buy_nulls = n - no_of_buy
        
    if (n <= no_of_sell):
        no_of_sell_pops = n
        no_of_sell_nulls = 0
    
    else:
        no_of_sell_pops = no_of_sell
        no_of_sell_nulls = n - no_of_sell
    
    #Get the top no_of_buy_pops elements from buy heap
    for _ in range(no_of_buy_pops):

        #Get the top of buy heap
        temp = heapq.heappop(buy_orders_list)

        push_list.append(temp)

        #Dictionary to store the order
        Dict = dict()

        #Setting the required fields
        Dict["Quantity"] = temp.quantity
        Dict["Price"] = -temp.price
        Dict["Type"] = "0"
        Dict["Order ID"] = temp.order_id

        #Append the order dictionary to the return list
        return_list.append(Dict)

        for order in push_list:

            heapq.heappush(buy_orders_list, order)

        push_list = list()            
        
    #Get the top no_of_sell_pops elements from sell heap
    for _ in range(no_of_sell_pops):

        #Get the top of sell heap
        temp = heapq.heappop(sell_orders_list)

        push_list.append(temp)

        #Dictionary to store the order
        Dict = dict()

        #Setting the required fields
        Dict["Quantity"] = temp.quantity
        Dict["Price"] = temp.price
        Dict["Type"] = "1"
        Dict["Order ID"] = temp.order_id

        #Append the order dictionary to the return list
        return_list.append(Dict)

        for order in push_list:
        
            heapq.heappush(sell_orders_list, order)


    #Return the return list
    return return_list
