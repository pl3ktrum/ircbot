import random
import mysql.connector
import mysqllogin
import subprocess
import logging
import time
from socket import *
from datetime import timedelta

######################################
IRCHOST = 'xs4all.nl.quakenet.org'  
IRCPORT =  6667
IRCUSER = 'BierBot * * : bestaboteva'
IRCNICK = 'BierBot'
IRCchannel = '#dasimperium'
######################################

# Liste der im Channel anwesenden leute
user_online = []
# Liste in der die Witze gespeichert werden
witze = []

# konfiguation des loggers
logging.baseconfig(filename='bot.log', level=logging.DEBUG, format="%(asctime)s %(message)s")

def timestamp(ausgabe = ""):
    zeit = time.localtime()
    if ausgabe == "":
        timestmp = "{0:02d}:{1:02d}:{2:02d} - {3:02d}.{4:02d}.{5:04d}".format(zeit[3], zeit[4], zeit[5], zeit[2], zeit[1], zeit[0])
        return timestmp
    elif ausgabe == "zeit":
        timestmp = "{0:02d}:{1:02d}:{2:02d}".format(zeit[3], zeit[4], zeit[5])
        return timestmp
    elif ausgabe == "datum":
        timestmp = "{0:02d}.{1:02d}.{2:02d}".format(zeit[2], zeit[1], zeit[0])
        return timestmp
    
def shell_exec(nick, cmd):
    if cmd == "ls":
        p = subprocess.Popen("ls", stdout=subprocess.PIPE, shell=True)
        output = p.stdout.read().decode().replace("\r", " ").replace("\n", " ")
        con.send("PRIVMSG {} : {}".format(nick, output))
    if cmd == "df":
        p = subprocess.Popen("df -h", stdout=subprocess.PIPE, shell=True)
        output = p.stdout.read().decode().replace("\r", " ").replace("\n", " ")
        con.send("PRIVMSG {} : {}".format(nick, output)) 
    else:
        con.send("PRIVMSG {} : wat?".format(nick))
        
def system_uptime(nick, privat = False):
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(timedelta(seconds = uptime_seconds))
        if privat == True:
            con.send("PRIVMSG {} :Uptime: {}".format(nick, uptime_string))
        else:
            con.send("PRIVMSG {} :Uptime: {}".format(IRCchannel, uptime_string))
    except BaseException as e:
        logging.exception("FEHLER '{}'".format(e))

def witzeupdate(nick):
    global witze
    startzeit = time.time()
    try:
        f = open("witze.txt", "r")
    except BaseExcpetion as e:
        logging.exception("witzedatei konnte nicht geladen werden '{}'".format(e))
    witze = f.readlines()
    logging.info("Es wurden {} Witze eingelesen".format(len(witze)))
    f.close()
    endzeit = time.time()
    con.send("PRIVMSG {} :Es wurden {} witze in {} geladen".format(nick, len(witze), round(endzeit - startzeit, 4)))
    
def gibwitz():
    global witze
    rseed = random.random()
    random.seed(rseed)
    if len(witze) != 0:
        witz = witze[random.randint(0,len(witze)-1)]
        return witz
    else:
        return "keine Witze geladen"
    
def bot_commands(nick):
    befehle = (
        "commands - Listet alle Befehle auf",
        "uhr - Gibt die Uhrzeit aus",
        "datum - Gibt das Datum aus",
        "bier - Gibt dir ein köstliches vBier",
        "energy - Gibt einen Köstlichen Monster Energy",
        "monster - macht das gleiche wie energy",
        "witz - lässt den Bot einen unglaublich guten Witz erzählen",
        "shit - gibt einen Joint rum",
        "kaffee - gibt kaffee",
        "uptime - gibt die server uptime aus"
        )
    for element in befehle:
        con.send("PRIVMSG {} :{}".format(nick, element))
        time.sleep(0.2)
        
##def bot_say(nachricht):
##    nachricht = nachricht.split("say", 1)[1]
##    con.send("PRIVMSG {} :{}".format(IRCchannel, nachricht))
    
