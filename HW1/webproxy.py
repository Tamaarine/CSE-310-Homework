import socket as sk 

port = 5500
ip = '0.0.0.0' # Localhost

# Create our proxy server socket
proxySocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

# Reuse the 
proxySocket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEPORT, 1)

# Bind our socket to the ip and port 
proxySocket.bind((ip, port))

# Make it into listen mode with backlog queue size of 3
proxySocket.listen(1)

def fetch_file(filename):
    cache_file = fetch_from_cache(filename)

    if cache_file:
        print("Got file from cache")
        return cache_file
    else:
        # Fetch from server        
        print("Fetching from server")
        
        file_from_server = fetch_from_server(filename)
        

if __name__ == "__main__":
    while True:
        connection, addr = proxySocket.accept() # Block until connection is accepted
        print("Connection established")
        
        host = ""
        
        request = connection.recv(1024).decode()
        print(request)
        
        found_referer = False
        # First step figure out who the hell is the host
        splitted = request.split('\r\n')
        
        for line in splitted:
            if "Referer: " in line:
                port_index = line.find(f":{port}")
                host = line[port_index + 6:]
                print(host)
                host = host.replace("http://", "")
                
                found_referer = True
                break
                
        
        # Parse the request, taking away the first slash, and http or https
        parsed_line = request.split('\r\n')[0]
        parsed_line = parsed_line.split(' ')[1]
        parsed_line = parsed_line[1:]
        parsed_line = parsed_line.replace("http://", "")
        
        try:
            # try to open it from the cache
            cached_file = open(f"cache/{parsed_line.replace('/', '*')}.html", 'r')
            print("Cache hit if we reached here")
        
            cache_response = cached_file.read()
            
            header = "HTTP/1.1 200 OK\n\n"
            doctype_index = cache_response.find("<!doctype")
            
            if doctype_index == -1:
                html_index = cache_response.find("<html>") 
                response = header + cache_response[html_index:]
            else:
                response = header + cache_response[doctype_index:]
            
            # final_response = header.encode() + response
            
            connection.sendall(response.encode())
            print("Sent response to client")
            connection.close()
            continue
        except FileNotFoundError:
            print("File not found in cache hence retrieve from server")
            
            if not found_referer:
                # find the first slash
                first_slash = parsed_line.find('/')
                if first_slash == -1:
                    first_slash = len(parsed_line)
                
                # Get us the host if there is no referer
                host = parsed_line[:first_slash]
                
            # Second find the resource to locate
            first_slash = parsed_line.find('/')
            
            if found_referer:
                resource_to_locate = '/' + parsed_line      
            elif first_slash == -1 and parsed_line == host:
                resource_to_locate = '/'
            else:
                # incldue the slash
                resource_to_locate = parsed_line[first_slash:] 
            
            proxy_server_socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
            proxy_server_socket.settimeout(1)
            
            try:
                proxy_server_socket.connect((host, 80))
                
                header = f"GET {resource_to_locate} HTTP/1.1\r\nHost: {host}\r\n\r\n"
                print(header)
                
                # cache the file here, open up a new file if it doesn't exist
                cache_file = open(f"cache/{parsed_line.replace('/', '*')}.html", 'w+')
                
                proxy_server_socket.sendall(header.encode())
            
                while True:
                    data = proxy_server_socket.recv(1024)
                    cache_file.write(data.decode())
                    if len(data) == 0:
                        break
                    connection.sendall(data)
            except UnicodeDecodeError:
                print("Cannot decode certain unicode :(")
            except sk.timeout:
                print("Timed out/Finished fetching resources")    
                
            print("Closing connection")
            cache_file.close()
            connection.close()
            proxy_server_socket.close()