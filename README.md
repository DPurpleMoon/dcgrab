# dcgrab

Grab message from other channel to desired channel.

## Usage

```
bot.py -i <input_token> -o <output_token> -c <get_channel_id> -u <post_channel_id> -l <message_limit> [-r <reload_time>] [-h]
```
-i&nbsp;<input_token>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;User/Bot token for scraping text history  
-o&nbsp;<output_token>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;User/Bot token for outputing text history  
-c&nbsp;<get_channel_id>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Channel id of channel to scrap  
-u&nbsp;<post_channel_id>&nbsp;&nbsp;&nbsp;Channel id to post output  
-l&nbsp;<message_limit>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The number of message to get when executed(Must exceed 0, Default is 100)  
-r&nbsp;<reload_time>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Enable continous mode(Optional), Must specify a reload time when enabled  
-h&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show help message  
