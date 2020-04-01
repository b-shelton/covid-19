# L.A. County Department of Public Health: Confirmed COVID-19 Cases Tracker

### Purpose
This folder's [la_dph_tracking.py](https://github.com/b-shelton/covid-19/blob/master/la_dph_tracking/la_dph_tracking.py) script appends daily updates from the L.A. County public health website of various coronavirus counts. A job is scheduled to check the County webpage for updates at the top of every hour. Currently, the updates occur once per day.

L.A. County DPH Confirmed Tracking site: http://publichealth.lacounty.gov/media/Coronavirus/locations.htm

The .py script scrapes the html page to check if the date of the page has been updated since the last update of the file that continues to get appended. If the webpage date is later than the maximum date on the file, then the script scrapes, formats, and appends the webpage content to the existing file

### Contents
- [la_dph_tracking.py](https://github.com/b-shelton/covid-19/blob/master/la_dph_tracking/la_dph_tracking.py): The script that executes the update.
- [county_coronavirus_tracking.csv](https://github.com/b-shelton/covid-19/blob/master/la_dph_tracking/county_coronavirus_tracking.csv): The file that is updated daily to append the latest accumulated data to the previous dates.
  - Fields:
    - `date`: The update mm-dd, per the County's webpage. The page is currently being updated daily.
    - `section`: The County's table is broken down into different sections. This field notates what section the record belongs to.
    - `row_name`: Reflects the various row names of the County's webpage table.
    - `count`: The count of confirmed cases, as posted by the County's webpage. Please note that header (i.e., summary) are intentionally excluded from this file. To get the total number of confirmed cases for a given day, sum the `count`field where `section == "laboratory confirmed cases"`.
- [last_update_time.txt](https://github.com/b-shelton/covid-19/blob/master/la_dph_tracking/last_update_time.txt): Logs the update times for the county_coronvirus_tracking.csv file.
- [county_coronavirus_tracking_yesterday.csv](https://github.com/b-shelton/covid-19/blob/master/la_dph_tracking/county_coronavirus_tracking_yesterday.csv): Yesterday's update of the output file. The County has made changes to their webpage formatting, which may cause inaccurate results during an update. Retaining yesterday's output allows us to make the necessary web scraping updates and then re-run, once corrected. 
