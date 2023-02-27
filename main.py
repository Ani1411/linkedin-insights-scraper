import os

import pandas as pd
from dotenv import load_dotenv
from linkedin_insights import InsightsReader

load_dotenv()


creds = {
    'email': os.environ.get('EMAIL'),
    'password': os.environ.get('PASSWORD')
}

companies = pd.read_csv('companies.csv')
companies.drop_duplicates(subset=['company_name', 'linkedin_url'], keep='first', inplace=True)

linkedin = InsightsReader(chrome_path='chrome/chromedriver')

if linkedin.signin(email=creds['email'], password=creds['password']):
    linkedin.insights(company_list=companies.to_dict(orient='records'))
    print('--------------- completed ---------------')
