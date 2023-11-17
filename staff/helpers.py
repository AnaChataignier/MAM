import requests
from config import CHAVE_API_GOOGLE
from authentication.models import CustomUser


def obter_lat_lng_tecnicos():
    tecnicos = CustomUser.objects.filter(groups__name="Técnico")
    coordenadas_tecnicos = []

    for tecnico in tecnicos:
        endereco = f"{tecnico.endereco.rua}, {tecnico.endereco.numero}, {tecnico.endereco.bairro}, {tecnico.endereco.cidade}, {tecnico.endereco.estado}, {tecnico.endereco.cep}"

        # Geocodificar o endereço para obter as coordenadas
        endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": endereco,
            "key": CHAVE_API_GOOGLE,  # Substitua pela sua chave de API do Google Maps
        }
        response = requests.get(endpoint, params=params)

        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                location = data["results"][0]["geometry"]["location"]
                lat_lng = (location["lat"], location["lng"])
                coordenadas_tecnicos.append(lat_lng)

    return coordenadas_tecnicos


def obter_lat_lng_endereco(endereco):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": endereco,
        "key": CHAVE_API_GOOGLE,  # Substitua pela sua chave de API do Google Maps
    }
    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            lat_lng = (location["lat"], location["lng"])
            return lat_lng

    return None
