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
        # "capture.video": True,
        # "capture.network": False,
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
        
#try to find the first converstaion as a button then default to linear layout
    try:
        chatWindow = driver.find_element(By.XPATH, '(//android.widget.Button[@resource-id="com.whatsapp:id/contact_row_container"]')
        print("Found the element as a button")
    except:
        chatWindow = driver.find_element(By.XPATH, '(//android.widget.LinearLayout[@resource-id="com.whatsapp:id/contact_row_container"])[1]')
        print("Found the element as a linear layout")

    chatWindow.click()
    try:
        messageWait.until(EC.presence_of_element_located(
                        (By.XPATH, '//android.widget.ImageView[@resource-id="com.whatsapp:id/scroll_bottom_icon"]'))).click()
        print("Hitting scroll button...")
        time.sleep(3)
    except:
        print("Scroll button not present moving on")
    #mobile: touchAndHold #
# mobile: longClickGesture {"elementId": "00000000-0000-0092-ffff-ffff0000027a", "duration": 2000}
    
    for a in range(20):
        message = driver.find_element(By.XPATH, '//android.widget.ListView[@resource-id="android:id/list"]/android.view.ViewGroup[2]')
        
        driver.execute_script('mobile: longClickGesture', {
        'elementId': message.id,
        'duration': 2000
    })
        chatList = driver.find_elements(By.XPATH, '//android.widget.ListView[@resource-id="android:id/list"]/android.view.ViewGroup')

        for i in range(3, len(chatList)):
            driver.find_element(By.XPATH, f'//android.widget.ListView[@resource-id="android:id/list"]/android.view.ViewGroup[{i}]').click()
        time.sleep(2)
        driver.find_element(By.XPATH, '//android.widget.Button[@content-desc="Delete"]').click()

        messageWait.until(EC.presence_of_element_located(
            (By.XPATH, '//android.widget.Button[@resource-id="android:id/button1"]'))).click()

finally:
    print("Quiting Driver in Finally Block")
    driver.quit()
