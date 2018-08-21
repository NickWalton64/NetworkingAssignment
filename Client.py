import socket
from select import select

def client():
    """Main client function. Handles the socket creation, port error checking 
    and if the server has taken to long to respond"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = int(input("Enter a port number: "))
    #port = 1500 #Uncommented for faster testing
    server = input("Enter an IP address: ")
    #server = 'localhost' #Uncommented for faster testing
    pkttype = input("Enter 'date' for the date and 'time' for the time: ")
    #pkttype = 'time' #Uncommented for faster testing
    if port < 64000 and port > 1024:
        DtRequest = DtReqPkt(pkttype)
        s.settimeout(1)
        sockets = [s]
        if DtRequest == 0:
            return 'Invalid input for date or time. No capitals or spaces'
        s.sendto(DtRequest, (server, port))
        insock = select(sockets, [], [], 1) #Client waits for a response from the server
        if insock[0] != None:
            error_check(s)
        else:
            print("Connection timed out")
            s.close()
    else:
        print("Invalid port number")
        
def error_check(s):
    """Checks for impossible or unacceptable values caused by either
    the server sending the packet wrong, or packet corruption"""
    try:
        dtpkt = bytearray(s.recv(2048)) #Recievces the packet from the server 
        s.close() #closes the socket that recieved the response packet
        if hex(dtpkt[0]) != hex(0x49) or hex(dtpkt[1]) != hex(0x7e):
            print("Magic Number is incorrect, dicarding server response")
        elif hex(dtpkt[3]) != hex(0x02):
            print("Packet Type is incorrect, dicarding server response")
        elif hex(dtpkt[5]) != hex(0x01) and hex(dtpkt[5]) != hex(0x02) and hex(dtpkt[5]) != hex(0x03):
            print("Language Code is incorrect, dicarding server response")
        elif dtpkt[6] > 20:
            print("Year is greater than 2100, dicarding server response")
        elif dtpkt[8] < 1 or dtpkt[8] > 12:
            print("Month is greater than 12 or less than 1, dicarding server response")
        elif dtpkt[9] > 31 or dtpkt[9] < 1:
            print("Day is greater than 31 or less than 1, dicarding server response")
        elif dtpkt[10] > 23 or dtpkt[10] < 0:
            print("Hour is greater than 23 or less than 0, dicarding server response")
        elif dtpkt[11] > 59 or dtpkt[11] < 0:
            print("Minute is greater than 59 or less than 0, dicarding server response")
        elif len(dtpkt) != dtpkt[12]:
            print("Length is incorrect, dicarding server response")
        else:
            print(dtpkt[13:].decode('utf-8'))
            print("Magic number: " + hex(dtpkt[0]) + (hex(dtpkt[1]))[2:])
            print("Packet Type: " + (hex(dtpkt[3]))[2:])
            print("Language: " + (hex(dtpkt[5]))[2:])
            year = str(bin(dtpkt[6])[2:] + bin(dtpkt[7])[2:])
            print("Year:", int(year, 2))
            print("Month:", int(bin(dtpkt[8]), 2))
            print("Day:", int(bin(dtpkt[9]), 2))
            print("Hour:", int(bin(dtpkt[10]), 2))
            print("Minute:", int(bin(dtpkt[11]), 2))
            print("Length of the Packet:", int(bin(dtpkt[12]), 2), "bytes")
    except:
        print("Invalid socket, the choosen port was not open on the server")
        print("or some of the packet contents could not be displayed")
    
def DtReqPkt(datapkt):
    """Creates the request packet to be sent to the server"""
    DtRequest = bytearray(6)
    DtRequest[0] = 0x49 #Magic Number
    DtRequest[1] = 0x7e #Magic Number
    DtRequest[3] = 0x01 # Request Type
    if datapkt == 'date':
        DtRequest[5] = 0x01 #Date
    elif datapkt == 'time':
        DtRequest[5] = 0x02 #Time
    else:
        return 0
    return DtRequest
    

client()