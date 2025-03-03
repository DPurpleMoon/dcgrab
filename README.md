# dcgrab

Grab message from other channel to desired channel.

### Usage

```
bot.py -i <input_token> -o <output_token> -c <get_channel_id> -u <post_channel_id> -l <message_limit> [-r <reload_time>] [-h]
```
-i <input_token>        User/Bot token for scraping text history  
-o <output_token>       User/Bot token for outputing text history  
-c <get_channel_id>     Channel id of channel to scrap  
-u <post_channel_id>    Channel id to post output  
-l <message_limit>      The number of message to get when executed(Must exceed 0, Default is 100)  
-r <reload_time>        Enable continous mode(Optional), Must specify a reload time when enabled  
-h                      Show help message  
