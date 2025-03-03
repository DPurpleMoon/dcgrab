import requests
import json
import time
import getopt
import sys
from urllib.parse import urlparse
import os
from datetime import datetime
import math
from itertools import dropwhile
import multiprocessing
import msvcrt

api = "https://discord.com/api/v10"
message = ""
last = ""
reload_time = None

def detect():
    while True:
        if msvcrt.kbhit():  # Check if a key is pressed
            key = msvcrt.getch()  # Get the key press
            if key == b'c':  # Check if the key is 'c'
                break

def continous_bot(utoken, btoken, channel, output, reloadtime, limit):
    reloadtime = int(reloadtime)
    flimit = 1
    climit = int(limit)
    botrun(utoken, btoken, channel, output, flimit)
    while True:
        time.sleep(reloadtime)
        botrun(utoken, btoken, channel, output, climit)

def check_token_type(token):
    url = "https://discord.com/api/v10/users/@me"
    headers = {
        "Authorization": f"Bot {token}"
    }
    response = requests.get(url, headers=headers)
    type = ""
    if response.status_code == 200:
        type = "bot"
        return type
    elif response.status_code == 401:
        headers = {"Authorization": token} 
        response = requests.get(url, headers=headers) 
        if response.status_code == 200:
            type = "user"
            return type
        else:
            type = "invalid"
            return type
    else:
        type = "nan"
        return type

def getmsg(channel, limit, headers, state, lastid = None, info = None):
    data = info
    if state == "nan": #check if the get request is for the newest message or message before
        message = requests.get(f"{api}/channels/{channel}/messages?limit={limit}", headers = headers)
    elif state == "before": #lastid required to determine which message before specific message should get
        message = requests.get(f"{api}/channels/{channel}/messages?limit={limit}&before={lastid}", headers = headers)
    if message.raise_for_status() != None: #return error for error
        print(message.raise_for_status())
        sys.exit(1)
    ndata = list(reversed(json.loads(message.content[:-1]))) #convert json obtained from discord api to dictionary list
    #add old data in list get above on top of new data get from previous execute of function
    if info == None:
        data = ndata
    else:
        ndata.extend(data)
        data = ndata
    try:
        data[0]["id"]
    except IndexError:
        return "","na"
    else:
        lastid = data[0]["id"] #determine the message id of the first message in list
        return lastid, data

def botrun(utoken, btoken, channel, output, limit):
    data = [{"id":0}]
    lastid = ""
    hundredlimit = 0
    firstlimit = int(limit)
    #split the message obtain limit when execute to bypass discord api get message limit per request
    if int(limit) > 100:
        firstlimit = limit % 100
        hundredlimit = limit // 100

    #determine the input token is user token or bot token
    if check_token_type(utoken) == "user":
        uheaders = {"Authorization": f"{utoken}"}
    elif check_token_type(utoken) == "bot":
        uheaders = {"Authorization": f"Bot {utoken}"}
    elif check_token_type(utoken) == "invalid":
        print("Invalid input token.")
        sys.exit(1)
    elif check_token_type(utoken) == "nan":
        print("Unable to read input token.")
        sys.exit(1)

    #determine the output token is user token or bot token
    if check_token_type(btoken) == "user":
        bheaders = {"Authorization": f"{btoken}"}
    elif check_token_type(btoken) == "bot":
        bheaders = {"Authorization": f"Bot {btoken}"}
    elif check_token_type(btoken) == "invalid":
        print("Invalid output token.")
        sys.exit(1)
    elif check_token_type(btoken) == "nan":
        print("Unable to read output token.")
        sys.exit(1)
    while (list(dropwhile(lambda a : a["id"] != last, data)) == []) and (last != ""): #check if message id from last execution exists and the last message id is not contained in "data" dictionary list
        #will continue to grab messages until checked the last message id from last execution is in "data" dictionary list
        if lastid == "":
            outmsg = getmsg(channel, 100, uheaders, "nan")
            lastid = outmsg[0]
            data = outmsg[1]
            if list(dropwhile(lambda a : a["id"] != last, data)) == []:
                return
        else:
            #discord api
            time.sleep(1)
            outmsg = getmsg(channel, 100, uheaders, "before", lastid, data)
            lastid = outmsg[0]
            data = outmsg[1]
    else:
        #for first boot or program mode only
        if last == "":
            outmsg = getmsg(channel, firstlimit, uheaders, "nan")
            lastid = outmsg[0]
            data = outmsg[1]
            while hundredlimit > 0:
                #discord api
                time.sleep(1)
                outmsg = getmsg(channel, 100, uheaders, "before", lastid, data)
                lastid = outmsg[0]
                data = outmsg[1]
                hundredlimit = hundredlimit - 1
        if data == "na":
            if reload_time == None:
                print("No message to get.")
            return
        
        #delete duplicate message before the message obtained from last execution in data dictionary list
        if list(dropwhile(lambda a : a["id"] != last, data)) != []:
            data = list(dropwhile(lambda x: x["id"] != last, data))
            data = list(dropwhile(lambda x: x["id"] == last, data))
        if data == []:
            return
        
        
    #for input message debug
    #print(json.dumps(data, indent=4))
    outputmsg(data, bheaders, output)

