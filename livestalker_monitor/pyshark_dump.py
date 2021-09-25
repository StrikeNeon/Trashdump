import socket
import pyshark
import psutil
import time
from pysyge import GeoLocator
from ipwhois import IPWhois, exceptions
# import nmap
import pprint
import hashlib
import base64
import plotly.graph_objects as go


class WireSharkManager():

    def __init__(self):
        self.geodata = GeoLocator('./data/SxGeoCity.dat')
        self.addrs = psutil.net_if_addrs()
        self.interfaces = self.addrs.keys()
        self.hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(self.hostname)

    def make_hash_sha256(self, data_dict: dict):
        hasher = hashlib.sha256()
        hasher.update(repr(self.make_hashable(data_dict)).encode())
        return base64.b64encode(hasher.digest()).decode()

    def make_hashable(self, data_dict: dict):

        if isinstance(data_dict, (tuple, list)):
            return tuple((self.make_hashable(data) for data in data_dict))

        if isinstance(data_dict, (set, frozenset)):
            return tuple(sorted(self.make_hashable(data) for data in data_dict))

        if isinstance(data_dict, dict):
            return tuple(sorted((key, self.make_hashable(value)) for key, value in data_dict.items()))

        return

    def read_ethernet(self, packet_count: int = 10):
        # define interface
        networkInterface = "Ethernet"

        # define capture object
        capture = pyshark.LiveCapture(interface=networkInterface)

        print(f"listening on {networkInterface}")

        for packet in capture.sniff_continuously(packet_count=packet_count):
            # adjusted output
            try:
                # get timestamp
                localtime = time.asctime(time.localtime(time.time()))

                # get packet content
                protocol = packet.transport_layer   # protocol type
                src_addr = packet.ip.src            # source address
                src_port = packet[protocol].srcport   # source port
                dst_addr = packet.ip.dst            # destination address
                dst_port = packet[protocol].dstport   # destination port

                # output packet info
                yield (localtime, src_addr, src_port, dst_addr, dst_port, protocol)
            except AttributeError as e:
                # ignore packets other than TCP, UDP and IPv4
                pass

    def get_loc(self, packet_count: int = 10):
        packets = self.read_ethernet(packet_count)
        for localtime, src_addr, src_port, dst_addr, dst_port, protocol in packets:
            parsed_info = {}
            if src_addr != self.local_ip:
                try:
                    obj = IPWhois(src_addr)
                    parsed_info["whois"] = obj.lookup_whois()
                except exceptions.IPDefinedError:
                    continue

                location = self.geodata.get_location(src_addr, detailed=True)
                if location.get("info"):

                    detailed_info = location.get("info")

                    country_data = detailed_info.get("country")
                    parsed_info["country_name"] = country_data.get("name_en")
                    parsed_info["country_iso"] = country_data.get("iso")
                    parsed_info["country_lat"] = country_data.get("lat")
                    parsed_info["country_lon"] = country_data.get("lon")

                    city_check = location.get("city")
                    if city_check != "":
                        city_data = detailed_info.get("city")
                        parsed_info["city_name"] = city_data.get("name_en")
                        parsed_info["city_iso"] = city_data.get("iso")
                        parsed_info["city_lat"] = city_data.get("lat")
                        parsed_info["city_lon"] = city_data.get("lon")
            yield parsed_info


shark = WireSharkManager()
printer = pprint.PrettyPrinter(indent=1)

lon_points = []
lat_points = []

for info in shark.get_loc(100):
    print("location data")
    info["data_hash"] = shark.make_hash_sha256(info)
    printer.pprint(info)
    lon_points.append(info.get("city_lon") if info.get("city_lon") else info.get("country_lon"))
    lat_points.append(info.get("city_lat") if info.get("city_lat") else info.get("country_lat"))

fig = go.Figure(go.Scattermapbox(
    mode="markers",
    lon=lon_points,
    lat=lat_points,
    marker={'size': 10}))

fig.update_layout(
    margin ={'l':0,'t':0,'b':0,'r':0},
    mapbox = {
        'center': {'lon': 10, 'lat': 10},
        'style': "stamen-terrain",
        'center': {'lon': -20, 'lat': -20},
        'zoom': 1})

fig.show()

# nm = nmap.PortScanner()
# result = nm.scan(hosts="", arguments='-n -sP -PE -PA21,23,80,3389')
# print(result)
