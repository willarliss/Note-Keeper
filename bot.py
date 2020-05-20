from datetime import datetime as dt
from key import TOKEN
import urllib.request
import websocket
import json
import os


receiving_note = False
note_action = False


def send_message(channel, text):

    text = text.replace(' ', '%20')
    url = 'https://slack.com/api/chat.postMessage?token={}&channel={}&text={}&as_user=note_keeper&pretty=1'.format(TOKEN, channel, text)
    connection = urllib.request.urlopen(url)
    if text != '': print('MESSAGE SENT')
    connection.close()


def start_rtm():       

    url_string = 'https://slack.com/api/rtm.connect?token={}&pretty=1'.format(TOKEN)
    connection = urllib.request.urlopen(url_string)
    text = connection.read().decode('utf-8')
    connection.close()
    data = json.loads(text)

    return data['url']


def on_error(ws, error):

    print('ERROR OCCURRED', error)


def on_close(ws):

    print('\nCONNECTION TERMINATED')


def on_open(ws):

    print('CONNECTION STARTED\n')

    
def on_message(ws, message): 
    
    global receiving_note
    global note_action
    global title
    global outfile
    
    message_txt = json.loads(message)
    text = message_txt['text']
    channel = message_txt['channel']
    
    if 'bot_id' not in message_txt.keys():
        print('MESSAGE RECEIVED')
        
        if text.lower().strip() == 'new note':      
            print('NEW NOTE')
            receiving_note = True
            note_action = False
            send_message(channel, '`NOTE TITLE:`')
        
        elif text.lower().strip() == 'done':     
            print('SAVING NOTE')
            receiving_note = False
            note_action = False
            outfile.close()
            send_message(channel, '`NOTE SAVED`')
        
        elif receiving_note == True:

            if note_action == False:
                title = text
                send_message(channel, title + ' `NOTE TEXT:`')
                note_action = True
                
                note_file = newFile(title)
                time = dt.now().replace(microsecond=0)
                outfile = open(note_file, 'w', encoding='utf-8')
                encoded_head = title + ' - ' + str(time) + '\n'
                outfile.write(encoded_head)
                
            elif note_action == True:
                send_message(channel, title + ' `NOTE TEXT:`')
                encoded_text = '\n' + text
                outfile.write(encoded_text)                


def newFile(title):
    
    note_name = title.replace(' ','_') + '.txt'
    all_notes = os.listdir(os.getcwd())
    count = 1
    
    while note_name in all_notes:
        note_name = title.replace(' ','_') + '_' + str(count) + '.txt'
        count += 1

    return note_name


if __name__ == '__main__':

    r = start_rtm()
    ws = websocket.WebSocketApp(r, on_message=on_message, 
                                   on_error=on_error,
                                   on_close=on_close, 
                                   on_open=on_open)
    ws.run_forever()
