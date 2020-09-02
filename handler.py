import boto3
import decimal
import pytz
import sys
import uuid
from settings import get_aws_access_key
from settings import get_aws_secret_access_key
from settings import get_region
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from time import sleep


def aws_session_token():
    session = boto3.Session(
        aws_access_key_id=get_aws_access_key(),
        aws_secret_access_key=get_aws_secret_access_key(),
        region_name=get_region(),
    )
    return session


session = aws_session_token()
dynamodb = session.resource('dynamodb')
three_gorges_table = 'three_gorges_reservoir_table'
other_station_table = 'other_station_reservoir_table'
tz = pytz.timezone('Europe/London')
dt = datetime.now(tz)
dt_string = dt.strftime("%d/%m/%Y %H:%M:%S")


def driver_engine():
    options = Options()
    # # dev
    # options.add_argument('--headless')
    # chromedriver = webdriver.Chrome(chrome_options=options)
    # prod
    options.binary_location = '/opt/bin/chromium-browser/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    chromedriver = webdriver.Chrome(
        '/opt/bin/chromedriver', chrome_options=options)
    return chromedriver


def get_soup():
    driver = driver_engine()
    print('\nProcessing Data... Please Wait.')
    driver.get('http://www.cjh.com.cn/sqindex.html')
    sleep(10)
    html_source = BeautifulSoup(driver.page_source, 'html.parser')
    return html_source


def web_scraping():
    soup = get_soup()

    # Three Gorges Reservoir Data Scraping
    try:
        station_name = soup.find("td", text="三峡水库")
        datetime = soup.find("td", text="三峡水库").find_next_sibling("td")
        water_level = datetime.find_next_sibling("td")
        water_flow = water_level.find_next_sibling("td")

        table = dynamodb.Table(three_gorges_table)
        table.put_item(
            Item={
                'UUID': str(uuid.uuid1()),
                'StationName': station_name.text,
                'DateTime': str(dt_string),
                'WaterLevel': decimal.Decimal(water_level.text),
                'WaterFlow': water_flow.text
            }
        )
    except Exception as e:
        print(e)
        sys.exit(6)

    # Other Station Data Scraping
    try:
        water_station_all = soup.find_all("td")
        for element in water_station_all:
            children = element.findChildren("a", recursive=False)
            if children != []:
                station_name_all = element
                datetime_all = element.find_next_sibling("td")
                water_level_all = datetime_all.find_next_sibling("td")
                water_flow_all = water_level_all.find_next_sibling("td")

                table = dynamodb.Table(other_station_table)
                table.put_item(
                    Item={
                        'UUID': str(uuid.uuid1()),
                        'StationName': station_name_all.text,
                        'DateTime': str(dt_string),
                        'WaterLevel': decimal.Decimal(water_level_all.text),
                        'WaterFlow': water_flow_all.text
                    },
                )
    except Exception as e:
        print(e)
        sys.exit(6)

    print('DynamoDB Item Create Successful.')


# # dev
# web_scraping()

# prod
def scrape(event, context):
    web_scraping()
