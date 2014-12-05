#!/usr/bin/env python
# coding=utf8

# This is a script which connects to a delegate periodically to check if it is time to send a payment
# set in the config.json file. It sends the amount to the payto account specified.

import requests
import sys
import os
import json
import getpass
import time
import datetime
from pprint import pprint

BTS_PRECISION = 100000

config_data = open('config.json')
config = json.load(config_data)
config_data.close()

##Send payments to hosted delegate at defined time once per day
global x_just_sent
x_time_to_send = config["x_time_to_send"]
x_just_sent = False
x_fulltime = datetime.time(x_time_to_send, 0, 0)
x_hour_chosen = int(x_fulltime.hour)

auth = (config["bts_rpc"]["username"], config["bts_rpc"]["password"])
url = config["bts_rpc"]["url"]

WALLET_NAME = config["wallet_name"]

DELEGATE_NAME = config["delegate_name"]
PAYTO = config["payto_account"]
AMOUNT = config["x_amount"]
MARKETUSD = "USD"
MARKETBTS = "BTS"

def parse_date(date):
  return datetime.datetime.strptime(date, "%Y%m%dT%H%M%S")

def call(method, params=[]):
  headers = {'content-type': 'application/json'}
  request = {
          "method": method,
          "params": params,
          "jsonrpc": "2.0",
          "id": 1
          }

  while True:
    try:
      response = requests.post(url, data=json.dumps(request), headers=headers, auth=auth)
      result = json.loads(vars(response)["_content"])
      #print "Method:", method
      #print "Result:", result
      return result
    except:
      print "Warning: rpc call error, retry 5 seconds later"
      time.sleep(5)
      continue
    break  
  return None

while True:
  try:
    global x_just_sent
    os.system("clear")
    print("\nRunning Balance Keeper\n")
 
    response = call("wallet_get_account", [DELEGATE_NAME] )
    if "error" in response:
      print("FATAL: Failed to get info:")
      print(result["error"])
      exit(1)
    response = response["result"]

    balance = response["delegate_info"]["pay_balance"] / BTS_PRECISION

    print ("Balance for %s is currently: %s BTS\n" % (DELEGATE_NAME, balance))

    x_nowtime = datetime.datetime.time(datetime.datetime.now())
    x_hour_current = int(x_nowtime.hour)
    print("Payment will be sent at hour: %d" % x_hour_chosen)
    print("Checking the time... %s" % x_nowtime) 
    print("Sent Recently?: %d" % x_just_sent)
    
    x_hour_chosen = x_hour_current
    if x_hour_chosen == x_hour_current:
      print("Hours Match!\n")
      if x_just_sent == False:
        ## Send one payment per day
        ##response = call("wallet_delegate_withdraw_pay", [DELEGATE_NAME, PAYTO, AMOUNT])
        print("Sending Payment Now...\n")
        x_just_sent = True
        
        response = call("blockchain_market_status", [MARKETUSD, MARKETBTS])
        if "error" in response:
          print("FATAL: Failed to get market info:")
          print(result["error"])
          exit(1)
        response = response["result"]
        
        feed_price = response["current_feed_price"]
        USDequiv = AMOUNT * feed_price
        
        response = call("wallet_account_transaction_history", [DELEGATE_NAME])
        if "error" in response:
          print("FATAL: Failed to get account history info:")
          print(result["error"])
          exit(1)
          
        response = response["result"]
        k = 0
        for i in response:
          l = response[0]["ledger_entries"]["memo"]
          k = k + 1
          print(l)
       
        ##feed_price = response["current_feed_price"]
        
        f = open("payroll.txt","a")
        f.write('Payment Sent!  Date/Time: %s  Amount: %.5f BTS ($%.5f)  Rate: $%.5f /BTS\n' % (datetime.datetime.now(), AMOUNT, USDequiv, feed_price))
        f.close()
        print("Payment Sent!  Date/Time: %s  Amount: %.5f BTS ($%.5f)  Rate: $%.5f /BTS\n" % (datetime.datetime.now(), AMOUNT, USDequiv, feed_price))
      else:
        print("Payment has already been sent.  Nothing to do.\n")
    else:
      x_just_sent = False
      print("\nNot time yet...\n")
      
    print("going to sleep")
    time.sleep(60)
  except:
    print("exception")
    time.sleep(60)