def bot_weed(nick, privat = False):
    if privat == False:
        con.send("PRIVMSG {} :BierBot steckt einen Joint an und reicht ihn herum".format(IRCchannel))
    else:
        con.send("PRIVMSG {} :BierBot steckt dir Joint an und reicht ihn dir".format(nick))
        
def bot_witz(nick, privat = False):
    if privat == False:
        con.send("PRIVMSG {} :{}".format(IRCchannel, gibwitz()))
    else:
        con.send("PRIVMSG {} :{}".format(nick, gibwitz()))
        
def bot_uhrzeit(nick, privat):
    if privat == False:
        con.send("PRIVMSG {} :Es ist gerade {}".format(IRCchannel, timestamp("zeit")))
    else:
        con.send("PRIVMSG {} :Es ist gerade {}".format(nick, timestamp("zeit")))

def bot_datum(nick, privat):
    if privat == False:
        con.send("PRIVMSG {} :Wir haben den {}".format(IRCchannel, timestamp("datum")))
    else:
        con.send("PRIVMSG {} :Wir haben den {}".format(nick, timestamp("datum")))       

def bot_bier(nick, privat):
    if privat == False:
        con.send("PRIVMSG {} :Öffnet ein Bier für {} und reicht es feierlich rüber".format(IRCchannel, nick))
    else:
        con.send("PRIVMSG {} :Öffnet dir ein Bier und reicht es feierlich rüber".format(nick))
    botmysql.userstats(nick, "bier_erhalten")
    
def bot_kaffee(nick, privat):
    if privat == False:
        con.send("PRIVMSG {} :Reicht {} einen leckeren Kaffee rüber".format(IRCchannel, nick))
    else:
        con.send("PRIVMSG {} :Reicht dir einen mega leckeren Kaffee rüber".format(nick))
    botmysql.userstats(nick, "energy_erhalten")  

def bot_monster(nick, privat):
    if privat == False:
        con.send("PRIVMSG {} :Reicht {} ein mega kaltes Monster Energy rüber".format(IRCchannel, nick))
    else:
        con.send("PRIVMSG {} :Reicht dir ein mega kaltes Monster Energy rüber".format(nick))
    botmysql.userstats(nick, "energy_erhalten")
    
def bot_willkommen(nick):
    global user_online
    if nick != IRCNICK:
        con.send("PRIVMSG {} :Hallo {}!".format(IRCchannel, nick))
        botmysql.userstats(nick, "joined_channel")
        user_online.append(nick)
        
def bot_wiedersehen(nick):
    global user_online
    botmysql.userstats(nick, "leaved_channel")
    user_online.remove(nick)
    
def nick_changed(nick_alt, nick_neu):
    global user_online
    user_online.remove(nick_alt)
    user_online.append(nick_neu)
    botmysql.userstats(nick_alt, "nick_changed", nick_neu)

def konsolen_ausgabe(nachricht):
    zeit = timestamp()
    print("\n" + zeit + nachricht + "\n\n")

def bot_adjektiv(nick, privat, adjektiv):
    global user_online
    if adjektiv.find(".") != -1:
        adjektiv = adjektiv.replace(".","")
    if adjektiv.find("!") != -1:
        adjektiv = adjektiv.replace("!","")
    if adjektiv.find("?") != -1:
        adjektiv = adjektiv.replace("?","")
    if adjektiv == "cool":
        if privat == True:
            con.send("PRIVMSG {} :Du nicht!".format(nick))
            return
        else:
            con.send("PRIVMSG {} :Du nicht!".format(IRCchannel))
            return
    rseed = random.random()
    random.seed(rseed)
    if privat == True:
        con.send("PRIVMSG {} :{} ist {}".format(nick, user_online[random.randint(0, len(user_online) -1)], adjektiv))
    else:
        con.send("PRIVMSG {} :{} ist {}".format(IRCchannel, user_online[random.randint(0, len(user_online) -1)], adjektiv))
        
def pingpong(message):
# Antwortet auf den Ping
    pong = message.split(":")
    con.send("PONG :" + pong[1])

