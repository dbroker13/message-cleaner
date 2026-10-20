import os
import sys
from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        "appPackage": "com.whatsapp",
        "appActivity": "com.whatsapp.home.ui.HomeActivity",
        "noReset": True,
        "forceAppLaunch": True
    },
    "headspin:options": {
        # "selector": "device_note:*Whatsapp*",
        "selector": "device_id:R5CT22BKELM",
        "capture.video": True,
        "capture.network": False,
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
    print("Failed to start driver")
    print(f)
    sys.exit(1)

try:
    messageWait = WebDriverWait(driver, 3)
    wait = WebDriverWait(driver, 10)
    try:
        #no reason to activate app if it is already open
        wait.until(EC.presence_of_element_located(
        (By.ID, 'com.whatsapp:id/toolbar_logo')))
        print("App is open")
    except:
        driver.activate_app('com.whatsapp')
        print("Open WhatsApp")
        wait.until(EC.presence_of_element_located(
                (By.ID, 'com.whatsapp:id/toolbar_logo')))
    startNum = 2
    try:
        chatWindow = driver.find_element(By.XPATH, '(//android.widget.Button[@resource-id="com.whatsapp:id/contact_row_container"]')
        print("Found the element as a button")
    except:
        chatWindow = driver.find_element(By.XPATH, '(//android.widget.LinearLayout[@resource-id="com.whatsapp:id/contact_row_container"])[1]')
        print("Found the element as a linear layout")

        skipped_targets = chatWindow.find_elements(
            By.XPATH, './/android.widget.TextView[contains(@text, "Stage Sandbox")]')
        if skipped_targets:
            try:
                chatWindow = driver.find_element(By.XPATH, '(//android.widget.LinearLayout[@resource-id="com.whatsapp:id/contact_row_container"])[2]')
                startNum = 3
            except:
                print("All messages are deleted!!")
                sys.exit(0)
        else:
            print("Not our contact")        
    
    driver.execute_script('mobile: longClickGesture', {
        'elementId': chatWindow.id,
        'duration': 2000
    })

    try:
        print("Looking for other chats other chats")
        chatList = driver.find_elements(By.XPATH, '(//android.widget.LinearLayout[@resource-id="com.whatsapp:id/contact_row_container"])')
        print("Found other chats")
        for i in range(startNum, len(chatList)+1):
            chat = driver.find_element(By.XPATH, f'(//android.widget.LinearLayout[@resource-id="com.whatsapp:id/contact_row_container"])[{i}]')
            skipped_targets = chat.find_elements(
                By.XPATH, './/android.widget.TextView[contains(@text, "Stage Sandbox")]')
            contactNames = chat.find_elements(By.XPATH, './/android.widget.TextView')
            if skipped_targets:
                print("This Contact needs Skipped...")
            else:
                chat.click()

    except:
        print("No other chats")

    time.sleep(2)
    wait.until(EC.presence_of_element_located(
        (By.ACCESSIBILITY_ID, 'Delete chats'))).click()
    try:
        driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Delete all"]').click()
    except:
        driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Delete chat"]').click()
  

finally:
    print("Quiting Driver in Finally Block")
    driver.quit()
