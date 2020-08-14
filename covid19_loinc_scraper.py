'''
Author: Brandon Shelton
Last Update: 2020-08-14

Description:
    This script pulls the latest table of SARS-CoV-2 related lab results from
    the LOINC COVID-19 page.

    Every LOINC code that has 'SARS-CoV-2' in its description is considered
    confirmed when the results are positive. If 'SARS-CoV-2' is not found but
    the more general 'SARS' desription is found, then it is considered surveillance
    when positive. 'SARS-CoV-2' codes are listed as both confirmed and surveillance
    because a lab identification is considered surveillance if the test come back
    inconclusive or without a results indicator.

    Table is written out as .csv file into the user's specific path, as well as
    written out to Hive for more general consumption.

    Created as part of a CDSW job to update daily, at 12:20pm PST.
'''

#import the necessary packages
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# path to write output
path = '/home/cdsw/references/codes/'


# define the webscraping function
def loinc_update(write2):

    # get the html for the LOINC Pre-Release website
    url = 'https://loinc.org/sars-cov-2-and-covid-19/'
    r1 = requests.get(url)
    coverpage = r1.content
    soup = BeautifulSoup(coverpage, 'html.parser')

    # identify the table
    table = soup.find_all('tbody')[0].find_all('tr') # table body

    # populate the lists for each of the different elements listed directly below
    version = []
    code = []
    short_name = []
    descr = []

    for i in range(0, len(table)):
        td_tags = table[i].find_all('td')
        cd = td_tags[0].get_text()

        try:
            c = table[i].find_all('a', class_ = 'pre-code')[0].get_text()
        except IndexError:
            c = table[i].find_all('a', class_ = 'loinc-code')[0].get_text()

        sn = td_tags[11].get_text()
        d = td_tags[2].get_text()

        version.append(cd)
        code.append(c)
        short_name.append(sn)
        descr.append(d)

    # put LOINC list elements into single dataframe
    loincs = pd.DataFrame({'version': version,
                           'code': code,
                           'short_name': short_name,
                           'descr': descr})

    # filter for just SARS related LOINCs
    sars_cov2 = loincs[loincs['short_name'].str.contains('SARS')] \
        .reset_index(drop = True)

    # Make a two rows for every LOINC code one for a confirmed (positive) status
    # and one for a surveillance (test not performed) status.

    # only keep the SARS-CoV-2 specific tests as the ones capable of having
    # a confirmed for COVID-19.
    sars_cov2_positive = sars_cov2[sars_cov2['short_name'] \
        .str.contains('SARS-CoV-2')].reset_index(drop = True)
    sars_cov2_positive['case_type'] = 'confirmed'

    sars_cov2_tnp = sars_cov2
    sars_cov2_tnp['case_type'] = 'surveillance'

    # union the 'positive' and 'surveillance' records
    sars_cov2 = sars_cov2_positive.append(sars_cov2_tnp)

    sars_cov2['code_type'] = 'LOINC'
    sars_cov2 = sars_cov2[['case_type', 'code_type', 'code', 'descr', 'version']]
    sars_cov2 = sars_cov2.reset_index(drop = True)


    # write to csv in CDSW project
    sars_cov2.to_csv(path + 'sars_cov2_loinc_codes.csv',
                     index = False)


# run the function
loinc_update(path)
