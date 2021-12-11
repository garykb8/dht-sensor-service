# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import adafruit_dht
from typing import Optional
from fastapi import FastAPI, HTTPException
from aiocache import Cache, caches

app = FastAPI()
caches.set_config({
    'default': {
        'cache': "aiocache.SimpleMemoryCache",
        'serializer': {
            'class': "aiocache.serializers.StringSerializer"
        }
    }
})

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)


@app.get('/api/temperature')
async def get_temperature():
    cache = caches.get('default')
    try:
        temperature_c = dhtDevice.temperature
        # temperature_f = temperature_c * (9 / 5) + 32
        # humidity = dhtDevice.humidity
        await cache.set('temp', temperature_c)
        return {
            "temperature": temperature_c,
            # "humidity": humidity
        }
    except Exception as error:
        cachedTemp = await cache.get('temp')
        if cachedTemp is not None:
            return {
                "temperature": int(cachedTemp, base=10),
            }
        else:
            raise HTTPException(status_code=400, detail=error.args[0])


@app.get('/api/humidity')
async def get_humidity():
    cache = caches.get('default')
    try:
        humidity = dhtDevice.humidity
        await cache.set('hum', humidity)
        return {
            "humidity": humidity
        }
    except Exception as error:
        cachedHum = await cache.get('hum')
        if cachedHum is not None:
            return {
                "humidity": float(cachedHum)
            }
        else:
            raise HTTPException(status_code=400, detail=error.args[0])


# if __name__ == "__main__":
#     uvicorn.run(app)

# while True:
#     try:
#         # Print the values to the serial port
#         temperature_c = dhtDevice.temperature
#         temperature_f = temperature_c * (9 / 5) + 32
#         humidity = dhtDevice.humidity
#         print(
#             "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
#                 temperature_f, temperature_c, humidity
#             )
#         )

#     except RuntimeError as error:
#         # Errors happen fairly often, DHT's are hard to read, just keep going
#         print(error.args[0])
#         time.sleep3(3.0)
#         continue
#     except Exception as error:
#         dhtDevice.exit()
#         raise error

#     time.sleep(3.0)
