#pip install heroku3 
import heroku3
import argparse
import os

''' 
set env variable HEROKU_TOKEN to your heroku access token
ex: export HEROKU_TOKEN=<token>
'''
HEROKU_TOKEN = os.environ['HEROKU_TOKEN'] 

'''
Get command line arguments 
-a <app_name> 
-k <config var name> 
-v <config var value>
'''
parser = argparse.ArgumentParser(description="add config variable to heroku app: -a <heroku_app_name> -k <key> -v <value>\ncreate HEROKU_TOKEN env var to pass in api token")
parser.add_argument('-a', dest = 'app', required=True)
parser.add_argument('-k', dest ='key', required=True)
parser.add_argument('-v', dest = 'value', required=True)
args = parser.parse_args()
app_name = args.app
key      = args.key
val      = args.value

#connect to you heroku account
heroku_conn = heroku3.from_key(HEROKU_TOKEN)
#get app name
app = heroku_conn.apps()[app_name]
#get app configuration 
config = app.config()
#set new config var
config[key] = val
#check if var was succesfully created
if key in config:
    print("variable added")
else:
    print("error in adding variable")

    