# Überprüft die eingegangenen nachrichten und verarbeitet diese weiter
def controller(message):
    # Globale Variable Importieren
    global user_online
    # Überprüft auf PING
    if message.startswith("PING :"):
        pingpong(message)
    # Überprüft auf authentifizierung und joined dem channel
    if message.split(" ")[1].startswith("221"):
        con.send("JOIN " + IRCchannel)
    # Speicher die User die im channel sind in eine Liste
    if message.split(" ")[1].startswith("353"):
        for nick in message.split(" ")[5:]:
            if nick.startswith(":") or nick.startswith("@"):
                user_online.append(nick[1:])
            else:
                user_online.append(nick)
    
    # Checkt ob jemand joined oder leaved oder umbenennt
    if message.split(" ")[1].startswith("QUIT") or message.split(" ")[1].startswith("PART"):
        nick = message.split("!")[0][1:]
        bot_wiedersehen(nick)
        
    if message.split(" ")[1].startswith("JOIN"):
        nick = message.split("!")[0][1:]
        bot_willkommen(nick)
        
    if message.split(" ")[1].startswith("NICK"):
        nick_alt = message.split("!")[0][1:]
        nick_neu = message.split("NICK")[1][2:]
        nick_changed(nick_alt, nick_neu)
        
    # Checkt ob ein User etwas geschrieben hat
    if message.split(" ")[1].startswith("PRIVMSG"):
        #prüft ob es query oder öffentlich ist
        if message.split(" ")[2].startswith(IRCNICK):
            privat = True
        else:
            privat = False
            
        #Extrahiert den Nick aus der servermessage
        nick = message.split("!")[0][1:]
        #Extrahiert die Nachricht aus der servermessage
        nachricht = message.split(" ", 3)[3][1:]
        #Schickt die nachricht an die Verlaufmethode
        botmysql.chatlog(nick, nachricht)
        #Überprüft ob der Bot angesprochen wurde
        if nachricht.lower().find(IRCNICK.lower()) != -1 and message.split(" ")[1].startswith("PRIVMSG"):
            if nachricht.lower().startswith(IRCNICK.lower()):
            ###################################################
            # AB HIER WERDEN DIE BEFEHL AN DEN BOT ÜBERPRÜFT  #
            ###################################################
                # Überprüft ob nach dem namen ein doppeltpunkt kommt
                if nachricht.lower().split(IRCNICK.lower())[1].startswith(":"):
                    bot_befehl = nachricht.lower().split(IRCNICK.lower())[1][2:].lower()
                else:
                    bot_befehl = nachricht.lower().split(IRCNICK.lower())[1][1:].lower()
                logging.info("Botbefehl: " + bot_befehl)
                if bot_befehl == "uhr":
                    bot_uhrzeit(nick, privat)
                if bot_befehl == "datum":
                    bot_datum(nick, privat)
                if bot_befehl == "bier":
                    bot_bier(nick, privat)
                if bot_befehl == "energy" or bot_befehl == "monster":
                    bot_monster(nick, privat)
                if bot_befehl == "witz":
                    bot_witz(nick, privat)
                if bot_befehl == "witzupdate":
                    witzeupdate(nick)                    
                if bot_befehl == "shit":
                    bot_weed(nick, privat)
                if bot_befehl == "commands":
                    bot_commands(nick)
                if bot_befehl == "kaffee":
                    bot_kaffee(nick, privat)
                if bot_befehl.startswith("say0815"):
                    bot_say(nachricht)
                if bot_befehl.startswith("wer ist"):
                    adjektiv = bot_befehl.split(" ", 2)[2]
                    bot_adjektiv(nick, privat, adjektiv)
                if bot_befehl == "uptime":
                    system_uptime(nick, privat)
                if bot_befehl.startswith("exec"):
                    cmd = bot_befehl.split(" ", 1)[1]
                    shell_exec(nick, cmd)
             
