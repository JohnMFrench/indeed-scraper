import argparse
import matplotlib as plt
import pandas as pd
from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import bs4
import requests

###############################################################
# Define class that will represent job card in indeed search result
###############################################################


class JobPost:
    def __init__(self, job_id, job_title, job_company, job_salary, job_date_posted, job_company_link):
        self.job_id = job_id
        self.job_title = job_title
        self.job_company = job_company
        self.job_date_posted = job_date_posted
        self.job_company_link = job_company_link
        self.job_salary = job_salary

    def toString(self):
        print(self.job_title)
        print(self.job_company)
        print(self.job_date_posted)


###############################################################
# PARSE ARGUMENTS FROM THE CLI AND SET STATE APPROPRIATELY
###############################################################
parser = argparse.ArgumentParser()
parser.add_argument("-d", help="Pull latest data on indeed server")
parser.add_argument("-job", help="Specify a job")
parser.add_argument("-n", help="The number")
parser.add_argument("-comp", help="Limit search results to paid positions")
args = parser.parse_args()

CompFiltered = False

if args.job is not None:
    job = "none specified"
    job_query = args.job or "data-analyst"

if args.comp is not None:
    CompFilter = True

# CREATE PAGE REQUESTS WITH CUSTOM FIELDS
#URL = "https://www.indeed.com/jobs?q=" + job_query
# INCLUDE THE NO COLLEGE DEGREE FILTER
URL2 = "https://www.indeed.com/jobs?q=" + job_query + \
    "%20no%20degree%20%2460%2C000&sc=0kf%3Aattr(FCGTU%7CQJZM9%7CUTPWG%252COR)%3B&vjk=e6db7da96543b7b6"

# LOAD THE WEBPAGE OR READ FROM HTML FILE
if(args.d == "pull"):
    html = urllib.request.urlopen(URL2).read()
else:
    html = open("pass1.html", "r", encoding="utf8")
soup = BeautifulSoup(html, "html.parser")

# SAVE ANOTHER PASS
# with open("pass1.html", "wb") as f:
#  f.write(soup.encode(formatter="html"))

job_lis = soup.find("ul", "jobsearch-ResultsList")
#print(f'found {len(job_lis)} in document')

# SEPARATE VALUES RETURNED INTO DIVS THAT CONTAIN BOTH
# .jobCard_mainContent AND .jobCardShelfContainer
result_card_list = soup.find_all("result")

#print(f'found {len(result_card_list)} tags')

# FIND THE PARENT TAGS BY CSS CLASS
results_list = soup.find_all("div", class_="cardOutline")
#print(f"Found {len(results_list)} job search results items \n")

# ITERATE THROUGH THE <table> TAGS THAT CONTAIN JOB DATA
for result in results_list:

    # EXTRACT THE SALARY IF IT IS SHOWN ON THE JOBCARD
    salary_divs = result.find("div", "salary-snippet-container")
    salary = "Compensation Not Listed"
    if salary_divs is not None:
        salary_sub_div = salary_divs.find("div")
        for s in salary_sub_div.strings:
            if s[0] == '$':
                salary = s

    # EXTRACT THE JOB TITLE
    title_h2 = result.find_all("h2", class_="jobTitle")
    a_tag = title_h2[0].find("a")
    title = a_tag.string

    # EXTRACT JOB ID FROM DATA ATTRIBUTE
    job_id = a_tag["data-jk"]

    # EXTRACT THE COMPANY
    company_span = result.find_all("span", class_="companyName")
    for span in company_span:
        if span.string[0] != '+':
            company = span.string
        else:
            company = span[1].string

    # EXTRACT THE URL FOR THE JOB APPLICATION
    company_link = result.find("a", class_="jcs-JobTitle")['href']
    company_link = 'http://indeed.com' + company_link

    # EXTRACT THE LOCATION
    location_div = result.find("div", "companyLocation")
    location = location_div.string

    # EXTRACT THE TIME THE JOB WAS POSTED date_posted =
    date_posted = ""
    date_spans = result.find_all("span", class_="date")
    for d_span in date_spans:
        if (d_span.string is not None):
            date_posted = d_span.string

    # jobsearch-HiringInsights-entry--text

    ###############################################################
    # SCRAPING INDIVIDUAL PAGES
    ###############################################################

    try:
        job_page_url = "https://www.indeed.com/viewjob?jk=" + job_id
        print(job_page_url)
        job_html = urllib.request.urlopen(job_page_url).read()
        job_soup = BeautifulSoup(job_html, "html.parser")
        # IF THE SINGLE PAGE VIEW OF THE JOB, EXTRACT MORE DATA
        posted = job_soup.find(
            "span", class_="jobsearch-HiringInsights-entry--text").string
        print(posted)
        job = JobPost(job_id, title, company, salary,
                      date_posted, company_link)
        job.toString()

    except Exception as e:
        print(e)
