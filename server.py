import json
import BaseHTTPServer
import requests
import collections
import struct
import base64

def ejercicio1(origin, destiny):
    print "Ruta desde %s a %s" % (origin, destiny)
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=(origen)&destination=(destino)&key=AIzaSyDm3w4oPw82M8upaATU0IY5Sm_-tNvaXp8"
    final_url = url.replace("(origen)", origin, 1)
    final_url = final_url.replace("(destino)", destiny, 1)
    r = requests.post(final_url, None)
    get_json = json.loads(r.text)
    if get_json["status"] != "OK":
        return -1
    directions = collections.defaultdict(list)
    start_location = get_json["routes"][0]["legs"][0]["start_location"]
    directions["ruta"].append({"lat": start_location["lat"], "lon": start_location["lng"]})
    parsed = get_json["routes"][0]["legs"][0]["steps"]
    for direction in parsed:
        lat = direction["end_location"]["lat"]
        lng = direction["end_location"]["lng"]
        directions["ruta"].append({"lat":lat, "lon":lng})
    return json.dumps(directions)

def ejercicio2(origin):
    print "Restaurantes cerca de %s" % origin
    coord_url = "https://maps.googleapis.com/maps/api/geocode/json?address=(origen)&key=AIzaSyDXvf09KDyp0cTk5nroClhViAJBa2fwVRk"
    r = requests.post(coord_url.replace("(origen)", origin, 1), None)
    get_json = json.loads(r.text)
    if get_json["status"] != "OK":
        return -1
    final_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=lat,lng&radius=500&type=restaurant&key=AIzaSyDXvf09KDyp0cTk5nroClhViAJBa2fwVRk"
    lat = get_json["results"][0]["geometry"]["location"]["lat"]
    lng = get_json["results"][0]["geometry"]["location"]["lng"]
    print "Lat %s, Lng: %s" % (lat, lng)
    final_url = final_url.replace("lat", str(lat), 1)
    final_url =  final_url.replace("lng", str(lng), 1)
    r = requests.post(final_url, None)
    get_json = json.loads(r.text)
    if get_json["status"] != "OK":
        return -1
    get_json = get_json["results"]
    directions = collections.defaultdict(list)
    for direction in get_json:
        lat = direction["geometry"]["location"]["lat"]
        lng = direction["geometry"]["location"]["lng"]
        name = direction["name"]
        directions["restaurantes"].append({"nombre":name,"lat":lat,"lon":lng})
    return json.dumps(directions)

def ejercicio3(data):
    arr = data.decode('base64')
    width = struct.unpack('<%dH' % 2, arr[18:22])[0]
    height = struct.unpack('<%dH' % 2, arr[22:26])[0]
    bpp = struct.unpack('<%dH' % 1, arr[28:30])[0]
    starting_byte = struct.unpack('<%dH' % 2, arr[10:14])[0]
    print "Len %s\t|\tWidth %s\t|\tHeight %s\t|\tBPP %s\t|\tOffset %s" % (len(arr), width, height, bpp, starting_byte)
    final_arr = bytearray(arr[:starting_byte])
    x = 0
    if bpp == 32:
        for pixel in arr[starting_byte::4]:
            if x+starting_byte+3 < len(arr):
                r = struct.unpack('B', arr[x+starting_byte+1])[0]
                g = struct.unpack('B', arr[x+starting_byte+2])[0]
                b = struct.unpack('B', arr[x+starting_byte+3])[0]
                grey_value = (r + g + b) / 3
                final_arr.append(b'\xFF')
                final_arr.append(grey_value)
                final_arr.append(grey_value)
                final_arr.append(grey_value)
                x += 4
    elif bpp == 24:
        for pixel in arr[starting_byte::3]:
            if x+starting_byte+2 < len(arr):
                r = struct.unpack('B', arr[x+starting_byte])[0]
                g = struct.unpack('B', arr[x+starting_byte+1])[0]
                b = struct.unpack('B', arr[x+starting_byte+2])[0]
                grey_value = (r + g + b) / 3
                final_arr.append(grey_value)
                final_arr.append(grey_value)
                final_arr.append(grey_value)
                x += 3
    else:
        return -1

    return base64.b64encode(final_arr)

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(s):
        content_len = int(s.headers.getheader('content-length', 0))
        post_body = json.loads(s.rfile.read(content_len))
        if s.path == "/ejercicio1":
            try:
                r = ejercicio1(post_body["origen"], post_body["destino"])
            except Exception, err:
                print err
                s.send_response(400)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write("{\"error\":\"no se especifico origen o destino\"}")
                return
            if r == -1:
                s.send_response(500)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write("{\"error\":\"no se encontro la direccion\"}")
            else:
                s.send_response(200)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write(r)
        elif s.path == "/ejercicio2":
            try:
                r = ejercicio2(post_body["origen"])
            except Exception, err:
                print err
                s.send_response(400)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write("{\"error\":\"no se especifico origen\"}")
                return
            if r == -1:
                s.send_response(500)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write("{\"error\":\"no se encontro la direccion\"}")
            else:
                s.send_response(200)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write(r)
        elif s.path == "/ejercicio3":
            try:
                r = ejercicio3(post_body["data"])
                name = post_body["nombre"]
            except Exception, err:
                print err
                s.send_response(400)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write("{\"error\":\"no se especifico origen\"}")
                return
            if r == -1:
                s.send_response(500)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                s.wfile.write("{\"error\":\"error modificando el archivo. Es de 24 o 32 bits por pixel?\"}")
            else:
                s.send_response(200)
                s.send_header("Content-type", "application/json")
                s.end_headers()
                data = collections.defaultdict(list)
                data["nombre"] = name.replace(".bmp", "(blanco y negro).bmp", 1)
                data["data"] = r
                s.wfile.write(json.dumps(data))
        else:
            s.send_response(500)
            s.send_header("Content-type", "application/json")
            s.end_headers()
            s.wfile.write("{}")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(("localhost", 8080), MyHandler)
    print "Server Started"
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print "Server Stopped"
