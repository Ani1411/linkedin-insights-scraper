import re
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from constants import ELEMENT_LOAD_WAIT_TIME, TIME_SLEEP, SCROLL_PAUSE_TIME, SCROLL_HEIGHT_IN_PX


class InsightsReader:
    def __init__(self, chrome_path):
        self.browser, self.wait = self.initiate_browser_object(chrome_path)

    @staticmethod
    def initiate_browser_object(chrome_path):
        options = Options()
        # options.add_argument('--headless')
        browser = webdriver.Chrome(options=options, executable_path=chrome_path)
        wait = WebDriverWait(browser, ELEMENT_LOAD_WAIT_TIME)
        return browser, wait

    def signin(self, email, password):
        print('---------- signing in ----------')
        is_login = bool
        self.browser.get('https://www.linkedin.com')
        try:
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, 'session_key')))
            print('---------- entering email ----------')
            for letter in email:
                email_input.send_keys(letter)
                time.sleep(TIME_SLEEP / 100)
            pwd_input = self.wait.until(EC.presence_of_element_located((By.ID, 'session_password')))
            print('---------- entering password ----------')
            for letter in password:
                pwd_input.send_keys(letter)
                time.sleep(TIME_SLEEP / 100)
            submit_btn = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'sign-in-form__submit-button')))
            submit_btn.click()
            time.sleep(TIME_SLEEP)
            current_url = self.browser.current_url
            if current_url[:30] == 'https://www.linkedin.com/feed/':
                is_login = True
        except Exception:
            is_login = False
        else:
            return is_login

    def scroll(self):
        # Get scroll height
        last_height = SCROLL_HEIGHT_IN_PX

        while True:
            # Scroll down to bottom
            self.browser.execute_script(f"window.scrollTo(0, {last_height});")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            page_height = self.browser.execute_script("return document.body.scrollHeight")
            if page_height <= last_height:
                break
            last_height += SCROLL_HEIGHT_IN_PX

    @staticmethod
    def get_text(text, span=False):
        string = text.get_attribute('textContent').strip()
        return string.split('\n')[1].strip().split(' ')[0] if span else string

    @staticmethod
    def create_csv(csv_name, input_data, data):
        input_df = pd.DataFrame(input_data)
        input_df.drop_duplicates(subset=['company_name', 'linkedin_url'], keep='first', inplace=True)
        data_df = pd.DataFrame(data)
        df = pd.merge(input_df, data_df, on=['company_name', 'linkedin_url'], how='left')
        df.to_csv(f'csv/{csv_name}', index=False)

    def get_basic_details(self, data, company):
        obj = {
            'company_name': company['company_name'],
            'linkedin_url': company['linkedin_url'],
        }
        overview_div = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'p.break-words.white-space-pre-wrap.t-black--light.mb5.text-body-small')))
        obj['overview'] = re.subn('  +|\n+', ' ', self.get_text(overview_div))[0]
        dl = self.browser.find_element(By.CSS_SELECTOR, 'dl.overflow-hidden')
        titles = dl.find_elements(By.CSS_SELECTOR, 'dt.mb1.text-heading-small')
        values = dl.find_elements(By.CSS_SELECTOR, 'dd.mb4.t-black--light.text-body-small')
        for title, value in zip(titles, values):
            try:
                obj[self.get_text(title)] = re.subn('  +|\n+', '', self.get_text(value))[0]
            except Exception as e:
                obj[self.get_text(title)] = ''
        data.append(obj)

    def get_employee_distribution(self, data, company):
        emp_distribution_table = self.wait.until(
            EC.presence_of_element_located((By.ID, 'function-growth__a11y-functions-table')))
        table_body = emp_distribution_table.find_element(By.TAG_NAME, 'tbody')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            table_cells = row.find_elements(By.TAG_NAME, 'td')
            obj = {
                'company_name': company['company_name'],
                'linkedin_url': company['linkedin_url'],
                'function': self.get_text(text=table_cells[0]),
                'number_of_employees': self.get_text(text=table_cells[1]),
                'percentage_of_total_headcount': self.get_text(text=table_cells[2]),
                'six_month_growth': self.get_text(text=table_cells[3], span=True),
                'twelve_month_growth': self.get_text(text=table_cells[4], span=True)
            }
            data.append(obj)

    def get_new_hires(self, data, company):
        k = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ember-view')))
        new_hires_section = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.org-insights-module.org-insights-newhires-module.module')))
        table = new_hires_section.find_element(By.CLASS_NAME, 'visually-hidden')
        table_body = table.find_element(By.TAG_NAME, 'tbody')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            table_cells = row.find_elements(By.TAG_NAME, 'td')
            obj = {
                'company_name': company['company_name'],
                'linkedin_url': company['linkedin_url'],
                'date': self.get_text(text=table_cells[0]),
                'number_of_senior_hires': self.get_text(text=table_cells[1]),
                'number_of_other_hires': self.get_text(text=table_cells[2])
            }
            data.append(obj)

    def get_openings(self, data, company):
        k = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ember-view')))
        new_hires_section = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'section.org-insights-module.org-insights-functions-growth.org-insights-jobs-module')))
        table = new_hires_section.find_element(By.ID, 'function-growth__a11y-jobs-table')
        table_body = table.find_element(By.TAG_NAME, 'tbody')
        rows = table_body.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            table_cells = row.find_elements(By.TAG_NAME, 'td')
            obj = {
                'company_name': company['company_name'],
                'linkedin_url': company['linkedin_url'],
                'function': self.get_text(text=table_cells[0]),
                'number_of_openings': self.get_text(text=table_cells[1]),
                'percentage_of_total_openings': self.get_text(text=table_cells[2]),
                'three_month_growth': self.get_text(text=table_cells[3], span=True),
                'six_month_growth': self.get_text(text=table_cells[4], span=True),
                'twelve_month_growth': self.get_text(text=table_cells[5], span=True)
            }
            data.append(obj)

    def get_data(self, name, perform, company, company_list, data):
        try:
            perform(data, company)
        except Exception as e:
            print(f'{name}:', e)
        else:
            self.create_csv(csv_name=f'{name}.csv', input_data=company_list, data=data)

    def insights(self, company_list):
        basic_details = []
        employee_distribution = []
        new_hires = []
        new_openings = []

        for idx, company in enumerate(company_list):
            url = company['linkedin_url']
            about_url = f"{url}about/" if url.endswith('/') else f"{url}/about/"
            self.browser.get(about_url)
            time.sleep(TIME_SLEEP / 2)
            try:
                self.get_data(name='basic_details', perform=self.get_basic_details, company_list=company_list,
                              company=company, data=basic_details)
            except Exception:
                print(f"error in {company['company_name']} about")
            insights_url = f"{url}insights/" if url.endswith('/') else f"{url}/insights/"
            self.browser.get(insights_url)
            time.sleep(TIME_SLEEP / 2)
            try:
                self.scroll()
                self.get_data(name='employee_distribution', perform=self.get_employee_distribution,
                              company_list=company_list, company=company, data=employee_distribution)
                self.get_data(name='new_hires', perform=self.get_new_hires, company_list=company_list, company=company,
                              data=new_hires)
                self.get_data(name='new_openings', perform=self.get_openings, company_list=company_list, company=company,
                              data=new_openings)
            except Exception as e:
                if company_list.count(company) <= 2:
                    company_list.append(company)
            print(idx)





