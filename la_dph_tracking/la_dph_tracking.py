'''
This script appends daily updates from the L.A. County public health website
of various coronavirus counts.
Site: http://publichealth.lacounty.gov/media/Coronavirus/locations.htm

It uses html to check if the date of the page has been updated since the last update
of the file that continues to get appended. If the webpage date is later than
the maximum date on the file, then this scrapes, formats, and appends the webpage
content to the existing file. If the webpage date is not later than the maximum
date on the file, it simply notifies the developer that no update has occurred.

Author: Brandon Shelton
Last update: 2020-04-01
'''

# Set path to save output file and update log file
opath = 'covid-19/la_dph_tracking/'

#import the necessary packages
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from datetime import datetime
from pytz import timezone
import pytz


# Define the function
# ------------------------------------------------------------------------------

def county_covid_scraper():
    #bring in the existing collected dates of tracking
    last_df = pd.read_csv(opath + 'county_coronavirus_tracking.csv')

    # get the html for the LA County counter
    url = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'
    r1 = requests.get(url)
    coverpage = r1.content
    soup = BeautifulSoup(coverpage, 'html.parser')

    # get the date of the county website's last update
    caption = soup.find_all('caption')[0].get_text()
    month = caption.rsplit('/', 1)[0].rsplit(' ', 1)[1]
    day = re.sub('[^0-9]', '', caption.rsplit(month+'/', 1)[1][0:2])
    day = day.zfill(2)
    date = month + '-' + day
    date = date.zfill(5)

    '''
    If the date of the county website is greater than the max date in our tracker,
    then append our tracker with the county's lastest update.
    '''
    if date > max(last_df['date']):

        # Isolate the row elements and values
        table = soup.find_all('table', class_ = 'table table-striped table-bordered table-sm')[0]
        rows = table.find_all('td')

        lister = [x.get_text() for x in rows]
        ndata = pd.DataFrame({'rows': lister})
        ndata['count'] = ndata['rows'].shift(periods = -1)

        # only keep records where 'rows' contains alpha characters
        ndata = ndata[ndata['rows'].str.contains(('[a-zA-Z]'), regex = True)]
        ndata['rows'] = ndata['rows'].str.lower()

        # change '--' to zeros
        ndata['count'] = ndata['count'].replace('--', 0)

        # check these manually every day to make sure they remain consistent
        headers = ['deaths',
                   'age group',
                   'gender',
                   'hospitalization',
                   'city/community',
                   'under investigation']

        df = pd.DataFrame({'section': [], 'row_name': [], 'count': []})

        # loop through each 'headers' section in the html table
        for h in range(0, len(headers)):
            row_names = []
            row_amounts = []

            # loop through each row in the table and assign the appropriate section header
            for i in range(0, len(ndata)):
                field = ndata['rows'].iloc[i]
                count = ndata['count'].iloc[i]

                # skip all combinations of previously identified header/name/count combos
                if len(df[(df['section'].isin(['laboratory confirmed cases'] + headers[0:h]))
                          & (df['row_name'].isin([field]))
                          & (df['count'].isin([count]))]) > 0:
                      pass
                else:
                    # break loop if the header is in the field name and
                    # the header is not equal to the last header
                    if (headers[h] in field) & (headers[h] != headers[-1]):
                        break
                    else:
                        row_names.append(field)
                        row_amounts.append(count)

            # assign section names
            if len(df) == 0:
                section = ['laboratory confirmed cases'] * len(row_names)
            else:
                section = [headers[h-1]] * len(row_names)

            # create data section dataframe
            subdf = pd.DataFrame({'section': section,
                                  'row_name': row_names,
                                  'count': row_amounts})

            # append the section to the existing data frame
            df = df.append(subdf)

        # appropriately name the last section
        df = df.reset_index(drop = True)
        last_sec = df.index[df['row_name'].str.contains(headers[-1]) == True]
        last_section = last_sec[len(last_sec)-1]
        df.loc[last_section: len(df), 'section'] = headers[-1]

        # remove the rows that do not include numeric values in count
        df = df[~df['count'].isnull()]

        # add update date
        df['date'] = [date] * len(df)

        # format as much as possible
        df['section'] = df['section'].str.replace(' / ', '/')
        df['name_length'] = df['row_name'].map(len)
        df['row_name'] = np.where(df['name_length'] == 1, # remove special characters
                                  '',
                                  df['row_name'])
        df['row_name'] = df['row_name'].str.replace('*', '')
        df['row_name'] = df['row_name'].map(lambda x: x.lstrip('- '))
        df['count'] = df['count'].str.replace('*', '')

        # only keep rows with numbers in 'counts' column
        df = df[df['count'].str.isdigit() == True]
        # only keep rows that are not section headers (except 'under investigation')
        df = df[(df.apply(lambda x: x.section in x.row_name, axis=1) == False) \
                | (df['section'] == 'under investigation')]
        df['count'] = df['count'].astype(int)

        df = df[['date', 'section', 'row_name', 'count']]

        # combine the latest update with the rest
        final = last_df.append(df).sort_values(['section', 'row_name', 'date'])

        # Save the previous update, just in case something goes wrong with this one
        last_df.to_csv(opath + 'county_coronavirus_tracking_yesterday.csv',
                       index = False)

        # overwrite the existing file with the updates
        final.to_csv(opath + 'county_coronavirus_tracking.csv', index = False)
        print(f'L.A. County tracker updated with counts from {date}.')

        # log the time that this last update occurred
        exact_time = str(datetime.now().astimezone(timezone('US/Pacific')) \
            .replace(microsecond=0))[0:19]

        try: # tries to access the existing log and append update time to top
            log = open(opath + 'last_update_time.txt', 'r')
            log_txt = log.read()
            log.close()

            last_update_file = open(opath + 'last_update_time.txt', 'w')
            last_update_file.write(exact_time + '\n' + log_txt)

        except FileNotFoundError:
            last_update_file = open(opath + 'last_update_time.txt', 'w')
            last_update_file.write(exact_time)

        last_update_file.close()
        print(f'Collected at {exact_time}')


    # if no update yet
    else:
        exact_time = str(datetime.now().astimezone(timezone('US/Pacific')) \
            .replace(microsecond=0))[0:19]

        try: # tries to read the latest update date from the log, if exists
            last_update_time = open(opath + 'last_update_time.txt', 'r').read() \
                .split('\n', 1)[0]
            print(f'Last update occured at {last_update_time}')
            print(f'No new LA County coronavirus count updates as of {exact_time}')

        except FileNotFoundError:
            print(f'No new LA County coronavirus count updates as of {exact_time}')



# Execute the function
# ------------------------------------------------------------------------------
if  __name__ == '__main__':
    county_covid_scraper()
