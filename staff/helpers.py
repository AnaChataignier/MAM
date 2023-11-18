import requests
from config import CHAVE_API_GOOGLE
from authentication.models import CustomUser
from .models import OrdemDeServico


def calcula_atraso_reagendamento(user):
    try:
        ordens_em_atraso = OrdemDeServico.objects.filter(
            staff=user,
            atraso_em_minutos__isnull=False,
            status__in=["Atenção", "Urgente", "Aguardando"],
            atraso_em_minutos__gt=0,
        )
        ordens_reagendar = OrdemDeServico.objects.filter(
            staff=user,
            status="Reagendar",
        )
        total_reagendar = len(ordens_reagendar)
        atrasos = len(ordens_em_atraso)
        return {"atrasos": atrasos, "total_reagendar": total_reagendar}
    except Exception as e:
        print(f"Erro ao calcular aviso: {e}")
        return {"atrasos": 0, "total_reagendar": 0}


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
