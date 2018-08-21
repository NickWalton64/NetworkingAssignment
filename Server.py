import socket
from select import select
import datetime
import time

def server():
    """Main server loop, looks after the port inputs, checks if 
    sockets have recieved data, calls the translation sends the 
    response packet and closes the sockets"""
    loop = True
    port1 = input("Please Enter the value of port 1: ")
    port2 = input("Please Enter the value of port 2: ")
    port3 = input("Please Enter the value of port 3: ")
    if valid_port(int(port1), int(port2), int(port3)) == True:
        while loop:
            sockets = []
            port_bind(int(port1), sockets)
            port_bind(int(port2), sockets)
            port_bind(int(port3), sockets)
            print("Waiting For Connection")
            insock = select(sockets, [], [])[0]
            count = 0
            for socket_num in range(len(sockets)):  #loops through all sockets to see which was used
                if (str(insock[0])) == str(sockets[count]):
                    clientIP, port = insock[0].getsockname()
                count += 1
            used_sock = insock[0]
            dtreq, clientIP = used_sock.recvfrom(2048)
            dtreq = bytearray(dtreq)
            if valid_pkt(dtreq) == 1:
                date = datetime.datetime.now()
                trans_date, lang = lang_pick(port, port1, port2, port3, date, dtreq)  
                pkt_length = len(trans_date.encode('utf-8')) + 13
                dtres = dt_creator(pkt_length, trans_date, date, lang)
                used_sock.sendto(dtres, (clientIP))
                close_ports(sockets)
    else:
        print("The ports were the same values or outside boundries")
        
def lang_pick(port, port1, port2, port3, date, dtreq):
    """See which language was chosen to be translated to by port number"""
    if int(port) == int(port1):
        trans_date, lang = make_eng(date, dtreq[5])
    elif int(port) == int(port2):
        trans_date, lang = make_mao(date, dtreq[5])
    elif int(port) == int(port3):
        trans_date, lang = make_ger(date, dtreq[5])
    return trans_date, lang

def close_ports(sockets):
    """Closes the 3 open ports"""
    print("Sent DT Response")
    sockets[0].close()
    sockets[1].close()
    sockets[2].close()
    print("Sockets closed\n")    
    
        
def valid_port(port1, port2, port3):
    """Takes the port values and ensures they are within the range of
    Valid port numbers that are usable"""
    if port1 == port2 or port1 == port3 or port2 == port3:
        return False
    if port1 > 64000 or port2 > 64000 or port3 > 64000:
        return False
    if port1 < 1024 or port2 < 1024 or port3 < 1024:
        return False
    return True
    
        
def port_bind(port_num, sockets):
    """Binds a socket to a certain port"""
    try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Creates a new socket
            server_socket.bind(('', port_num)) #Attempts to bind the socket to the port
            sockets.append(server_socket) #Adds the open socket to the list of open sockets
    except:
        print("Failed to bind to chosen port/s")
    return sockets
        
        
def dt_creator(length, date, d_date, lang):
    """Creates the response paket that will be recieved and decoded by the client"""
    pkt = bytearray(length)
    pkt[0] = 0x49 #Magic Number
    pkt[1] = 0x7e #Magic Nuber
    pkt[3] = 0x02#Response Type
    pkt[5] = int((format(lang, '08b')), 2) #Language
    pkt[6] = int((format(d_date.year, '16b')[:8]), 2)
    pkt[7] = int((format(d_date.year, '16b')[8:]), 2)
    pkt[8] = int((format(d_date.month, '08b')), 2)
    pkt[9] = int((format(d_date.day, '08b')), 2)
    pkt[10] = int((format(d_date.hour, '08b')), 2)
    pkt[11] = int((format(d_date.minute, '08b')), 2)
    pkt[12] = int((format(length, '08b')), 2)
    en_date = date.encode('utf-8')
    count = 0
    for byte in range(length - 13):
        pkt[count + 13] = en_date[count] #Adds the encoded translation byte by byte to thye packet
        count += 1
    return pkt   
        
        
def make_eng(date, reqtype):
    """Takes take and time and required packet type and returns the
    spoken word description of date or time in English"""
    if hex(reqtype) == hex(0x01):
        months = ['January ', 'February ', 'March ', 'April ', 'May ', 'June ', 'July ', 'August ', 'September ', 'October ', 'November ', 'December ']
        spoken = "Today's date is " + months[date.month - 1] + str(date.day) + ', ' + str(date.year)
    else:
        if date.minute <= 9:
            spoken = "The current time is " + str(date.hour) + ":0" + str(date.minute) #Adds a 0 so three past ten shows 10:03 rather than 10:3
        else:
            spoken = "The current time is " + str(date.hour) + ":" + str(date.minute)
    return spoken, 1

def make_mao(date, reqtype):
    """Takes take and time and required packet type and returns the
    spoken word description of date or time in Maori"""    
    #Was unsure of what to do about the Maori characters that weren't displayed
    if hex(reqtype) == hex(0x01):
        months = ['Kohit¯atea ', 'Hui-tanguru ', 'Pout¯u-te-rangi ', 'Paenga-wh¯awh¯ ', 'Haratua ', 'Pipiri ', 'H¯ongongoi ', 'Here-turi-k¯ok¯a ', 'Mahuru ', 'Whiringa-¯a-nuku ', 'Whiringa-¯a-rangi ', 'Hakihea ']
        spoken = "Ko te ra o tenei ra ko " + months[date.month - 1] + str(date.day) + ', ' + str(date.year)
    else:
        if date.minute <= 9:
            spoken = "Ko te wa o tenei wa " + str(date.hour) + ":" + '0' + str(date.minute) #Adds a 0 so three past ten shows 10:03 rather than 10:3
        else:
            spoken = "Ko te wa o tenei wa " + str(date.hour) + ":" + str(date.minute)
    return spoken, 2

def make_ger(date, reqtype):
    """Takes take and time and required packet type and returns the
    spoken word description of date or time in German"""    
    #Was unsure of what to do about the Maori characters that weren't displayed
    if hex(reqtype) == hex(0x01):
        months = ['Januar ', 'Februar ', 'M¨arz ', 'April ', 'Mai ', 'Juni ', 'Juli ', 'August ', 'September ', 'Oktober ', 'November ', 'Dezember ']
        spoken = "Heute ist der " + str(date.day) + '. ' + months[date.month - 1] + str(date.year)
    else:
        if date.minute <= 9:
            spoken = "Die Uhrzeit ist " + str(date.hour) + ":" + '0' + str(date.minute) #Adds a 0 so three past ten shows 10:03 rather than 10:3
        else:
            spoken = "Die Uhrzeit ist " + str(date.hour) + ":" + str(date.minute)
    return spoken, 3
        
def valid_pkt(pkt):
    """Checks if the request packet sent by the client is valid or
    if the server should ignore it"""
    if hex(pkt[0]) != hex(0x49) or hex(pkt[1]) != hex(0x7e):
        print("Invalid 'Magic Number', dicarding Request")
        return 0
    elif hex(pkt[2]) != hex(0x00) or hex(pkt[3]) != hex(0x01):
        print("Invalid 'Packet Type', dicarding Request")
        return 0
    elif hex(pkt[4]) != hex(0x00) or (hex(pkt[5]) != hex(0x01) and hex(pkt[5]) != hex(0x02)):
        print("Invalid 'Request Type', dicarding Request")
        return 0
    return 1
    
    

server()