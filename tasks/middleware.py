from django.utils import timezone
from pytz import timezone as pytz_tz

from .utils import get_client_ip, get_tzname_by_ip


class UserTimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('user_timezone', None)
        try:
            if tzname is None:
                ip = get_client_ip(request)
                print(ip)
                if ip:
                    tzname = get_tzname_by_ip(ip)
                    request.session['user_timezone'] = tzname
            if tzname:
                timezone.activate(pytz_tz.timezone(tzname))
            else:
                timezone.deactivate()
        except:
            pass
        return self.get_response(request)