# -*- coding: utf8 -*-
"""Data analysis module."""

from itertools import chain

from airflights.auxiliary_func import add_total_travel_time, get_flight_weights
from airflights.parser_xml import FILE_PATH, get_xml_tree


def get_all_flights():
    """Get list of all flights with total time flight.

    Returns:
        list: list of flights, each flight is represented by a dictionary.
    """
    root = get_xml_tree(FILE_PATH).getroot()
    all_flights = []

    for flights in root.xpath('//OnwardPricedItinerary/Flights'):
        all_flights.append(get_route(flights))

    return list(map(add_total_travel_time, all_flights))


def get_route(flights):
    """Return route from flights.

    Args:
        flights (object of class 'lxml.etree._Element'): an object containing
            a description of flights. every flight is a "Flight" tag.

    Returns:
        dict: "FLight" tags are generated in the route dictionary.
    """
    route = {}
    order = 0

    for flight in flights.iter('Flight'):
        flight_direction = {}
        order += 1

        for elem in flight.iter('*'):
            if elem.tag == 'Flight':
                continue
            if elem.text is not None:
                flight_direction[elem.tag] = elem.text.strip()

        route['flight{0}'.format(order)] = flight_direction

        route['Price'] = {
            'TicketPrice': flights.find(
                '../../Pricing/ServiceCharges[@ChargeType="TotalAmount"]',
            ).text,
            'Currency': flights.find('../../Pricing').attrib['currency'],
        }

    return route


def get_flights_sorted_price(flights, reverse=False):
    """Return a list of flights sorted by price.

    Args:
        flights (list): list of flights, each flight is represented
            by a dictionary.
        reverse (bool, optional): defines the sorting order,
            by default to False - ascending, if True sort in descending order.

    Returns:
        list: a list of flights sorted by price.
    """
    return sorted(
        flights,
        key=lambda flight: float(flight['Price']['TicketPrice']),
        reverse=reverse,
    )


def get_flights_sorted_time(flights, reverse=False):
    """Return a list of flights sorted by time.

    Args:
        flights ([type]): list of flights, each flight is represented
            by a dictionary.
        reverse (bool, optional): defines the sorting order,
            by default to False - ascending, if True sort in descending order.

    Returns:
        list: a list of flights sorted by time.
    """
    return sorted(
        flights,
        key=lambda flight: flight['TotalTravelTime'],
        reverse=reverse,
    )


def get_flights_filtered_direction(source, destination):
    """Return a list of flights sorted by directions.

    Args:
        source (str): name of city (airport) of departure.
        destination (str): name of city (airport) of arrival.

    Returns:
        list: a list of flights sorted by destination.
    """
    flights = get_all_flights()
    filtered_flights = []

    for flight in flights:
        source_in_flight = flight.get('flight1').get('Source')

        if flight.get('flight2'):
            second_flight = flight.get('flight2')
        else:
            second_flight = flight.get('flight1')

        if source_in_flight == source:
            if second_flight.get('Destination') == destination:
                filtered_flights.append(flight)

    return filtered_flights


def get_all_routes(return_set_airports=False):
    """Return all possible routes or a set of airport names.

        With an indication of the place of departure, transfer and destination
        or a set of airport names.

    Args:
        return_set_airports (bool): by default, False. Returns a list of
            dictionaries. The data type is a list.
            If True, it returns a set of airport names,
            such as {'DXB', 'BKK', '...', }. Data type set.

    Returns:
        list or set: list of routes, each route is represented by a dictionary
            of the form {'Source': ..., 'Transfer': ..., 'Destination': ...}.
            Set of airport names such as {'DXB', 'BKK', '...', }.
    """
    all_routes = []

    for flight in get_all_flights():
        source = flight.get('flight1').get('Source')
        destination = flight.get('flight1').get('Destination')

        if flight.get('flight2') is None:
            all_routes.append({
                'Source': source,
                'Destination': destination,
            })
        else:
            all_routes.append({
                'Source': source,
                'Transfer': destination,
                'Destination': flight.get('flight2').get('Destination'),
            })

    if return_set_airports:
        airports = (list(route.values()) for route in all_routes)
        return set(chain(*airports))

    all_routes = (tuple(route.items()) for route in all_routes)
    return [dict(route) for route in set(all_routes)]


def get_optimal_route(source, destination, count=10):
    """Return optimal flight routes by time and price.

    Args:
        source (str): name of city (airport) of departure.
        destination (str): name of city (airport) of arrival.
        count (int, optional): the number of flights to be returned.

    Returns:
        list: a list of optimal flights by time and price.
    """
    sort_flight_time = get_flights_sorted_time(get_flights_filtered_direction(
        source,
        destination,
    ))
    sort_flight_price = get_flights_sorted_price(get_flights_filtered_direction(
        source,
        destination,
    ))

    flight_weights = get_flight_weights(sort_flight_time, sort_flight_price)

    optimal_route = []
    for flight, _ in sorted(flight_weights, key=lambda pair: pair[1])[:count]:
        optimal_route.append(flight)

    return optimal_route
