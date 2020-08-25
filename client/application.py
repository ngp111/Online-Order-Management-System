import sys
import time
import quickfix as fix
import quickfix44 as fix44
import logging
from datetime import datetime
import threading
from collections import deque
import argparse
import json
from quickfix import Side_BUY, Side_SELL
import time

#forward_path_queue = [{'order_id':7317, 'user_id': 38234, 'product_id' : 'TCS', 'side': 1, 'ask_price': 70, 'total_qty' : 40}]
heartbeatingFlag = 0

# Start Test cases after the heartbeat with ExecutionLink

t_event = threading.Event()

# configured
__SOH__ = chr(1)

# Logger
logfix = logging.getLogger('FIX')


# Event for triggerting pass or fail status of test case on ExecutionLink side
validation_failed = threading.Event()

class Application(fix.Application):
	live_orders = {}

	def onCreate(self, sessionID):
		self.sessionID = sessionID
		logging.info("--- Application::onCreate ---")
		print ("Session created with sessionID :", sessionID)
		return

	def onLogon(self, sessionID):
		logging.info("--- Application::onLogon ---")
		heartbeatingFlag = 1
		t_event.set()
		t_event.clear()
		return
	
	def onLogout(self, sessionID):
		logging.info("--- Application::onLogout ---")
		heartbeatingFlag = 0
		return

	def toAdmin(self, message, sessionID):
		return

	def fromAdmin(self, sessionID, message):
		logging.info("--- Application::fromAdmin ---")
		logging.info( str(message) )
		return

	def toApp(self, message, sessionID):
		msg = message.toString().replace(__SOH__, "|")
		print("-----toApp called-----")
		#print(msg)
		logfix.info("S >> (%s)" % msg)
		return
	def fromApp(self, message, sessionID):
		print("-----FromApp called-----")
		msg = message.toString().replace(__SOH__, "|")
		print("Execution Report from ME: ",msg)
		self.onExecutionReport(message)
		return

	def getValue(self, fix_message, tag): 
		field = fix.StringField(tag)
		if(fix_message.isSetField(field)):
			return (str(fix_message.getField(tag)))
		elif(fix_message.getHeader().isSetField(field)):
			return (str(fix_message.getHeader().getField(tag)))
		elif(fix_message.getTrailer().isSetField(field)):
			return (str(fix_message.getTrailer().getField(tag)))
		else:
        		return None

	def onExecutionReport(self, message) :
		orderID = self.getValue(message, 37)
		if orderID not in self.live_orders :
			if self.getValue(message, 150) == "0" and self.getValue(message, 39) == "0" :
				print("Order of orderID: ",orderID, " is accepted")
				self.live_orders[orderID] = ["Accepted"]
			elif self.getValue(message, 150) == "8" and self.getValue(message, 39) == "8" :
				print("Order of orderID: ",orderID, " is rejected")
				self.live_orders[orderID] = ["Rejected"]
		else :
			if self.getValue(message, 150) == "F" and self.getValue(message, 39) == "2" :
				print("Order with orderID: ", orderID, "is completely filled")
				self.live_orders.pop(orderID)
			elif self.getValue(message, 150) == "F" and self.getValue(message, 39) == "1" :
				print("Order with orderID: ", orderID, "is partially filled with qty done = ",self.getValue(message, 38))

	def run(self) :
		#logon
		logon_message = "8=FIX.4.49=7535=A34=109249=TESTBUY152=20180920-18:24:59.64356=TESTSELL198=0108=6010=178"
		logon = fix44.Logon()
		print("Sending Logon")
		logon.setString(logon_message, True, fix.DataDictionary(r'./fix44.xml'))
		

		with open('orders.json','r') as json_file:
			user_data=json.loads(json_file.read())
			for message in user_data:
				self.onNOS(message)
		return 

	def onNOS(self, message):
		trade = fix.Message()
		header = trade.getHeader()
		header.setField(fix.BeginString("FIX.4.4"))
		header.setField(fix.SenderCompID("COEPUSER"))
		header.setField(fix.TargetCompID("COEPEXCH"))
		header.setField(fix.MsgType("D"))
		trade.setField(fix.ClOrdID(message['order_id']))
		trade.setField(fix.Symbol(message['symbol']))
		if message['side'] == 'sell' :
			trade.setField(fix.Side(Side_SELL))
			trade.setField(58, "Sell shares")
		else :
			trade.setField(fix.Side(Side_BUY))
			trade.setField(58, "Buy shares")
		trade.setField(40, "2")
		trade.setField(fix.Price(message['ask_price']))
		trade.setField(fix.OrderQty(message['total_qty']))
		transact_time = datetime.utcnow() 
		trade.setField(60, transact_time.strftime("%Y%m%d-22:29:00.000"))
		trade.setField(fix.Account("EXECLINKS"))
		
		fix.Session_sendToTarget(trade, self.sessionID)
		return


