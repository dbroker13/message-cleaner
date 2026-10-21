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

options = AppiumOptions()
options.load_capabilities({
    "appium:options": {
        "automationName": "uiautomator2",
        "platformName": "Android",
        "autoGrantPermissions": True,
        "newCommandTimeout": 300,
        "appPackage": "com.google.android.apps.messaging",
        "appActivity": "com.google.android.apps.messaging.ui.ConversationListActivity",
        "noReset": True,
        "forceAppLaunch": True
    },
    "headspin:options": {
        "selector": "device_id:RZCXA0KH95R",
        "retryNewSessionFailure": False,
        # "deviceStrategy": "random",
        "capture.video": True,
        "capture.network": False,
        # "testName": "Android Browser Test",
        # "autoDownloadChromedriver": True,
        # "controlLock": True
    },
})
headers = {
            'Authorization': f'Bearer {APITOKEN}'
        }

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

caps = driver.capabilities
device_id = caps.get('udid') or caps.get('appium:udid') or caps.get('deviceUDID')
try:    
    #adb shell cmd notification set_dnd <value>
    #adb shell cmd notification set_dnd off
    #adb shell cmd notification set_dnd on
    wait = WebDriverWait(driver, 10)
    toastWait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located(
        (By.ACCESSIBILITY_ID, 'Google Messages')))
    print("App is open")
    data = 'cmd notification set_dnd on'
    URL = f'https://api-dev.headspin.io/v0/adb/{device_id}/shell'
    response = requests.post(
            URL,
            headers=headers,
            data=data,
        )
    startNum = 2
    initalChat = driver.find_element(By.XPATH, '(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[1]')
    skipped_targets = initalChat.find_elements(
    By.XPATH, './/android.widget.TextView[contains(@text, "e2e_tests_inbound")]')
    if skipped_targets:
        try:
            print("Skipping the intial convo")
            initalChat = driver.find_element(By.XPATH, '(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[2]')
            startNum = 3
        except:
            print("All messages are deleted!!")
            sys.exit(0)
        else:
            print("Not our contact")    

    driver.execute_script('mobile: longClickGesture', {
    'elementId': initalChat.id,
    'duration': 6000
    })
    chatList = driver.find_elements(By.XPATH, '(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])')
    for i in range(startNum, len(chatList)):
        chat = driver.find_element(
            By.XPATH, f'(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[{i}]')
        skipped_targets = chat.find_elements(
            By.XPATH, './/android.widget.TextView[contains(@text, "e2e_tests_inbound")]')
        contactNames = chat.find_elements(By.XPATH, './/android.widget.TextView')
        if skipped_targets:
            print("This Contact needs Skipped...")
        else:
            print("Adding this contact to be deleted")
            chat.click()
    driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Trash"]').click()
    toastWait.until(EC.presence_of_element_located(
                     (By.XPATH, '//android.widget.Button[@resource-id="android:id/button1"]'))).click()
    

finally:
    print("Quiting Driver in Finally Block")
    data = 'cmd notification set_dnd off'
    URL = f'https://api-dev.headspin.io/v0/adb/{device_id}/shell'
    response = requests.post(
            URL,
            headers=headers,
            data=data,
        )
    sid = driver.session_id
    print(f'https://ui.headspin.io/sessions/{sid}/waterfall')
    driver.quit()

