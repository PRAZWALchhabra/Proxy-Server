import os,sys,socket,time,re,copy
from netaddr import IPNetwork

authenticated = 0
superuser = 0

class CachedFile(object):
    def __init__(self,filename):
        self.filename = filename
        self.totalhits = 0
        self.lasthit = 0
        self.last2lasthit = 0

def server_thread(client_socket, client_address):
    global authenticated,superuser
    authenticated = 0

    request = client_socket.recv(1024) #receive 1024 bytes
    
    # Parse Request Server
    send_final = copy.deepcopy(request)
    send_final = send_final.decode().split('\n')
    send_final[0] = re.split('http://|/',send_final[0])
    send_final[0].pop(1)
    send_final[0][1] = '/'+send_final[0][1]
    send_final[0] = ''.join(send_final[0])
    rem = send_final[0].split('\r')
    rem.pop(1)
    send_final[0] = ''.join(rem)
    rem = send_final[0].find('HTTP')
    send_final[0] = send_final[0][:rem+4]+'/'+send_final[0][rem+4:]
    cur_temp_auth = copy.deepcopy(send_final[0])


    # USERNAME AND PASSWORD
    # Get Authentication Details

    auth_find_var = cur_temp_auth.find('?')
    pos_ok = cur_temp_auth.find('%')
    authent = cur_temp_auth[auth_find_var+1:pos_ok]
    print("AUTHENT",authent)

    fd = open("userlist.txt", "rb")
    data = fd.read()
    fd.close()
    USERNAMES = data.decode().split('\n')
    for lines in USERNAMES:
        print("LINE-->",lines,"AUTHENT-->",authent)
        if authent==lines:
            authenticated = 1
            if lines[1:6]=="admin":
                superuser = 1
    
    if authenticated==0:
        client_socket.send('Invalid Username and Password'.encode())
        client_socket.close()
        return    
    # AUTHENTICATED OR NOT
    
    cur_temp_auth = cur_temp_auth[0:auth_find_var] + cur_temp_auth[pos_ok+1:]
    print("extract",cur_temp_auth)
    send_final[0] = copy.deepcopy(cur_temp_auth)
    print("before join",send_final)
    send_fin = '\r\n'.join(send_final)+'\r\n\r\n'
    print(("client_request",send_fin))


    host = '' # any localhost
    port = -1   # standard number for http port
    cachefiles = []

    url = request.decode().split('\n')[0]
    url = url.split(' ')[1]

    http_pos = url.find('://')
    if http_pos == -1:
        temp = url
    else:
        temp = url[(http_pos+3):]
    
    # Find End Of Web Server
    webserver_pos = temp.find('/')
    if webserver_pos == -1:
        webserver_pos = len(temp)

    port_pos = temp.find(':')
    if port_pos == -1 or webserver_pos<port_pos:
        port = 80
        host = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        host = temp[:port_pos]

    print("Connect To:",host,port)

    cacheTimer = time.time() - 300

    # Clear Cached files bassed on time
    for files in cachefiles:
        if files.lasthit < cacheTimer:
            print("File "+files.filename+" Removed.")
            cachefiles.remove(files)
            # Delete From Directory Also
    
    for files in cachefiles:
        if host == files.filename:
            
            # Change Timers and Hits
            files.last2lasthit = files.lasthit
            files.lasthit = time.time()
            files.totalhits += 1
            
            # Change The Cached Files 
            fd = open(host,'r')
            cached_data = fd.read()
            client_socket.send(cached_data)
            print(" Cache Hit ")
            
            # Close the socket
            client_socket.close()
            break

    # If here , then no files in cache    
    # a new cachefile class initialise
    cachefiles.append(CachedFile(host))

    if superuser == 0:
        block = open('blacklist.txt','r')
        temp = block.readlines()
        addrs = [x.strip() for x in temp]
        for x in addrs:
            if host in IPNetwork(x):
                client_socket.send("ACCESS DENIED! IP Blocked!".encode())
                client_socket.close()
    try:
        server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.connect((host,port))
        server_socket.send(send_fin.encode())
        while True:
            data = server_socket.recv(1024) # receive 1024 bytes
            # print("Received "+len(data)+" bytes.") Gives Error
            temp = data.decode()
            if len(temp) <= 0:
                break
            client_socket.send(data)    
        server_socket.close()
        client_socket.close()
    except:
        if server_socket:
            server_socket.close()
        if client_socket:
            client_socket.close()
        print('Error!',sys.exc_info())
        sys.exit(1)