class connection:
    # Konstruktor
    def __init__(self, ho, po, us, ni):
        self.HOST = str(ho)
        self.PORT = int(po)
        self.USER = str(us)
        self.NICK = str(ni)
        # Socket Objekt erstellen
        self.s = socket(AF_INET, SOCK_STREAM)
        # Dateireferenz vom Socket erstellen
        self.fs = self.s.makefile("rw")
    # Verbindung Herstellen
    def connect(self):
        # Socket verbinden
        self.s.connect((self.HOST, self.PORT))
        # Beim Server anmelden
        self.fs.write("PASS " + str(random.random()) + "\n")
        self.fs.write("USER " + self.USER + "\n")
        self.fs.write("NICK " + self.NICK + "\n")
        self.fs.flush()
    def receive(self):
        while True:
            # sendet die empfangenen daten an die controller methode
            # ohne escape sequenz
            try:
                message = self.fs.readline()[:-1]
                controller(message)
            except BaseException as e:
                logging.exception("Fehler beim einlesen der nachricht '{}'".format(e))

    def send(self, nachricht):
        global startzeit
        global endzeit
        try:
            self.fs.write(nachricht + "\n")
            self.fs.flush()
            botmysql.chatlog("BOT", nachricht)
        except BaseException as e:
            logging.exception("Fehler beim senden der Nachricht '{}'".format(e))

class botmysql:
    def __init__(self):
        self.sqlhost = mysqllogin.sqlhost
        self.sqluser = mysqllogin.sqluser
        self.sqlpw = mysqllogin.sqlpw
        self.sqldb = mysqllogin.sqldb

    def userExists(self, nick):
        #Prüft ob der Nutzer angelegt ist, und legt dieses gegebenenfalls an
        conn = mysql.connector.connect(user=self.sqluser, password=self.sqlpw, host=self.sqlhost, database=self.sqldb, buffered=True)
        cur = conn.cursor()
        cur.execute("SELECT nick FROM userstats WHERE nick = '{}'".format(nick))
        if cur.rowcount < 1:
            cur.execute("INSERT INTO userstats (nick) VALUES '{}'".format(nick))
            return True
        else:
            return True
   conn.close()
   
    def chatlog(self, nick, nachricht):
        if not nachricht.startswith("PONG :xs4all.nl.quakenet.org"):
        # Verbindungm mit der Datenbank herstellen
        conn = mysql.connector.connect(user=self.sqluser, password=self.sqlpw, host=self.sqlhost, database=self.sqldb, buffered=True)
        cur = conn.cursor()
        # Query ausführen
        cur.execute("INSERT INTO irclog (nick, nachricht) VALUES ('{}', '{}')".format(nick, nachricht))
        if userExists(nick):
            cur.execute("UPDATE userstats SET zeichen_gesendet=zeichen_gesendet+{} where nick='{}'".format(len(nachricht), nick))
        conn.close()
      
    def userstats(self, nick, action, value=""):
    # Verbindungm mit der Datenbank herstellen
    conn = mysql.connector.connect(user=self.sqluser, password=self.sqlpw, host=self.sqlhost, database=self.sqldb, buffered=True)
    cur = conn.cursor()
    if action == "joined_channel":
        if userExists(nick):
            cur.execute("UPDATE userstats SET gejoined=gejoined+1 where nick='{}'".format(nick))
            cur.execute("UPDATE userstats SET online=1 where nick='{}'".format(nick))
            logging.info("{} CHANNEL BETRETEN".format(nick))
         
    if action == "bier_erhalten":
        if userExists(nick):
            cur.execute("UPDATE userstats SET bier=bier+1 where nick='{}'".format(nick))
            logging.info("{} BIER ERHALTEN".format(nick))
         
    if action == "energy_erhalten":
        if userExists(nick):
            cur.execute("UPDATE userstats SET energy=energy+1 where nick='{}'".format(nick))
            logging.info("{} ENERGY ERHALTEN".format(nick))
         
    if action == "leaved_channel":
        if userExists(nick):
            cur.execute("UPDATE userstats SET online=0 where nick='{}'".format(nick))
            logging.info("{} CHANNEL VERLASSEN".format(nick))

    if action == "nick_changed":
        if userExists(nick):
            cur.execute("UPDATE userstats SET nick='{}' where nick='{}'".format(value, nick))
            logging.info("{} HEISST JETZT {}".format(nick, value))
    conn.close()  
    
if __name__ == "__main__":
    con = connection(IRCHOST, IRCPORT, IRCUSER, IRCNICK)
    con.connect()
    con.receive()
