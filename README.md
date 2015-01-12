This is an adaptation of Riverheads adaptation of alt's watchdog.py script gutted to make daily payments to another user.
- Copy the config.json.sample to config.json
- Update config.json with your own rpc and delegate data as well as who the payments will be sent to and the amount.
- x_amount is the amount your going to send daily.  1 = 1 BTS
- x_time_to_send is the hour when the payment will be sent everyday. Uses 24 hours, 14 = 2PM
- Script loops every 60 seconds to check if it is time to send.

