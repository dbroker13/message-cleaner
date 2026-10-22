import os
import sys
from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import path
import time
import requests

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
        "selector": "device_id:00008120-000E505426D8A01E",
        # "deviceStrategy": "random",
        "capture.video": True,
        "capture.network": False,
        # "testName": "Android Browser Test",
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
    # converstations[0].click()
    # skipped_targets = chat.find_elements(
    #         By.XPATH, './/android.widget.TextView[contains(@text, "e2e_tests_inbound")]')
    # contactNames = chat.find_elements(By.XPATH, './/android.widget.TextView')
    # if skipped_targets:
    # print("This Contact needs Skipped...")
    #     else:
    # print("Adding this contact to be deleted")
    #     chat.click()


#(//XCUIElementTypeOther[@name="Sticker" and contains(@label, "Outbound")]
#if this has a link delete the link element not the element. 
#
#
    # try:
    #     messageToDelete = wait.until(EC.presence_of_element_located(
    #         (By.XPATH, '//XCUIElementTypeOther[@name="Sticker" and contains(@label, "Outbound")]')))

    #     child_links = messageToDelete.find_elements(By.XPATH, './/XCUIElementTypeLink')
    #     if len(child_links) > 0:
    #         print(f"Found {len(child_links)} link child element(s)!")
    #         driver.execute_script('mobile: touchAndHold', {
    #             'elementId': child_links[0].id,
    #             'duration': 3.0
    #         })
    #     else:
    #         driver.execute_script('mobile: touchAndHold', {
    #             'elementId': messageToDelete.id,
    #             'duration': 3.0
    #         })
    # except:
    #     messageToDelete = wait.until(EC.presence_of_element_located(
    #                 (By.XPATH, '//XCUIElementTypeOther[@name="Sticker" and contains(@label, "Shortening")]')))
        
    #     driver.execute_script('mobile: touchAndHold', {
    #             'elementId': messageToDelete.id,
    #             'duration': 3.0
    #         })

    # wait.until(EC.presence_of_element_located(
    #     (By.ACCESSIBILITY_ID, 'More…'))).click()
    # wait.until(EC.presence_of_element_located(
    #     (By.ACCESSIBILITY_ID, 'Delete'))).click()
    # wait.until(EC.presence_of_element_located(
    #     (By.XPATH, '//XCUIElementTypeButton[contains(@name, "Delete Message")]'))).click()

    ##Not handled //XCUIElementTypeButton[@name="Sticker" and contains(@label, "Outbound"]
    ##//XCUIElementTypeCollectionView[@name="TranscriptCollectionView"]
    

#mobile: touchAndHold #
# mobile: longClickGesture {"elementId": "2B000000-0000-0000-0D21-000000000000", "duration": 2.0}

    #//XCUIElementTypeOther[@name="Sticker" and contains(@label, "Outbound")]
    # wait.until(EC.presence_of_element_located(
    #     (By.ACCESSIBILITY_ID, 'optionsButton'))).click()
    # #Using this to resolve stale element issue
    # time.sleep(2)
    # wait.until(EC.presence_of_element_located(
    #     (By.ACCESSIBILITY_ID, 'Select Messages'))).click()


    # chatList = driver.find_elements(By.XPATH, '(//XCUIElementTypeImage[@name="circle"])')

    # for i in range(10):
    #     for i in range(1, len(chatList)+1):
    #         driver.find_element(By.XPATH, f'(//XCUIElementTypeImage[@name="circle"])[1]').click()
    #     print("Moving to delete messages")
    
    # # for i in range(3):
    # #     driver.find_element(By.XPATH, '(//XCUIElementTypeImage[@name="circle"])[1]').click()
    # #     time.sleep(2)

    #     wait.until(EC.presence_of_element_located(
    #         (By.ACCESSIBILITY_ID, 'Delete'))).click()
        
    #     # wait.until(EC.presence_of_element_located(
    #     #     (By.ACCESSIBILITY_ID, 'Done'))).click()


finally:
    print("Quiting Driver in Finally Block")
    sid = driver.session_id
    print(f'https://ui.headspin.io/sessions/{sid}/waterfall')
    driver.quit()
