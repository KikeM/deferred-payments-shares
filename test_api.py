import pytest

from salary import get_net_salary

def test_net_salary():

    expected = 1581.0

    result = get_net_salary(2000)

    assert expected == result