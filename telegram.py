# -- GNU GPLv3 --

import requests as rq
import time
import subprocess as sp
import json
import threading


def getPIU():
    """
    asks which gpio pin the user wants, activates it, sets it to output and returns it
    """

    want=input("Which gpio pin would you like to use: (e.g: 15)\n") or "15"
    
    command = "ls /sys/class/gpio/ | grep gpio" + want
    test = str(sp.run(command, capture_output=True, shell=True).stdout)
    teststring = "gpio" + want

    if teststring in test:
        command = "echo out > /sys/class/gpio/gpio" +want+ "/direction"
        sp.call(command, shell=True)

    else:
        command = "echo " + want + " > /sys/class/gpio/export"
        sp.call(command, shell=True)
        time.sleep(2)
        command = "echo out > /sys/class/gpio/gpio" + want + "/direction"
        sp.call(command, shell=True)
    
    return want

def get_last_update_id():   # looks for "last_update_id.txt" and returns its contents // creates the file if it does not exist
    try:
        with open('last_update_id.txt', 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        f = open("last_update_id.txt", "x")
        return 0

def save_last_update_id(lui):   # saves parameter to "last_update_id.txt"
    with open('last_update_id.txt', 'w') as file:
        file.write(str(lui))

class telbot():
    """
    telegramm bot class:
        initialize like so: mybot = telbot("mybotname", "myapikey", "mygpiopinnumber")
        
        methods:
            blink()         #flashes LED twice
            request()       #makes a request to the telegram api
            update()        #updates to check for messages
            incoming()      #calls the update() method, checks its output and calls the respond() function
            respond()       #responds to messages using the request() method

    """
    def __init__(self, name: str, api_key: str, pin: str):
        self.name=name
        self.api_key=api_key
        self.pin=pin
        self.on = "echo 1 > /sys/class/gpio/gpio" + pin + "/value"
        self.off = "echo 0 > /sys/class/gpio/gpio" + pin + "/value"
        self.last_update_id=get_last_update_id()

    def blink(self, speed): # flashes LED twice
        time.sleep(speed)
        sp.call(self.on, shell=True)
        time.sleep(speed)
        sp.call(self.off, shell=True)
        time.sleep(speed)
        sp.call(self.on, shell=True)
        time.sleep(speed)
        sp.call(self.off, shell=True)
    updates=[]
    
    def request(self, method, param):   # generates a request // can be used for all types of requests
        url = "https://api.telegram.org/bot" + self.api_key + "/" + method + param
        #print(F"making a request @ {url}")
        resp=rq.get(url)
        #print(resp.status_code)
        return resp

    def update(self):   # makes a getUpdate request
        updata = self.request("getUpdates", F"?offset={self.last_update_id + 1}")
        updata = json.loads(updata.text)
        return updata

    def incoming(self, trfa): # checks data from update()
        data = self.update()
        #check if data is empty
        if data['result']!=[]:
            for update in data['result']:
                #printdd(F"last_updat_id:       {self.last_update_id}")
                current_update_id = int(update['update_id'])
                #print(F"current_update_id:   {current_update_id}")
                if current_update_id > self.last_update_id:
                    #print(F"handling update with id: {update['update_id']}")
                    self.updates.clear()
                    self.updates.append(update)
                    self.respond(update, trfa)
                self.last_update_id = current_update_id


    
    def respond(self, thing, TF):   #does something on message

        chat_id = thing['message']['chat']['id']
        message_text = thing['message']['text'].lower()
        pinadd = "/sys/class/gpio/gpio" + self.pin + "/value"
        gpio_val = int(sp.run(['cat', pinadd], capture_output=True, text=True).stdout)

        # message logic
        if message_text=="on":
            if gpio_val==1:
                answer="LED already on!"
            else:
                answer="turning LED on"
                sp.call(self.on, shell=True)
        elif message_text=="off":
            if gpio_val==0:
                answer="LED already off"
            else:
                answer="turning LED off"
                sp.call(self.off, shell=True)
        elif message_text=="blink":
            answer=";)"
            self.blink(0.2)
        elif message_text=="clear":
            answer="what?"
        elif message_text=="s":
            TF[0]=False
            myin="s"
            answer="stopping..."
        else:
            answer="Invalid command"
       
        # sending the sendMessage - request with the paramters answer & chat_id
        self.request("sendMessage", F"?chat_id={chat_id}&text={answer}")

        # saving the last update_id to avoid chaos 
        save_last_update_id(self.last_update_id)


def ask_input(myin, tf): # stops the programm if the user enters "s"
    while myin != "s":
        myin = input("Enter 's' to stop! \n")
    tf[0] = False

def loop(tf, bot): # continiously makes the bot update messages
    while tf[0] == True:
        bot.incoming(tf)


def gettoken(): # looks for "token.txt" -> token.txt needs to contain a valid telegram bot token
    try:
        with open('token.txt', 'r') as file:
            return str(file.read().strip())
    except:
        print("Failed to get token!")


#####  "main function" #####

#  asking which gpio pin should be used
PIU = getPIU();
myin=""
running=[True]
token=gettoken()

#  initializing the telbot instance Raspitin, loading the last update id and updating
Raspitin = telbot("RaspitinLED_bot", token, PIU)
Raspitin.blink(0.5)
Raspitin.incoming(running)


# Create threads
input_thread = threading.Thread(target=ask_input, args=(myin, running,))
bot_thread = threading.Thread(target=loop, args=(running, Raspitin))

# Start threads
input_thread.start()
bot_thread.start()


# Wait for both threads to finish
input_thread.join()
bot_thread.join()

# saving last_update_id & shutting off the LED
save_last_update_id(Raspitin.last_update_id)
sp.call("echo 0 > /sys/class/gpio/gpio15/value", shell=True)
