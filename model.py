import requests
from bs4 import BeautifulSoup


def get_float_from_tag(tag):
    """Transform string number with characters into float.

    Parameters
    ----------
    tag: bs4.element.Tag
        - Example: ["* X,YZW £"]

    Returns
    -------
    float
    """
    amount = []

    for element in tag.contents[0]:
        if element.isdigit() == True:

            amount.append(element)

    amount_str = ''.join(amount)
    
    return float(amount_str)


def get_tag_by_id(url, id_name):
    """Get bs4 tag by id_name.

    Parameters
    ----------
    url: str

    id_name: str

    Returns
    -------
    bs4.Element.Tag
    """
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    tag = soup.find(id = id_name)

    return tag