import os
import sys
from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import path
from dotenv import load_dotenv
import time
import requests

load_dotenv(path.join(path.dirname(__file__), 'config.env'))
APITOKEN = os.getenv('APITOKEN')
APPIUM = f'https://appium-dev.headspin.io:443/v0/{APITOKEN}/wd/hub'
validate = False

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
        "fullReset": False
    },
    "headspin:options": {
        "selector": "device_id:RZCXA0KH95R",
        # "deviceStrategy": "random",
        # "capture.video": True,
        # "capture.network": False,
        # "testName": "Android Browser Test",
        # "autoDownloadChromedriver": True,
        "controlLock": True
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
    #adb shell cmd notification set_dnd <value>
    #adb shell cmd notification set_dnd off
    #adb shell cmd notification set_dnd on
    wait = WebDriverWait(driver, 10)
    toastWait = WebDriverWait(driver, 5)
    try:
        #no reason to activate app if it is already open
        wait.until(EC.presence_of_element_located(
        (By.ACCESSIBILITY_ID, 'Google Messages')))
        print("App is open")
    except:
        driver.activate_app('com.google.android.apps.messaging')
        print("Open Google Messages")
        try:
            wait.until(EC.presence_of_element_located(
                    (By.ACCESSIBILITY_ID, 'Google Messages')))
            print("App opened in converstaions")
            element = driver.find_element(By.XPATH, '(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[1]')
            element.click()
        except:
            print("App opened in odd place. Lets see if its E2E Tests")
            driver.find_element(By.XPATH, '//android.widget.TextView[@text="E2E Tests"]')
            print("We are in E2E messages")


    time.sleep(3)
#(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[1]
    # element = driver.find_element(By.XPATH, '(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[1]')
    # element.click()

#     print("About to long click")
#     time.sleep(3)
#     driver.execute_script('mobile: longClickGesture', {
#     'elementId': element.id,
#     'duration': 6000
# })
    #R5CT22BKELM 3000
    #RZCXA0KH95R 6000
    #we may come back to this
    #//android.widget.ImageView[@content-desc="More options"]
    #//android.widget.TextView[@resource-id="com.google.android.apps.messaging:id/title" and @text="Mark as read"]

    cap = 8
    for i in range(10):
        print("iteration " + str(i))
        messageToHold = toastWait.until(EC.presence_of_element_located(
                    (By.XPATH, '//android.view.View[@resource-id="message_list"]/android.view.View[1]')))

        if(messageToHold.get_attribute("clickable") == "true"):
            driver.execute_script('mobile: longClickGesture', {
            'elementId': messageToHold.id,
            'duration': 5000
        })
        else:
            messageToHold = toastWait.until(EC.presence_of_element_located(
            (By.XPATH, '//android.view.View[@resource-id="message_list"]/android.view.View[2]')))
            driver.execute_script('mobile: longClickGesture', {
                        'elementId': messageToHold.id,
                        'duration': 5000
                    })
        # chatList = driver.find_elements(By.XPATH, '//android.view.View[@resource-id="message_list"]/android.view.View')
        # for i in range(3, min(len(chatList), cap)):
        #     print(i)
        #     el = driver.find_element(By.XPATH, f'//android.view.View[@resource-id="message_list"]/android.view.View[{i}]')
        #     if(el.get_attribute("clickable") == "true"):
        #         el.click()

        print("Moving to delete messages")
        driver.find_element(By.ACCESSIBILITY_ID, 'Delete').click()
        toastWait.until(EC.presence_of_element_located(
                        (By.XPATH, '//android.widget.TextView[@text="Delete"]'))).click()
        # print(f'Deleting {len(chatList)} messages')
        time.sleep(2)

    # #//android.view.View[@resource-id="message_list"]/android.view.View[4]
    # #accessibility id Delete
    # #//android.widget.TextView[@text="Delete"]
    # time.sleep(2)
    # chatList = driver.find_elements(By.XPATH, '(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])')

    # for i in range(2, len(chatList)):
    #     driver.find_element(By.XPATH, f'(//android.view.ViewGroup[@resource-id="com.google.android.apps.messaging:id/swipeableContainer"])[{i}]').click()
    # print("Moving to delete messages")
    # time.sleep(5)

    # driver.find_element(By.ACCESSIBILITY_ID, 'Trash')

    # driver.find_element(By.ACCESSIBILITY_ID, 'Done').click()

finally:
    print("Quiting Driver in Finally Block")
    driver.quit()
