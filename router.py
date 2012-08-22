'''
Super simple routing!
'''
import re

routes = {}


def add_route(route, handler):
    route = get_route_regex(route)
    routes[route] = handler


def route(request):
    for route in routes:
        m = re.match(route, request.path)
        if m is not None:
            wc_index = route.find('.*')
            if wc_index > 0:  # Check if this is a wildcard route and extract the parameter
                param = request.path[(wc_index - 1):]
                return routes[route](request, param)  # Route the request to the handler including parameter
            else:
                return routes[route](request)  # Route the request to the handler

    return routes[get_route_regex('404')](request)


def get_route_regex(route):
    return '^' + route.replace('*', '.*') + '$'  # Make wildcard routes "regex friendly"
