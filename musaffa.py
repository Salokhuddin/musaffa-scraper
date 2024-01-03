from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests, csv, time, sys


options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

def main():
    driver.maximize_window()
    actions = ActionChains(driver)


    # set the links
    link_head = 'https://screener.musaffa.com/cabinet/stock-overview/'
    login_link = 'https://screener.musaffa.com/authentication/login'

    # Log in
    driver.implicitly_wait(7)
    driver.get(login_link)
    
    email_form = driver.find_element(By.ID, 'email')
    fill_in(email_form, 'salohiddin.kutbiddinov@musaffa.com')
    pwd_form = driver.find_element(By.ID, 'pwd')
    fill_in(pwd_form, 'Googlecom_0000')
    login_button = driver.find_element(By.CLASS_NAME, 'btn.btn-success')
    login_button.click()

    # Sleep to allow for log-in to complete
    time.sleep(5)
     

    # Scrape date for tickers
    for ticker in get_links():
        driver.get(f'{link_head}{ticker}')

        # Go to compliance section
        compliance_button = driver.find_element(By.XPATH, '/html/body/app-root/app-cabinet/section/app-stock-overview/div/div/header/div/app-details-tab-btns/div/div/ul/li[2]/button')
        compliance_button.click()

        # Record status
        try:
            status = driver.find_element(By.CLASS_NAME, 'status-div.text-center.halal-status').text
        except Exception:
            try:
                status = driver.find_element(By.CLASS_NAME, 'status-div.text-center.not-halal-status').text
            except Exception:
                status = driver.find_element(By.CLASS_NAME, 'status-div.text-center.doubtful-status').text

        # Record status percentage ratios
        percents = driver.find_elements(By.CLASS_NAME, 'percent')
        halal_percent = percents[0].text
        doubtful_percent = percents[1].text
        haram_percent = percents[2].text
        
        # Go to Financial Screening - Assets section
        assets_button = driver.find_element(By.CLASS_NAME, 'grid-item-4.nav-item')
        assets_button.click()
        
        # Scroll all the way down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)

        # Expand calculation tab
        calculation_button = driver.find_element(By.XPATH, '/html/body/app-root/app-cabinet/section/app-stock-overview/div/div/div[2]/div/app-screener-report/div/div[2]/section/div/div/div/div[2]/div[3]/ngb-accordion/div/div/div/div/h2/button/span')
        actions.move_to_element(calculation_button).perform()
        calculation_button.click()
        time.sleep(1.5)

        # Record assets ration
        assets_ratio = driver.find_element(By.XPATH, '/html/body/app-root/app-cabinet/section/app-stock-overview/div/div/div[2]/div/app-screener-report/div/div[2]/section/div/div/div/div[2]/div[3]/ngb-accordion/div/div[2]/div/div/div[2]/div/div/div[3]').text

        # Go to Financial Screening - Debt section
        debt_button = driver.find_element(By.CLASS_NAME, 'grid-item-5.nav-item')
        debt_button.location_once_scrolled_into_view
        time.sleep(2)
        debt_button.click()

        # Scroll all the way down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)

        # Expand calculation tab
        calculation_button = driver.find_element(By.XPATH, '/html/body/app-root/app-cabinet/section/app-stock-overview/div/div/div[2]/div/app-screener-report/div/div[2]/section/div/div/div/div[2]/div[3]/ngb-accordion/div/div/div/div/h2/button')
        actions.move_to_element(calculation_button).perform()
        time.sleep(2)
        calculation_button.click()
        time.sleep(1.5)
        # Record debt ratio
        debt_ratio = driver.find_element(By.XPATH, '/html/body/app-root/app-cabinet/section/app-stock-overview/div/div/div[2]/div/app-screener-report/div/div[2]/section/div/div/div/div[2]/div[3]/ngb-accordion/div/div[2]/div/div/div[2]/div/div/div[3]').text
        # Save the data
        save([ticker,
            status.strip(), 
            halal_percent.strip(), 
            doubtful_percent.strip(), 
            haram_percent.strip(), 
            assets_ratio.strip(),
            debt_ratio.strip()])




# Define function to write data to a file
def save(field_vars):
    fieldnames = ['status', 
            'halal_percent', 
            'doubtful_percent', 
            'haram_percent', 
            'assets_ratio',
            'debt_ratio']
    row_dict = dict(zip(fieldnames, field_vars[1:]))
    with open('musaffa_stock_data.csv', 'a') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if field_vars[0] == 'AAPL':
            writer.writeheader()
        writer.writerow(row_dict)
        print(f'Success on saving: {field_vars[0]}')

# Define function to write data to a form/field on webpage
def fill_in(form, text):
    ActionChains(driver)\
        .send_keys_to_element(form, text).perform()

# Define function to read and return the list of tickers
def get_links():
    tickers = []
    with open('musaffa_tickers.csv') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tickers.append(row['company_ticker'])
    return tickers
 
# Run main()
if __name__ == '__main__':
    main()
