#!/usr/bin/env python
# coding: utf-8

# ### Importing Necessary Libraries

# In[1]:


from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime


# ### Specify path for exporting the results to a csv file

# In[2]:


export_path = "/Users/alay/output.csv" #Don't forget to add '.csv' at the end of the path


# ### Helper functions to process and parse the data rows which will be scraped from the website

# #### This function takes in row data as argument, and processes one row at a time. For each row, it verifies if any of its launch was successful or not, and increments the orbital launch value in the result dataframe whenever it finds a successful launch

# In[3]:


def parseLaunches(start_row_index, rows, df):
    i = start_row_index
    while i<len(rows):
        if(len(rows[i]) == len(columns_rocket*2)):
            date = getLaunchDate(rows[i])
            rowspan = int(rows[i].find('td')['rowspan'])
            index = 1
            while(index < rowspan and i < len(rows)):
                i+=1
                if(len(rows[i]) == len(columns_payload)*2):
                    outcome = rows[i].find_all('td')[5].text
                    outcome = outcome.strip().lower()
                    if(outcome in success):
                        df.loc[date] +=1
                        break
                index+=1
            i+=1
        else:
            i+=1


# #### This is a helper function used in the above mentioned (parseLaunches()) function which takes in a row having date as argument, and returns the date in ISO 8601 format

# In[4]:


def getLaunchDate(row):
    date = row.find('span').text
    date = re.sub('[^0-9a-zA-Z]+', ' ', date)
    date = date.split()[:2]
    date = date[0] + " " + date[1] + " 2019"
    date = datetime.strptime(date, '%d %B %Y')
    date = datetime.strftime(date, '%Y-%m-%dT%H:%M:%S+%H:%M')
    return(date)


# In[5]:


success = ["successful", "operational", "en route"] ### Storing the success messages in a success List


# ### Creating an empty data frame having dates in requires ISO 8601 format as indices and values as attributes. The initial values for all rows will be set to 0.

# In[6]:


start_date = datetime.strptime('1 January 2019', '%d %B %Y')
end_date = datetime.strptime('31 December 2019', '%d %B %Y')
index = pd.date_range(start_date, end_date, freq='D')
index


# In[7]:


df = pd.DataFrame(index = index, columns = ['value'])
df.index.names = ['date']
df['value'] = 0
df.index = df.index.map(lambda x: datetime.strftime(x, '%Y-%m-%dT%H:%M:%S+%H:%M'))
df


# ### Scraping Data From Source Website
# 
# The general procedure to get data from websites is:
# 
# 1. Use requests to connect to a URL and get data from it
# 2. Create a BeautifulSoup object
# 3. Get attributes of the BeautifulSoup object (i.e. the HTML elements that we want)

# In[8]:


# getting HTML from Wikipedia Source Web Page
url = "https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches"
response = requests.get(url)

# create a BeautifulSoup object
soup = BeautifulSoup(response.text, "html.parser")
    
print(soup.prettify())


# ### Grabbing the Orbital Table which is of our primary interest

# In[9]:


table = soup.find('table', {'class':'wikitable'})
print(table.prettify())


# In[10]:


rows = table.find_all('tr')

columns_rocket =  [v.text.replace('\n', '') for v in rows[0].find_all('th')]
columns_payload = [v.text.replace('\n', '') for v in rows[1].find_all('td')]

print("Column Names for Rocket:")
print(columns_rocket)

print("")

print("Column Names for Payload:")
print(columns_payload)

print("")

print("Total number of entries in Table:")
print(len(rows))


# ### Calling above defined helper functions to process rows and populate data frame

# In[11]:


# Since first two rows are header rows, hence we will start processing from 3rd row
start_row_index=3
parseLaunches(start_row_index, rows, df)


# ### Resultant DataFrame

# In[12]:


df.head()


# In[13]:


df[df['value'] > 0]


# In[14]:


export_csv = df.to_csv(export_path, header=True)

