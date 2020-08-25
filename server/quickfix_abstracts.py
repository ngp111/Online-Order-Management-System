import quickfix as fix
import quickfix44 as fix44
from Matching_Engine_Core import match, give_top_n

'''
This function returns a string value of the value of the tag needed.
Header and Trailer fields are to be checked separately as they are not retrieved in the getField()
'''
def getValue(fix_message, tag): 
    field = fix.StringField(tag)
    if(fix_message.isSetField(field)):
        return (str(fix_message.getField(tag)))
    elif(fix_message.getHeader().isSetField(field)):
        return (str(fix_message.getHeader().getField(tag)))
    elif(fix_message.getTrailer().isSetField(field)):
        return (str(fix_message.getTrailer().getField(tag)))
    else:
        return None


'''
match_and_return() calls match() function internally
It gets values that is required by the match() function storing it in a dictionary
match() is called
match() returns a list of dictionaries as specified in the API Return Document
It further converts these dicitonaries into a list of FIX messages which are to be sent to the target.
'''
def match_and_return(message):

    Dict = {}

    msg_type = getValue(message, 35)
    
    #New Order Single
    if (msg_type == "D"):

        Dict["Order ID"] = getValue(message, 11)

        Dict["Order type"] = int(getValue(message, 54)) - 1

        Dict["Security ID"] = getValue(message, 55)

        Dict["Order Qty"] = int(getValue(message, 38))

        Dict["Price"] = float(getValue(message, 44))

        Dict["Time stamp"] = getValue(message, 60)

        Dict["User ID"] = "COEPUSER"

        Dict["Return Order ID"] = Dict["Order ID"]

    #Order Amend request
    elif (msg_type == "G"):

        Dict["Order ID"] = getValue(message, 41)

        Dict["Order type"] = 2

        Dict["Order Qty"] = int(getValue(message, 38))

        Dict["Price"] = float(getValue(message, 44))

        Dict["Security ID"] = getValue(message, 55)

        Dict["Time stamp"] = getValue(message, 60)

        Dict["User ID"] = "COEPUSER"

        Dict["Return Order ID"] = getValue(message, 11)

    #Order Cancel Request
    elif (msg_type == "F"):

        Dict["Order ID"] = getValue(message, 41)

        Dict["Order type"] = 3

        Dict["Return Order ID"] = getValue(message, 11)
        
    print(Dict)
    ret_list = match(Dict)

    print("ret_list:", ret_list)
    
    ret_message_list = list()
    
    for ret_message in ret_list:

        message = fix.Message()
        
        header = message.getHeader()
        
        header.setField(fix.BeginString("FIX.4.4"))
        
        header.setField(fix.SenderCompID("COEPEXCH"))
            
        header.setField(fix.TargetCompID("EXECLINKS"))
        
        header.setField(fix.MsgType("8"))  #Tag 8 for Execution report
        
        message.setField(37, ret_message["Order ID"])

        response = ret_message["Response"]
        
        #New order accepted
        if (response == 0):
            
            message.setField(39, "0")
            
            message.setField(150, "0")
            
        #Amend order accepted            
        elif (response == 1):
            
            message.setField(150, "5")
            
        #Cancel order accepted
        elif (response == 2):
            
            message.setField(39, "4")
            
            message.setField(150, "4")
            
        #New order, amend order or cancel order rejected
        elif (response == 3 or response == 4 or response == 5):
            
            message.setField(39, "8")
            
            message.setField(150, "8")
            
        #Full execution of order            
        elif (response == 6):
            
            message.setField(39, "2")
            
            message.setField(150, "F")
            
            message.setField(55, ret_message["Security ID"])
            
            message.setField(38, str(ret_message["Order Qty"]))
            
            message.setField(44, str(ret_message["Price"]))
            
        #Partial execution of order            
        elif (response == 7):
            
            message.setField(39, "1")
            
            message.setField(150, "F")
            
            message.setField(55, ret_message["Security ID"])
            
            message.setField(38, str(ret_message["Order Qty"]))
            
            message.setField(44, str(ret_message["Price"]))
            
        ret_message_list.append(message)
        
    return ret_message_list

'''
Market Data Entry = MDEntry
This sends snapshots of n orders executed in the same message
Returns the list of top n open orders in both the buy and sell lists of the required stock, as given in the message
'''

def top_n_orders(message, n):
    
    stock_id = getValue(message, 55)
    
    dict_list = give_top_n(stock_id, n)
    
    ret_message = fix44.MarketDataSnapshotFullRefresh()

    group = fix44.MarketDataSnapshotFullRefresh().NoMDEntries()
    
    for Dict in dict_list:
        
        group.setField(fix.MDEntryType(Dict["Type"]))
        
        group.setField(fix.MDEntryPx(Dict["Price"]))
        
        group.setField(fix.MDEntrySize(Dict["Quantity"]))
        
        group.setField(fix.OrderID(Dict["Order ID"]))
        
        ret_message.addGroup(group)
        
    ret_message.setField(55, stock_id)
    
    return ret_message