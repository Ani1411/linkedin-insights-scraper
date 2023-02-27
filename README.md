# Getting Started

#### LinkedIn Insights Scraper. 
This script scrapes the insights data of the companies. Make sure you have a LinkedIn Premium account to access these

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/Ani1411/linkedin-insights-scraper.git
$ cd linkedin-insights-scraper

$ virtualenv venv
$ source venv/bin/activate
```

Then install the dependencies:

```sh
(venv)$ pip install -r requirements.txt
```

Virtual Environment variables. Enter LinkedIn Email and Password:

```
EMAIL=
PASSWORD=
```

Input File: `companies.csv`, 
Output Files: `csv/*`


### RUN
```shell
(venv)$ python main.py
```