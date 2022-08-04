from selenium import webdriver
from selenium.webdriver.common.by import By
import time


if __name__ == '__main__':
    cities = []
    try:
        browser = webdriver.Chrome()
        browser.get("https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0"
                    "%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8")
        time.sleep(5)
        file = open('cities.txt', 'w', encoding='UTF-8')
        i = 1
        while True:
            city = browser.find_element(By.CSS_SELECTOR, f'tbody > tr:nth-child({i}) > td:nth-child(3) > a')
            cities.append(city.text)
            if city == browser.find_element(By.CSS_SELECTOR, f'tbody > tr:last-child > td:nth-child(3) > a'):
                break
            i += 1
        file.write('\n'.join(cities))
        file.close()
    finally:
        # успеваем скопировать код за 30 секунд
        # закрываем браузер после всех манипуляций
        browser.quit()