def outputmsg(data, headers, output):
    for i, n in enumerate(data):
        json_data = ""
        files = ""
        fileurl = ""
        #discord api
        time.sleep(1)
        dt = datetime.fromisoformat(n["timestamp"])
        dt = math.floor(dt.timestamp())
        #reading bot name
        if n['author']["global_name"] == None:
            n['author']["global_name"] = n['author']["username"]
        if n["embeds"] and not n["attachments"]:
            #message with embeds that contains image
            try: 
                n["embeds"][0]["image"]
            except KeyError:
                pass
            else:
                json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: ",
                    "tts": False,
                    "allowed_mentions": {
                        "parse": []
                        },
                    "embeds": [{
                        "title": f"{n["embeds"][0]["title"]}",
                        "description": f"{n["embeds"][0]["description"]}",
                        "color": n["embeds"][0]["color"],
                        "author": {
                            "name": f"{n["embeds"][0]["author"]["name"]}",
                            "icon_url": f"{n["embeds"][0]["author"]["icon_url"]}"
                            },
                        "image":{
                            "url": f"{n["embeds"][0]["image"]["url"]}"
                        }
                    }]
                }
            if n["embeds"][0]["type"] == "video":
                #message with embeds that contains video
                if {n["content"]} == []:
                    json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: ",
                    "tts": False,
                    "allowed_mentions": {
                        "parse": []
                        },
                    "embeds": [{
                        "title": f"{n["embeds"][0]["title"]}",
                        "description": f"{n["embeds"][0]["description"]}",
                        "url": f"{n["embeds"][0]["url"]}",
                        "color": n["embeds"][0]["color"],
                        "author": {
                            "name": f"{n["embeds"][0]["author"]["name"]}",
                            "url": f"{n["embeds"][0]["author"]["url"]}"
                            },
                        "video": {
                            "url": f"{n["embeds"][0]["video"]["url"]}"
                        }
                    }]
                }
                #message with embeds that contains video link only
                else:
                    json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: \n{n["content"]}",
                    "tts": False,
                    "allowed_mentions": {
                        "parse": []
                        }
                    }
            #message with embeds that contains text only
            if n["embeds"][0]["type"] == "rich":
                json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: \n{n["content"]}",
                    "embeds": {
                        "color": n["embeds"][0]["color"],
                        "fields": n["embeds"][0]["fields"]
                    }
                }
                def fix_links(value):
                    return value.replace('<', '').replace('>', '')
                if isinstance(json_data['embeds'], dict):
                    json_data['embeds'] = [json_data['embeds']]
                for embed in json_data['embeds']:
                    for field in embed['fields']:
                        field['value'] = fix_links(field['value'])
            #message with embeds that contains gifv
            if n["embeds"][0]["type"] == "gifv":
                fileurl = requests.get(f"{n['embeds'][0]['url']}.gif", stream=True)
                json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: \n",
                }
                files = {
                    "file": (f"{n['embeds'][0]['provider']['name']}.gif", fileurl.raw)
                }
            #message with embeds that contains user uploaded gifv(images) only
            if n["embeds"][0]["type"] == "image":
                parsedurl = urlparse(n['embeds'][0]['thumbnail']['url'])
                path = parsedurl.path
                filename_with_params = path.split('/')[-1]
                filename = filename_with_params.split('?')[0]
                extension = os.path.splitext(filename)
                fileurl = requests.get(f"{n['embeds'][0]['thumbnail']['url']}", stream=True)
                json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: \n{n["content"]}",
                }
                files = {
                    "file": (f"{filename}", fileurl.raw, f"image/{extension}")
                }
        elif n["attachments"] and not n["embeds"]:
            fileurl = requests.get(f"{n['attachments'][0]['url']}", stream=True)
            json_data = {
                "content": f"**{n['author']["global_name"]}** at <t:{dt}>: \n{n["content"]}",
            }
            try: 
                n['attachments'][0]['content_type']
            except KeyError:
                #message with attachment that contains generic file type
                files = {
                "file": (f"{n['attachments'][0]['filename']}", fileurl.raw , "application/octet-stream")
            }
            else:
                #message with attachment that contains image/video/audio
                files = {
                "file": (f"{n['attachments'][0]['filename']}", fileurl.raw , f"{n['attachments'][0]['content_type']}")
            }
        else:
            try: 
                n["thread"]["id"]
            #message with rich text only
            except KeyError:
                json_data = {
                "content": f"**{n['author']["global_name"]}** at <t:{dt}>: {n["content"]}",
                "tts": False,
                "allowed_mentions": {
                    "parse": []
                }
            }
            #thread specific message
            else:
                json_data = {
                    "content": f"**{n['author']["global_name"]}** at <t:{dt}>: \n**{n['author']["global_name"]}** started a thread: **{n["content"]}**. See all threads.",
                    "tts": False,
                    "allowed_mentions": {
                        "parse": []
                    }
                }
        

        #for output message debug
        #print(json.dumps(json_data, indent=4))
        if files == "":
            response = requests.post(f"{api}/channels/{output}/messages", headers = headers, json = json_data)
        elif files != "":
            response = requests.post(f"{api}/channels/{output}/messages", headers = headers, data = json_data, files = files)
        if response.raise_for_status() != None:
            print(response.raise_for_status())
            sys.exit(1)
        #save last message id for next execution for continuous program mode
        if i == len(data) - 1:
            global last 
            last = n["id"]

    
   
