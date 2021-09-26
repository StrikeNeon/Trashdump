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

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output

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


# nm = nmap.PortScanner()
# result = nm.scan(hosts="", arguments='-n -sP -PE -PA21,23,80,3389')
# print(result)


shark = WireSharkManager()
printer = pprint.PrettyPrinter(indent=1)
app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div([
        html.H4('Live network monitor'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=10*1000, # in milliseconds
            n_intervals=1
        )
    ])
)


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    lon_points = []
    lat_points = []
    cities = []

    # Collect some data
    for info in shark.get_loc(10):
        # print("location data")
        info["data_hash"] = shark.make_hash_sha256(info)
        printer.pprint(info)
        lon_points.append(info.get("city_lon") if info.get("city_lon") else info.get("country_lon"))
        lat_points.append(info.get("city_lat") if info.get("city_lat") else info.get("country_lat"))
        cities.append(f'{info.get("city_name") if info.get("city_name") else info.get("country_name")+" city undefined"}')

    # Create the graph with subplots
    fig = go.Figure(go.Scattergeo(
                    mode="markers",
                    lon=lon_points,
                    lat=lat_points,
                    marker={'size': 8}))
    fig.update_geos(scope="world", bgcolor="#2b2b2b", projection_type="orthographic", landcolor="black", showocean=True, oceancolor="#5c0000",  showcountries=True, countrycolor="#850000")
    fig.update_traces(marker_color="#ff0000", marker_symbol="cross", text=cities, selector=dict(type='scattergeo'))
    fig.update_layout(height=1000, margin={"r":0,"t":0,"l":0,"b":0})

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
