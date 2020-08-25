import quickfix as fix
import sys
import quickfix44 as fix44
import argparse
import time
from Matching_Engine_Core import match, give_top_n
from quickfix_abstracts import match_and_return, top_n_orders
import logging
import threading

'''
Quickfix imports onCreate(), onLogon(), onLogout(),toAdmin(), fromAdmin(), toApp() and fromApp()
toApp() is a callback for application messages that are being sent to a counterparty.
fromApp() receives application level request.

Quickfix triggers fromApp() when it receives messages on the Socket
 
'''

t_event = threading.Event()

class Application(fix.Application):
    orderID = 0
    execID = 0

    def onCreate(self, sessionID):
        targetCompID = sessionID.getTargetCompID().getValue()
        print ("Session created")
        return
	
    def onLogon(self, sessionID):
        logging.info("--- Application::onLogon ---")
        t_event.set()
        t_event.clear()
        targetCompID = sessionID.getTargetCompID().getValue()
        if (targetCompID == "EXECLINKS") :
            print ("On Logon with EXECLINKS")
        elif (targetCompID == "REALTIMEMARKETS"):
            print ("On Logon with REALTIMEMARKETS")
        return

    def onLogout(self, sessionID):
        logging.info("--- Application::onLogout ---")
        targetCompID = sessionID.getTargetCompID().getValue()
        if (targetCompID == "EXECLINKS") :
            print ("On LogOut with EXECLINKS")
        return

    def toAdmin(self, message, sessionID):
        logging.info("--- Application::toAdmin ---")
        logging.info( str(message) )
        return

    def fromAdmin(self, sessionID, message):
        logging.info("--- Application::fromAdmin ---")
        logging.info( str(message) )
        return
            

    def toApp(self, message, sessionID):
        print("-------toApp() called-----------")
        logging.info("--- Application::toApp ---")
        logging.info( str(message) )
        print("Message sent to Client:")
        print(str(message))
        return

    def fromApp(self, message, sessionID):

            fixList = []
            print (str(message))
            logging.info("--- Application::fromApp ---")
            logging.info( str(message) )
            
            #To Exec Links
            fixList = match_and_return(message)
            
            for fix_message in fixList:
                status = fix.Session.sendToTarget(fix_message, sessionID)
                print("Sent to Client: ", status)
                
            #To RealTimeMarketData - snapshot message
            '''self.snapshot = top_n_orders(message, 3)
            fix.Session.sendToTarget(snapshot, self.real_time_markets_session_id)'''
        
		
def main(config_file):
    try:
        settings = fix.SessionSettings(config_file)
        application = Application()
        storefactory = fix.FileStoreFactory(settings)
        logfactory = fix.FileLogFactory(settings)
        acceptor = fix.SocketAcceptor(application, storefactory, settings, logfactory)
        acceptor.start()
        while(1):
            time.sleep(10)

    except (fix.ConfigError, fix.RuntimeError) as e:
        print(e)
        sys.exit()        
   
if __name__=='__main__':
    parser = argparse.ArgumentParser(description='FIX Client')
    parser.add_argument('file_name', type=str, help='Name of configuration file')
    args = parser.parse_args()
    main(args.file_name)
