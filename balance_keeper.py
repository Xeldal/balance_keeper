#!/usr/bin/env python
# coding=utf8

# This is a script which connects to a delegate periodically to check if the pay balance is at a,
# threshold set in the config.json file. If it is, it sends the balance_threshold amount to the payto account
# specified.

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
    print("\nRunning Balance Keeper")
 
    response = call("wallet_get_account", [DELEGATE_NAME] )
    if "error" in response:
      print("FATAL: Failed to get info:")
      print(result["error"])
      exit(1)
    response = response["result"]

    balance = response["delegate_info"]["pay_balance"] / BTS_PRECISION

    print ("Balance for %s is currently: %s BTS" % (DELEGATE_NAME, balance))

    x_nowtime = datetime.datetime.time(datetime.datetime.now())
    x_hour_current = int(x_nowtime.hour)
    print("Payment will be sent at hour: %d" % x_hour_chosen)
    print("Checking the time... %s" % x_nowtime) 
    print("Sent Recently?: %d" % x_just_sent)
    if x_hour_chosen == x_hour_current:
      print("Hours Match!\n")
      if x_just_sent == False:
        ## Send one payment per day
        response = call("wallet_delegate_withdraw_pay", [DELEGATE_NAME, PAYTO, AMOUNT])
        print("Sending Payment Now...\n")
        x_just_sent = True
        
        response = call("blockchain_market_status", [MARKETUSD, MARKETBTS])
        if "error" in response:
          print("FATAL: Failed to get market info:")
          print(result["error"])
          exit(1)
        response = response["result"]
        
        feed_price = response["current_feed_price"]
        f = open("payroll.txt","a")
        f.write('Payment Sent!   Price: %.5f    DATE/TIME: %s.\n' % (feed_price, datetime.datetime.now()))
        f.close()
        print("Payment Sent!   Price: %.5f    DATE/TIME: %s.\n" % (feed_price, datetime.datetime.now()))
      else:
        print("Payment has already been sent.  Nothing to do.\n")
    else:
      x_just_sent = False
      print("Not time yet...")
      
    print("going to sleep")
    time.sleep(60)
  except:
    print("exception")
    time.sleep(60)