HELP = '''Usage: bot.py -i <input_token> -o <output_token> -c <get_channel_id> -u <post_channel_id> -l <message_limit> [-r <reload_time>] [-h]
Options:
-i <input_token>        User/Bot token for scraping text history
-o <output_token>       User/Bot token for outputing text history
-c <get_channel_id>     Channel id of channel to scrap
-u <post_channel_id>    Channel id to post output
-l <message_limit>      The number of message to get when executed(Must exceed 0, Default is 100)
-r <reload_time>        Enable continous mode(Optional), Must specify a reload time when enabled
-h                      Show this help'''
   
def main(args):
    try:
        opts, args = getopt.getopt(args, 'i:o:c:u:l:r:h')
    except getopt.GetoptError:
        print('Invalid options.', HELP, sep='\n')
        sys.exit(1)
    input_token, output_token, get_channel_id, post_channel_id, message_limit, reload_time = None, None, None, None, "100", None
    for opt, arg in opts:
        if opt == '-i':
            if input_token:
                print('You may only select one token for input.')
                sys.exit(1)
            input_token = arg
        elif opt == '-o':
            if output_token:
                print('You may only select one token for output.')
                sys.exit(1)
            output_token = arg
        elif opt == '-c':
            if get_channel_id:
                print('You may only specify one channel to extract from.')
                sys.exit(1)
            get_channel_id = arg
        elif opt == '-u':
            if post_channel_id:
                print('You may only specify one channel to output.')
                sys.exit(1)
            post_channel_id = arg
        elif opt == '-l':
            if message_limit:
                print('You may only specify one message limit to get when executed.')
                sys.exit(1)
            message_limit = arg
        elif opt == '-r':
            if reload_time:
                print('You may only specify one reload time.')
                sys.exit(1)
            if arg == None:
                print('Must specify a reload time when enabling continous mode.')
                sys.exit(1)
            reload_time = arg
        elif opt == '-h':
            print(HELP)
            sys.exit()

    if not input_token:
        print('Must specify input token.', HELP, sep='\n')
        sys.exit(1)
    if not output_token:
        print('Must specify output token.', HELP, sep='\n')
        sys.exit(1)
    if not get_channel_id:
        print('Must specify channel id of a channel to extract from.', HELP, sep='\n')
        sys.exit(1)
    if not post_channel_id:
        print('Must specify channel id of a channel to output.', HELP, sep='\n')
        sys.exit(1)
    if (message_limit.isnumeric() == False) or (message_limit == 0):
        print('Number of message per execute must exceed 0', HELP, sep='\n')
        sys.exit(1)

    if reload_time == None:
        botrun(input_token, output_token, get_channel_id, post_channel_id, message_limit)
    elif reload_time != None:
        print("Press 'C' to terminate this program.")
        p1 = multiprocessing.Process(target=continous_bot, args=[input_token, output_token, get_channel_id, post_channel_id, reload_time, message_limit])
        p2 = multiprocessing.Process(target=detect)
        p1.start()
        p2.start()
        p2.join()
        p1.terminate()
        print("Program ended.")
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
