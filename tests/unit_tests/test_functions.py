# -*- coding: utf8 -*-
"""Tests the functions of web service."""

from airflight.auxiliary_func import formatting_time
from airflight.data_analysis import (
    get_flights_filtered_direction,
    get_optimal_route,
)
from tests.unit_tests.checking_sorting import (
    get_median_price,
    get_median_time,
    is_correct_filtered_by_direction,
    is_correct_sort_by_price,
    is_correct_sorting_by_time,
)


def test_get_all_flights(all_flights):
    """Test of the function get_all_flights.

    Args:
        all_flights (fixture): a fixture function that returns a function that,
            when called, returns a list of flights, where each flight is
            represented by a dictionary
    """
    assert len(all_flights) == 200


def test_get_flights_sorted_price(all_flights):
    """Test of the function get_flights_sorted_price.

    Args:
        all_flights (fixture): a fixture function that returns a function that,
            when called, returns a list of flights, where each flight is
            represented by a dictionary
    """
    assert is_correct_sort_by_price(all_flights, reverse=False)
    assert is_correct_sort_by_price(all_flights, reverse=True)


def test_get_flights_sorted_time(all_flights):
    """Test of the function get_flights_sorted_time.

    Args:
        all_flights (fixture): a fixture function that returns a function that,
            when called, returns a list of flights, where each flight is
            represented by a dictionary.
    """
    assert is_correct_sorting_by_time(all_flights, reverse=False)
    assert is_correct_sorting_by_time(all_flights, reverse=True)


def test_get_flights_filtered_direction(all_flights, get_routes_in_parts):
    """Test of the function get_flights_filtered_direction.

    Args:
        all_flights (fixture): fixture function that returns a function that,
            when called, returns a list of flights, where each flight is
            represented by a dictionary.
        get_routes_in_parts (fixture): Returns each route from the list
            separately. Each route is represented by a dictionary,
            dictionary of the form:
            {'Source': ..., 'Transfer': ..., 'Destination': ...}.
    """
    assert is_correct_filtered_by_direction(all_flights, get_routes_in_parts)


def test_get_all_routes(all_flights, get_routes_in_parts):
    """Test of the function get_all_routes.

    Args:
        all_flights (fixture): fixture function that returns a function that,
            when called, returns a list of flights, where each flight is
            represented by a dictionary.
        get_routes_in_parts (fixture): Returns each route from the list
            separately. Each route is represented by a dictionary,
            dictionary of the form:
            {'Source': ..., 'Transfer': ..., 'Destination': ...}.
    """
    total_count_flights = len(all_flights)
    count_each_route = {}
    for route in get_routes_in_parts():
        direction = '{0}-{1}-{2}'.format(
            route['Source'],
            route.get('Transfer', None),
            route['Destination'],
        )
        if count_each_route.get(direction):
            count_each_route[direction] += 1
        else:
            count_each_route[direction] = 1

    assert sum(count_each_route.values()) == total_count_flights


def test_get_optimal_route(get_routes_in_parts):
    """Test of the function get_optimal_route.

    Args:
        get_routes_in_parts (fixture): Returns each route from the list
            separately. Each route is represented by a dictionary,
            dictionary of the form:
            {'Source': ..., 'Transfer': ..., 'Destination': ...}.
            represented by a dictionary {source, transfer, destination}.
    """
    for route in get_routes_in_parts():
        filtered_flight_direction = get_flights_filtered_direction(
            route.get('Source'),
            route.get('Destination'),
        )
        optimal_route = get_optimal_route(
            route.get('Source'),
            route.get('Destination'),
        )

        median_time_optimal_route = get_median_time(optimal_route)
        median_price_optimal_route = get_median_price(optimal_route)

        assert median_time_optimal_route <= get_median_time(
            filtered_flight_direction,
        )
        assert median_price_optimal_route <= get_median_price(
            filtered_flight_direction,
        )


def test_formatting_time(all_flights):
    """Test of the function get_formatting_time.

    Args:
        all_flights (fixture): a fixture function that returns a function that,
            when called, returns a list of flights, where each flight is
            represented by a dictionary.
    """
    is_str = True
    flights_with_formatting_time = formatting_time(all_flights)

    for flight in flights_with_formatting_time:
        if not isinstance(flight['TotalTravelTime'], str):
            is_str = False

    assert is_str
