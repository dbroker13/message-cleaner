import logging
import sys
from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
logger = logging.getLogger(__name__)
import os


def clean_device(device):
    device_id = device['device_id']
    logging.info(f"Clean {device_id} for iMessage")

    APITOKEN = os.getenv('Messages_API_Token')
    APPIUM = f'https://appium-dev.headspin.io:443/v0/{APITOKEN}/wd/hub'
    #com.apple.MobileSMS
    options = AppiumOptions()
    options.load_capabilities({
        "appium:options": {
            "automationName": "xcuitest",
            "platformName": "ios",
            "bundleId": "com.apple.MobileSMS",
        },
        "headspin:options": {
            "selector": f"device_id:{device_id}",
            "capture.video": True,
            "capture.network": False,
            # "testName": "iMessageCleaner",
            # "autoDownloadChromedriver": True,
        },
    })

    try:
        print("Starting Driver")
        driver = webdriver.Remote(
            command_executor=APPIUM,
            options=options
        )
        print("Driver Started")
    except Exception as f:
        print("Failed to start Android browser driver:")
        print(f)
        sys.exit(1)

    try:
        time.sleep(5)
        wait = WebDriverWait(driver, 10)

        wait.until(EC.presence_of_element_located(
            (By.ACCESSIBILITY_ID, 'optionsButton'))).click()
        time.sleep(3)

        wait.until(EC.presence_of_element_located(
            (By.ACCESSIBILITY_ID, 'Select Messages'))).click()

        converstations = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//XCUIElementTypeCell')))

        for convos in converstations[:7]:
            if "outbound" in convos.text.lower():
                print("skpping message: " + convos.text)
            else:
                print("Deleting convo: " + convos.text)
                buttons = convos.find_elements(
                    By.XPATH, './/XCUIElementTypeOther/XCUIElementTypeImage[@name="circle"]')
                print(len(buttons))
                buttons[0].click()

                #(//XCUIElementTypeImage[@name="circle"])
        wait.until(EC.presence_of_element_located(
            (By.ACCESSIBILITY_ID, 'Delete'))).click()

        #
        deleteButtons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, '//XCUIElementTypeButton[@name="Delete"]')))
        # 2. Find the first visible button
        visible_button = next((btn for btn in deleteButtons if btn.is_displayed()), None)

        # 3. Click if a visible button exists
        if visible_button:
            visible_button.click()
        else:
            print("No visible delete button found.")

        time.sleep(8)
    
    finally:
        print("Quiting Driver in Finally Block")
        sid = driver.session_id
        print(f'{device_id} session link: https://ui.headspin.io/sessions/{sid}/waterfall')
        driver.quit()
