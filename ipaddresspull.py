#This can be used to pull the IP address that can be passed to the Actor. CloudService and Observer can be ran from local host. Print the IP address at the top of the main screen of the game on Observer side 

#Need requests library, can be downloaded with py -m pip install requests --user

import requests
from requests import get

ip = get('https://api.ipify.org').text
print('My public IP address is: {}'.format(ip))
