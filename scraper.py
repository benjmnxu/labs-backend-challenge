import random
import string
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app import DB_FILE, app
from extensions import db
from models import Club, Tags, User, ActiveUser, Comment, File

db.create_all()

options = webdriver.ChromeOptions()

options.add_argument('headless')

driver = webdriver.Chrome(
    service = Service('chromedriver'),
    options = options
)

time.sleep(0.02)

driver.get("https://pennclubs.com/")
screen_height = driver.execute_script("return window.screen.height;")
i = 1

loading_new = False

list = driver.find_elements(By.CLASS_NAME, 'ClubCard__CardWrapper-qqpg24-0')
last_element = None
iteration = 0

while True:
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
    i += 1
    time.sleep(0.3)
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'Loading__LoadingCircle-s3v9z-1')))
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    iteration += 1
    if (screen_height) * i > scroll_height:
        break

elements = driver.find_elements(By.CLASS_NAME, 'ClubCard__CardWrapper-qqpg24-0')
main_handle = driver.current_window_handle
information = {}
for element in elements:
    link = (element.find_element(By.TAG_NAME, 'a').get_attribute('href'))
    driver.switch_to.new_window('tab')
    driver.get(link)
    club_name = driver.find_element(By.CLASS_NAME, 'Header__Wrapper-sc-1ev3ukm-0').text
    raw_club_tags = driver.find_elements(By.CLASS_NAME, "Tags__Tag-sc-1fgujqo-0")
    club_tags = []
    for tags in raw_club_tags:
        club_tags.append(tags.text)
    club_description = driver.find_element(By.CLASS_NAME, 'Description__Wrapper-fvy1rr-0').get_attribute('innerText')
    points_of_contact = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[3]/div/div/div/div[1]/div[4]').get_attribute('innerText')
    basic_info = driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[3]/div/div/div/div[2]/div[2]').get_attribute('innerText')
    # print(club_name)
    # print(club_tags)
    # print(club_description)
    # print(points_of_contact)
    # print(basic_info)
    club = Club(code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)), name = club_name, description = club_description, basic_info=basic_info, contact_info=points_of_contact)
    db.session.add(club)
    for tag in club_tags:
        tag_obj = Tags.query.filter(Tags.tag==tag).first()
        if tag_obj is None:
            t = Tags(tag=tag)
            db.session.add(t)
            club.tags.append(t)
        else:
            club.tags.append(tag_obj)
    driver.close()
    driver.switch_to.window(main_handle)

db.session.commit()
