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

def parse_date(date):
  return datetime.datetime.strptime(date, "%Y%m%dT%H%M%S")

def call(method, params=[]):
  global x_just_sent
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
      print "Warnning: rpc call error, retry 5 seconds later"
      time.sleep(5)
      continue
    break  
  return None

while True:
  try:
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

    ##x_price_average = price_average/rate_cny["USD"]
    x_nowtime = datetime.datetime.time(datetime.datetime.now())
    x_hour_current = int(x_nowtime.hour)
    print("checking time")
    print(x_nowtime)
    print("justsent %d" % x_just_sent)
    print("Current hour %d" % x_hour_current)
    print("Hour to send %d" % x_hour_chosen)
    if x_hour_chosen == x_hour_current:
      print("Hours Match!")
      if x_just_sent == False:
        print("Time to Send!")
        ## Send one payment per day
        ##client.send_delegate_payment(x_delegate, x_to_account, x_amount)
        ##print("wallet_delegate_withdraw_pay %s, %s, %s" % (DELEGATE_NAME, PAYTO, THRESH))
        response = call("wallet_delegate_withdraw_pay", [DELEGATE_NAME, PAYTO, AMOUNT])
        print("sending Payment...")
        ##print("sending payment... BTS Rate- %.5f USD \n" % (x_price_average))
        f = open("payroll.txt","a")
        f.write('Payment sent at Price-> %s recorded at %s.\n' % (x_price_average, datetime.datetime.now()))
        f.close()
        x_just_sent = True
    else:
      x_just_sent = False
      print("Not time yet...")


    ##if balance > THRESH:
    ##   print("wallet_delegate_withdraw_pay %s, %s, %s" % (DELEGATE_NAME, PAYTO, THRESH))
    ##   response = call("wallet_delegate_withdraw_pay", [DELEGATE_NAME, PAYTO, THRESH])
    
    time.sleep(60)
  except:
    time.sleep(60)
