import time

import numpy as np
import pandas as pd
from tqdm import tqdm as tqdm

from model import get_float_from_tag, get_tag_by_id

URL_TEMPLATE = "https://neuvoo.es/calculadora-de-impuesto/?iam=&uet_calculate=calculate&salary={amount}&from=month&region=Cataluña"

def get_multiplier(pct):
    """Compute value multiplier.
    """
    if np.isclose(pct, 0.0):
        return 0.0
    elif np.isclose(pct, 0.25):
        return 1.0
    elif np.isclose(pct, 0.5):
        return 1.5
    elif np.isclose(pct, 0.75):
        return 2.0
    else:
        raise ValueError(f"Not implemented for pct = {pct}")


def compute_compensation(gross, pct):
    """Compute the new gross salary and 
    the amount to convert to shares. 

    Parameters
    ----------
    gross: float

    pct: float

    Returns
    -------
    gross_new: float
    
    compensation: float
    """    
    gross_new = gross * (1.0 - pct)
    
    multiplier = get_multiplier(pct)
    
    compensation = gross * pct * multiplier
    
    return gross_new, compensation


def compute_shares(amount, price):
    return np.floor(amount / price)


def compute_shares_net_value(shares, price):
    """Compute shares value after taxes.

    Assuming 21% taxes proxy.

    Notes
    -----
    Assumes initial price was zero. 
    """
    return shares * price * (1.0 - 0.21)


def get_net_salary(gross_salary):
    """Get the monthly net salary from the gross monthly salary.

    Parameters
    ----------
    gross_salary: float

    Returns
    -------
    float

    Notes
    -----
    Source: https://neuvoo.es/calculadora-de-impuesto/
    """
    # Get the url correctly parsed
    url = _set_url(gross_salary=gross_salary)

    # Get the tag
    tag = get_tag_by_id(url = url, id_name="net_pay")

    net_salary = get_float_from_tag(tag)

    return net_salary

def compute_yearly_value(gross = 2000, pct = 0.25, price = 50.03, reduction_months = ["APR", "MAY", "JUN"], ):
    """Compute monthly gross and net value for a given entry price and pct reduction. 

    Parameters
    ----------
    pct: float

    price: float

    reduction_months: list of str

    Returns
    -------
    pd.DataFrame
        - Index: ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
                  "JUL", "AGU", "SEP", "OCT", "NOV", "DEC"]
        - Columns: ["salaryGross", "salaryNet", "sharesGross", 
                    "sharesNet", "pct", "price"]
    """
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AGU", "SEP", "OCT", "NOV", "DEC"]

    salary_months_df = pd.DataFrame(data = 0.0, index = months, 
                                    columns = ["salaryGross", "salaryNet", 
                                               "sharesGross", "sharesNet",
                                               "pct", "price"])

    # Set reduction
    _reduction = pct
    _price     = price

    salary_months_df.loc[:, "pct"]   = 0.0
    salary_months_df.loc[:, "price"] = _price

    for month in reduction_months:
        salary_months_df.loc[month, "pct"] = _reduction

    for month in tqdm(months):

        # Compute gross and net salary
        _pct = salary_months_df.loc[month, "pct"]

        _gross, _compenstion = compute_compensation(gross = gross, pct = _pct)

        salary_months_df.loc[month, "salaryGross"] = _gross
        salary_months_df.loc[month, "salaryNet"]   = get_net_salary(_gross)

        # Compute shares and value
        _price_shares = salary_months_df.loc[month, "price"]
        shares = compute_shares(amount=_compenstion, price=_price_shares)

        salary_months_df.loc[month, "sharesGross"] = shares * _price_shares
        salary_months_df.loc[month, "sharesNet"]   = compute_shares_net_value(shares, _price_shares)

        # Prevent problem when scraping the website
        time.sleep(0.5)

    # Polish data details
    salary_months_df = salary_months_df.round(2)
    salary_months_df.name = "pct_" + str(_reduction)
    salary_months_df.index.name = "month"

    return salary_months_df


def _set_url(gross_salary):

    _gross_salary = int(gross_salary)

    url = URL_TEMPLATE.format(amount = _gross_salary)

    return url
