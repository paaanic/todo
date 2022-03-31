from datetime import timedelta

from django import template


register = template.Library()

@register.filter(name='add_dt')
def add_dt(value, arg):
    """
    Add timedelta to datetime object.
    :param value: datetime object
    :param arg: specify timedelta object using xn object 
        where x is one of ['Y', 'M', 'D', 'h', 'm', 's'], 
        n - integer number to add. Add sign '-' before 'xn' to 
        decrease value
    :returns: 

    Example: {{ datetime|add_dt:"h1 m1" }}; 
             {{ datetime|add_dt:"-Y1 s10" }}
    """
    return value + timedelta(minutes=1)


