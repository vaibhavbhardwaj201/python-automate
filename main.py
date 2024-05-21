from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

# Setup logging format for the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USERNAME = "silvesterbelt"
PASSWORD = "nevergiveup"

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.maximize_window()
driver.implicitly_wait(10)

try:
    driver.get("https://parabank.parasoft.com/parabank/index.htm")
    time.sleep(5)
    wait = WebDriverWait(driver, 10)

    # First, trying to register, if the username already exists, then logging in
    try:
        register_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[normalize-space()='Register']")))
        register_button.click()

        # Filling out the form with dummy data
        first_name = driver.find_element(By.ID, "customer.firstName")
        first_name.send_keys("Silvester")
        last_name = driver.find_element(By.ID, "customer.lastName")
        last_name.send_keys("Belt")
        address = driver.find_element(By.ID, "customer.address.street")
        address.send_keys("25 Sauletekio al.")
        city = driver.find_element(By.ID, "customer.address.city")
        city.send_keys("Vilnius")
        state = driver.find_element(By.ID, "customer.address.state")
        state.send_keys("Vilnius")
        zip_code = driver.find_element(By.ID, "customer.address.zipCode")
        zip_code.send_keys("12345")
        phone = driver.find_element(By.ID, "customer.phoneNumber")
        phone.send_keys("7635667897")
        ssn = driver.find_element(By.ID, "customer.ssn")
        ssn.send_keys("765876")
        username = driver.find_element(By.ID, "customer.username")
        username.send_keys(USERNAME)
        password = driver.find_element(By.ID, "customer.password")
        password.send_keys(PASSWORD)
        confirm_password = driver.find_element(By.ID, "repeatedPassword")
        confirm_password.send_keys(PASSWORD)

        # Registering the user
        register_button = driver.find_element(By.XPATH, "//input[@value='Register']")
        register_button.click()

        try:
            # Checking if the username already exists
            error_message = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'This username already exists.')]")))
            logging.info("Username already exists. Proceeding to login.")

            # Logging in with the username and password declared at the beginning
            driver.find_element(By.XPATH, "//input[@name='username']").send_keys(USERNAME)
            driver.find_element(By.XPATH, "//input[@name='password']").send_keys(PASSWORD)
            driver.find_element(By.XPATH, "//input[@value='Log In']").click()
        except TimeoutException:
            logging.info("Username is unique. Registration successful.")
    except TimeoutException as e:
        logging.error("Registration or login page did not load in time: %s", e)
        driver.save_screenshot('error_screenshot.png')
        raise

    # Open New Account
    try:
        open_account_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Open New Account']")))
        open_account_button.click()

        # Selecting "SAVINGS" account type from the dropdown, we can also select "CHECKING" which is the default
        account_type_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='type']")))
        Select(account_type_dropdown).select_by_visible_text("SAVINGS")

        time.sleep(2)
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@value='Open New Account']"))).click()
        # driver.find_element(By.XPATH, "//input[@value='Open New Account']").click()

        time.sleep(2)
        account_number_text = wait.until(EC.visibility_of_element_located((By.ID, "newAccountId")))
        account_number = account_number_text.text
        logging.info("New account number created: %s", account_number)
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        logging.error("Failed to open new account: %s", e)
        driver.save_screenshot('error_screenshot.png')
        raise

    # Transfering funds after checking if the account number was created successfully
    if account_number:
        try:
            transfer_funds_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Transfer Funds']")))
            transfer_funds_button.click()

            # Entering the amount and selecting the account number to transfer funds to
            driver.find_element(By.ID, "amount").send_keys("365")

            to_account_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "toAccountId")))
            Select(to_account_dropdown).select_by_visible_text(account_number)

            driver.find_element(By.XPATH, "//input[@value='Transfer']").click()

            try:
                # Handling the edge case of alert pop-up if any
                alert = wait.until(EC.alert_is_present())
                logging.info("Alert detected: %s", alert.text)
                alert.accept()
            except TimeoutException:
                logging.info("Transfer was successful.")
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
            logging.error("Failed to transfer funds: %s", e)
            # Saving a screenshot of the error for debugging purposes
            driver.save_screenshot('error_screenshot.png')
            raise
    else:
        # If the account number was not created, we skip the fund transfer
        logging.error("No account number was retrieved, skipping fund transfer.")

except Exception as e:
    logging.error("An unexpected error occurred: %s", e)
    driver.save_screenshot('error_screenshot.png')
    raise
finally:
    driver.quit()