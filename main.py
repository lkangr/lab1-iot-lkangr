print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json

import winrt.windows.devices.geolocation as wdg
import asyncio

locator = wdg.Geolocator()

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "nUEkJhzBZNXr3Vk4UmZ2"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


async def request_access_location():
    await locator.request_access_async()


async def get_current_location():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return pos.coordinate.latitude, pos.coordinate.longitude


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humi = 50
light_intensity = 100
counter = 0

asyncio.run(request_access_location())
latitude, longitude = asyncio.run(get_current_location())

while True:
    collect_data = {'temperature': temp, 'humidity': humi, 'light': light_intensity, 'longitude': longitude, 'latitude': latitude}
    temp += 1
    humi += 1
    light_intensity += 1
    latitude, longitude = asyncio.run(get_current_location())
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    time.sleep(10)