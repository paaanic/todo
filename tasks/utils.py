import requests

from django.conf import settings


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_tzname_by_ip(ip):
    api_key = settings.IPGEOLOCATION_API_KEY
    url = f'https://api.ipgeolocation.io/timezone?apiKey={api_key}&ip={ip}'
    response = requests.get(url)
    response_json = response.json()
    return response_json['timezone']

