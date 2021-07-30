import socket
import pyshark
import psutil
import time
from pysyge import GeoLocator
from ipwhois import IPWhois, exceptions
# import nmap
import pprint


printer = pprint.PrettyPrinter(indent=1)
geodata = GeoLocator('./data/SxGeoCity.dat')
addrs = psutil.net_if_addrs()
interfaces = addrs.keys()
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(local_ip)


def read_ethernet(packet_count: int = 10):
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
        print(" ")


read_ethernet(100)
for localtime, src_addr, src_port, dst_addr, dst_port, protocol in read_ethernet():
    if src_addr != local_ip:
        print(f"{localtime} IP {src_addr}:{src_port} <-> {dst_addr}:{dst_port} ({protocol})")
        try:
            obj = IPWhois(src_addr)
            res = obj.lookup_whois()
            print("basic whois")
            printer.pprint(res)
        except exceptions.IPDefinedError as IPDEFerror:
            print(IPDEFerror)
            continue

        location = geodata.get_location(src_addr, detailed=True)
        parsed_info = {}
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
        print("location data")
        printer.pprint(parsed_info)

# nm = nmap.PortScanner()
# result = nm.scan(hosts="", arguments='-n -sP -PE -PA21,23,80,3389')
# print(result)
