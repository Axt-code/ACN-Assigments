import socket
import sys
from bs4 import BeautifulSoup
import ssl
import os
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

def fetch_obj(host, port, url):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    if(port == 443):
        context = ssl.create_default_context()
        client_socket = context.wrap_socket(client_socket, server_hostname=host)
        
    
    request = f"GET {url} HTTP/1.1\r\nHost: {host}\r\n\r\n"
    
    print(f"Sending HTTP parallel request to {host}:{port}")
    client_socket.send(request.encode())
    
    # print(f"url : {url}")
    parsed_url = urllib.parse.urlparse(url)
    # print(f"parsed_url : {parsed_url}")
    
    # Receive and print the response
    byteResponse = b""
    
    client_socket.settimeout(10)
    
    try:
        while True:
            response_chunk = client_socket.recv(4096)
            # print("inside loop")
            if not response_chunk:
                break
            byteResponse += response_chunk
    except:
        pass
    
    # Process the HTTP response
    response_parts = byteResponse.split(b'\r\n\r\n', 1)
    
    if len(response_parts) == 2:
        headers, obj_data = response_parts
        status_line, *header_lines = headers.decode('utf-8').split('\r\n')
        status_code = status_line.split()[1].encode('utf-8')
        
        if status_code == b'200':
            obj_name = os.path.basename(parsed_url.path)
            
            # Save the image to a file
            with open(obj_name, 'wb') as obj_file:
                obj_file.write(obj_data)
            
            print(f"obj saved: {obj_name}")
            print()
            
        else:
            print(f"Failed to download image: {url}")
            print()
    else:
        print("Invalid HTTP response")
    
    client_socket.close()
    print("Parsing is Completed")
    
    

def send_http_request(host, port, path):
    
    print(f"Connecting directly to the web server at {host}:{port}")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    if(port == 443):
        context = ssl.create_default_context()
        client_socket = context.wrap_socket(client_socket, server_hostname=host)
        
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
    
    # Send the request to the server or proxy
    print(f"Sending HTTP request to {host}:{port}")
    client_socket.send(request.encode())

    # Receive and print the response
    byteResponse = b""
    
    client_socket.settimeout(5)
    
    try:
        while True:
            response_chunk = client_socket.recv(4096)
            # print("inside loop")
            if not response_chunk:
                break
            byteResponse += response_chunk
    except:
        pass
    
    client_socket.close()
    
    response_text = byteResponse.decode()
    
    soup = BeautifulSoup(response_text, 'html.parser')
    text = soup.get_text
    print(f"text : {text}")
    # print(body)
    
    object_tags=[]
    # handle image
    img_tags =soup.find_all("img")
    print("Number of img_tags : "+ str(len(img_tags)))
    if len(img_tags)!=0:
         for img in img_tags:
            img_src = img['src']
            object_tags.append(img_src)
            
    else:
        print("No img tags found on the web page.")
        print()
           
    # handle link
    link_tags = soup.find_all("a")
    print("Number of link_tags : "+ str(len(link_tags)))

    # handle script
    script_tags = soup.find_all("script")
    print("Number of script_tags: "+ str(len(script_tags)))
    if len(script_tags) != 0:
        for script in script_tags:
            if 'src' in script.attrs:
                script_src = script['src']
                object_tags.append(script_src)
                # print(f"External script source: {script_src}")
            else:
                pass
        
    else:
        print("No script tags found on the web page.")
        print()
       
   
   # handle icon
    icon_tags =soup.find_all("link", rel="shortcut icon") or soup.find_all("link", rel="icon")
    print("Number of icon_tags : "+ str(len(icon_tags)))
    if len(icon_tags)!=0:
         for icon in icon_tags:
            # Get the source (src) attribute of the img tag
            icon_src = icon.get('href')
            object_tags.append(icon_src)
    else:
        print("No icon tags found on the web page.")
        print()
        
    
    print(f"Total number of obj: {len( object_tags)}")
    
    max_threads = len( object_tags)
    with ThreadPoolExecutor(max_threads) as executor:
        for obj in object_tags:
            executor.submit(fetch_obj, host, port, obj)

        
    print("Parsing is Completed")

def main():
    if len(sys.argv) < 4:
        print("Give arguments as: python3 speedyClient.py <host> <port> <path> ")
        sys.exit(1)

    # print(f"Length od arguments: {len(sys.argv)}")
    host = sys.argv[1]
    port = int(sys.argv[2])
    path = sys.argv[3]
    
    send_http_request(host, port, path)

if __name__ == "__main__":
    main()
