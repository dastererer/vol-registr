from .constants import PIZZERIA_KULTOWA, REGISTRATION_CLOSED


def registration_status(request):
    return {"registration_closed": REGISTRATION_CLOSED}


def sponsor_info(request):
    return {"sponsor": PIZZERIA_KULTOWA}
