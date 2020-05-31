import pytesseract
import cv2
import re 
import time
from  selenium import webdriver

# Cut captcha to each word
from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
import time

def listCaseIfFalse(label, row_nums = 0):
    list_common_wrong_case = [
        [ "0", "o"],
        [ "i", "1"],
        [ "l", "i"],
        [ "q", "g"],
        [ "Q", "0"],
        [ "o", "9"],
        [ "n", "h"],
        [ "a", "q"],
    ]
    return re.sub(r'' + list_common_wrong_case[row_nums][0]
                        , list_common_wrong_case[row_nums][1]
                        , label)

def fillInfo(company_tax_code, invoice_format_code ,invoice_serial, invoice_number):
    driver.find_element_by_css_selector('#tin').send_keys(company_tax_code)
    driver.find_element_by_css_selector('#mau').send_keys(invoice_format_code)
    driver.find_element_by_css_selector('#kyhieu').send_keys(invoice_serial)
    driver.find_element_by_css_selector('#so').send_keys(invoice_number)

def getCaptcha():
    captcha_location = driver.find_element_by_css_selector("img").location
    driver.save_screenshot("tmp/screenshot.png")

    captcha_size = { 'x' : 120, 'y' : 25}
    img = cv2.imread('tmp/screenshot.png', 0)
    img = img[ captcha_location['y']: captcha_location['y'] + captcha_size['y'], captcha_location['x'] : captcha_location['x'] + captcha_size['x']]
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return img

def predict(img):
    custom_config = r'--oem 3 --psm 6'
    label = pytesseract.image_to_string(img, config=custom_config)
    print(label)
    return label.lower()


driver = webdriver.Chrome()
driver.get('http://tracuuhoadon.gdt.gov.vn/search1hd.html')
fillInfo("0102719114","01GTKT0/001","AB/20E","00002232")
img = getCaptcha()
label = predict(img)
match_label_flag = False
print(driver.find_element_by_css_selector('.ui-dialog').is_displayed())



while not match_label_flag:
    print(driver.find_element_by_css_selector('.ui-dialog').is_displayed())
    # If Label_predict is good ( > 70% )
    if len(label) == 6 and not any(c in label for c in "{}\/? []()"):
        driver.find_element_by_css_selector("#captchaCodeVerify").clear(), time.sleep(1)
        driver.find_element_by_css_selector("#captchaCodeVerify").send_keys(label), time.sleep(1)
        driver.find_element_by_css_selector("#searchBtn").click()
        # Predict false
        if driver.find_element_by_css_selector(".ui-state-active").get_attribute('id') != "tab2":
            # Change label 
            for i in range(0,7):
                new_label = listCaseIfFalse(label, i)
                print(new_label)
                time.sleep(2)
                if new_label == label:
                    continue
                driver.find_element_by_css_selector("#captchaCodeVerify").clear(), time.sleep(1)
                driver.find_element_by_css_selector("#captchaCodeVerify").send_keys(new_label), time.sleep(1)
                driver.find_element_by_css_selector("#searchBtn").click()
                if driver.find_element_by_css_selector(".ui-state-active").get_attribute('id') == "tab2":
                    match_label_flag = True
                    break
        else: 
            match_label_flag = True
            break
    # refresh new captcha 
    if len(label) != 6 or not match_label_flag :
        driver.refresh()
        fillInfo("0102719114","01GTKT0/001","AB/20E","00002232"), time.sleep(1)
        img = getCaptcha()
        label = predict(img)

time.sleep(2)
driver.quit()

