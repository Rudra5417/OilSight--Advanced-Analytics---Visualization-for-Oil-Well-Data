from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
from mysql.connector import Error
import getpass
import time


def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--log-level=DEBUG")
    return webdriver.Chrome(options=options)


def search_well(driver, api_number, well_name):
    driver.get("https://www.drillingedge.com/search")
    driver.find_element(By.NAME, 'api_no').send_keys(api_number)
    driver.find_element(By.NAME, 'well_name').send_keys(well_name)
    search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-submit.btn-medium.blue'))
    )
    search_button.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//a[text()='{well_name.upper()}']"))
    )
    driver.find_element(By.XPATH, f"//a[text()='{well_name.upper()}']").click()
    time.sleep(5)


def extract_well_data(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    well_status = soup.find('th', string='Well Status').find_next_sibling('td').get_text(strip=True)
    well_type = soup.find('th', string='Well Type').find_next_sibling('td').get_text(strip=True)
    closest_city = soup.find('th', string='Closest City').find_next_sibling('td').get_text(strip=True)
    production_data = soup.find_all('p', class_='block_stat')
    return {
        'Well Status': well_status,
        'Well Type': well_type,
        'Closest City': closest_city,
        'Oil Produced': production_data[0].get_text(strip=True),
        'Gas Produced': production_data[1].get_text(strip=True)
    }


def main():
    driver = setup_driver()
    password = getpass.getpass("Enter your password: ")
    host = "localhost"
    user = "root"
    database="dsci560_lab5"

    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()

    select_query = "SELECT * FROM welldata"
    cursor.execute(select_query)
    results = cursor.fetchall()

    for row in results:
        try:
            search_well(driver, ' '.join(row[0]), ' '.join(row[1]))
            data = extract_well_data(driver)
            for key, value in data.items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            driver.quit()


if __name__ == "__main__":
    main()

