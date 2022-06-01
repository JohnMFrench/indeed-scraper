import argparse
import csv
from re import A
import matplotlib as plt
import pandas as pd
from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import bs4
import requests
from urllib.parse import quote

###############################################################
# Define class that will represent job card in indeed search result
###############################################################


class JobPost:
    def __init__(self, job_id, job_title, job_company, job_salary, location, job_date_posted, job_company_link):
        self.job_id = job_id
        self.job_title = job_title
        self.job_company = job_company
        self.job_date_posted = job_date_posted
        self.job_company_link = job_company_link
        self.job_salary = job_salary
        self.location = location

    def printF(self):
        print(self.job_title)
        print(f"{self.job_company} at {self.location}")
        print(self.job_date_posted)
        print(self.job_salary)
        print(self.job_company_link)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

###############################################################
# Define class that will represent job card in indeed search result
###############################################################

jobs_post_list = []

###############################################################
# PARSE ARGUMENTS FROM THE CLI AND SET STATE APPROPRIATELY
###############################################################
parser = argparse.ArgumentParser()
parser.add_argument("-d", help="Pull latest data on indeed server")
parser.add_argument("-job", help="Specify a job")
parser.add_argument("-n", help="The number")
parser.add_argument("-comp", help="Limit search results to paid positions")
parser.add_argument("-l", help="Specify a location for the job search")
parser.add_argument("-deg", help="Specify which education level indeed will fuzzy search this")
args = parser.parse_args()

# PARSE JOB ARGUMENT
if args.job is None:
    print("defaulting job search to data analyst")
    job_query = quote("data-analyst")
else:
    #print("detected {args.job} as jobs argument")
    print(args.job)
    job_query = quote(args.job)

# PARSE COMPENSATION FILTER
CompFiltered = False
if args.comp is not None:
    CompFilter = True

# PARSE NUMBER OF RETURNS FILTER
if args.n is None:
    print("detected n arg")
    n = 10
else:
    n = args.n
    n = int(n)  # convert the n flag to an int for comparison
    print(f"detected {n} as arg")

# PARSE DEGREE LEVEL
if args.deg is None:
    deg = quote("no degree")
else:
    deg = quote(args.deg)

# CREATE PAGE REQUESTS WITH CUSTOM FIELDS
# INCLUDE THE NO COLLEGE DEGREE FILTER
url = "https://www.indeed.com/jobs?q=" + \
    job_query + "&" + deg
print(f"using url of {url}\n\n")

# LOAD THE WEBPAGE OR READ FROM HTML FILE
if(args.d == "pull"):
    html = urllib.request.urlopen(url).read()
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

# FIND THE PARENT TAGS BY CSS CLASS
results_list = soup.find_all("div", class_="cardOutline")
#print(f"Found {len(results_list)} job search results items \n")

# ITERATE THROUGH THE <table> TAGS THAT CONTAIN JOB DATA
i = 0
for result in results_list:
    if i < n:  # iterate for as many times as was specified by the flag"

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
        if location is None:
            location = "not specified"

        # EXTRACT THE TIME THE JOB WAS POSTED date_posted =
        date_posted = "Not specified when posted"
        date_spans = result.find_all("span", class_="date")
        for d_span in date_spans:
            if (d_span.string is not None):
                date_posted = d_span.string

        ###############################################################
        # CONSTRUCTING OBJECT FOR INDIVIDUAL PAGE
        ###############################################################

        try:
            job_page_url = "https://www.indeed.com/viewjob?jk=" + job_id
            job_html = urllib.request.urlopen(job_page_url).read()
            job_soup = BeautifulSoup(job_html, "html.parser")
            # IF THE SINGLE PAGE VIEW OF THE JOB, EXTRACT MORE DATA
            posted = job_soup.find(
                "span", class_="jobsearch-HiringInsights-entry--text").string
            job = JobPost(job_id, title, company, salary, location,
                          date_posted, company_link)
            jobs_post_list.append(job)

        except Exception as e:
            print(e)
        i = i + 1
print(f"collected {len(jobs_post_list)}")
i2 = 1
for job in jobs_post_list:
    print(i2)
    job.printF()
    i2 = i2 + 1
#csv_writer = csv.writer(f)
