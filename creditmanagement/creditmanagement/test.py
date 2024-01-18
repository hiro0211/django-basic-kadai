from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains

chrome_driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

#chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--no-sandbox")
#chrome_options.add_argument("--disable-dev-shm-usage")

# Chromeドライバーを起動
#chrome_driver = webdriver.Chrome(chrome_options=chrome_options)

chrome_driver.get("https://unipa.itp.kindai.ac.jp/up/faces/login/Com00501A.jsp")

time.sleep(1)

mail = chrome_driver.find_element(By.ID, 'form1:htmlUserId') 
password = chrome_driver.find_element(By.ID, 'form1:htmlPassword')

mail.clear()
password.clear()

mail.send_keys("2011530136k")
password.send_keys("Twks0104Hiroaki")

#mail.submit()
button = chrome_driver.find_element(By.ID, 'form1:login')
button.click()

#chrome_driver.save_screenshot('screenshot.png')
target_element = chrome_driver.find_element(By.ID, 'menuc3')
actions = ActionChains(chrome_driver)
actions.move_to_element(target_element).perform()

time.sleep(2)
grade = chrome_driver.find_element(By.ID, 'menuimg3-1')
grade.click()

time.sleep(2)
subject = chrome_driver.find_element(By.CLASS_NAME, 'form1:htmlAveTsusan').text


#chrome_driver.quit()
