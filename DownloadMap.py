import requests


def download():
    MAP_SQL_URL = 'https://ts20.x2.america.travian.com/map.sql'
    response = requests.get(MAP_SQL_URL)
    open("map", "wb").write(response.content)
