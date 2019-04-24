from json import loads
import socket
import sys

# check correct number of arguments
if (len(sys.argv) != 3):
    print("Wrong number of arguments.", file=sys.stderr)
    sys.exit(1)

# load input info and prepare message to be sent to the server
KEY = sys.argv[1]
CITY = sys.argv[2]

if (CITY == ""):
    print("Location is required.", file=sys.stderr)
    sys.exit(1)

HOST = "api.openweathermap.org"
PORT = 80
MSG = "GET /data/2.5/weather?q=" + CITY + "&appid=" + KEY + "&units=metric HTTP/1.1\r\nHost: " + HOST + "\r\n\r\n"

# create a new socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# try to connect to the server, send the request and receive data
try:
    s.connect((HOST, PORT))
    s.sendall(MSG.encode())
    data = str(s.recv(1024))
except:
    print("Connection failed.", file=sys.stderr)
    sys.exit(1)

# if no data is received, exit with error
if (len(data) == 0):
    print("No data received.", file=sys.stderr)
    sys.exit(1)

# handle HTTP errors
httpCode = int(data[11:14]) # extract HTTP status code from received data
if (httpCode != 200):
    codes = {400: 'Bad request.', 401: 'Unauthorized. (wrong key)',
             403: 'Forbidden.', 404: 'City not found.',
             500: 'Internal Server Error', 503: 'Service unavailable.'}
    errmsg = codes.get(httpCode, 'Check given error code.') # message for other error codes
    print("Server returned error " + str(httpCode) + ": " + errmsg, file=sys.stderr)
    sys.exit(1)

# get correct form of JSON data
data = "{" + data.split('{', 1)[1]                  # remove HTTP info from the beginning of data
data = data[:-1]                                    # remove apostrophe from the end of received data
data = data.translate({ord(i): None for i in '[]'}) # remove [ and ] symbols from JSON
data = loads(data)                                  # load data from JSON

# output received data
print(data["name"])
print(data["weather"]["description"])
print("temp: " + str(data["main"]["temp"]) + "°C")
print("humidity: " + str(data["main"]["humidity"]) + "%")
print("pressure: " + str(data["main"]["pressure"]) + " hPa")
print("wind-speed: " + str(round(data["wind"]["speed"] * 3.6, 2)) + " km/h")
print("wind-deg: ", end="") # print without \n
if ("deg" in data["wind"]):
    print(str(data["wind"]["deg"]))
else:
    print("-")
