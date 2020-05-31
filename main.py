import pytesseract
import cv2
import re 
import time
from  selenium import webdriver
from  selenium.webdriver.support.wait import WebDriverWait
from  selenium.webdriver.support import expected_conditions as EC
from  selenium.webdriver.common.by import By
from  selenium.webdriver.chrome.options import Options

# Cut captcha to each word
from PIL import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt
import pytesseract
import time
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

def listCaseIfFalse(label, row_nums = 0):
    return label.replace(list_common_wrong_case[row_nums][0], list_common_wrong_case[row_nums][1])

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
    # print(label)
    return label.lower()

start = time.time()
chrome_options = Options()
chrome_options.headless = True
driver = webdriver.Chrome(options=chrome_options)
driver.get('http://tracuuhoadon.gdt.gov.vn/search1hd.html')
# fillInfo("0105834034","01GTKT3/001","HN/13P","103")
fillInfo("0102719114","01GTKT0/001","SH/19E","0000004")
img = getCaptcha()
label = predict(img)
match_label_flag = False
while not match_label_flag:
    # If Label_predict is good ( > 70% )
    if len(label) == 6 and not any(c in label for c in "{}\/? []()"):
        driver.find_element_by_css_selector("#captchaCodeVerify").clear(), time.sleep(1)
        driver.find_element_by_css_selector("#captchaCodeVerify").send_keys(label), time.sleep(1)
        # close dialog 
        if driver.find_element_by_css_selector('.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front.ui-dialog-buttons.ui-draggable:last-of-type div:last-of-type button').is_displayed():
            driver.find_element_by_css_selector('.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front.ui-dialog-buttons.ui-draggable:last-of-type div:last-of-type button').click()
        driver.find_element_by_css_selector("#searchBtn").click()
        # Predict false
        time.sleep(3)
        if driver.find_element_by_css_selector('#dieukien').is_displayed():
            # Change label 
            for i in range(0,len(list_common_wrong_case)):
                new_label = listCaseIfFalse(label, i)
                # print(new_label)
                if new_label == label:
                    continue
                driver.find_element_by_css_selector("#captchaCodeVerify").clear(), time.sleep(1)
                driver.find_element_by_css_selector("#captchaCodeVerify").send_keys(new_label), time.sleep(1)
                # close dialog 
                if driver.find_element_by_css_selector('.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front.ui-dialog-buttons.ui-draggable:last-of-type div:last-of-type button'):
                    driver.find_element_by_css_selector('.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front.ui-dialog-buttons.ui-draggable:last-of-type div:last-of-type button').click()
                driver.find_element_by_css_selector("#searchBtn").click()
                time.sleep(3)
                if not driver.find_element_by_css_selector('#dieukien').is_displayed():
                    match_label_flag = True
                    break
        else: 
            match_label_flag = True
            break
    # refresh new captcha 
    if len(label) != 6 or not match_label_flag :
        driver.refresh()
        # fillInfo("0105834034","01GTKT3/001","HN/13P","103")
        fillInfo("0102719114","01GTKT0/001","SH/19E","0000004")
        img = getCaptcha()
        label = predict(img)


output = driver.find_elements(By.CSS_SELECTOR,'table tr:nth-of-type(6) td:last-of-type')[-1].text
print(output)
if ( output.find("Hoá đơn đã thông báo hết giá trị sử dụng trên thông báo cơ sở kinh doanh bỏ địa chỉ kinh doanh mang theo hoá đơn") != -1):
    final_output = "HOA DON BAT HOP PHAP"
else:
    final_output = "HOA DON HOP PHAP"
print(final_output)
driver.quit()
end = time.time()
print( end - start )