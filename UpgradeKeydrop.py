import math
import time
import re
import undetected_chromedriver as uc
import json
import requests

session_id = ""

value_item_base = 0.5

def upgradeWeapons(session_id, token):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    driver.get('https://key-drop.com/es/skins/upgrader')
    time.sleep(3)
    driver.add_cookie({"name": "session_id", "value": session_id})
    driver.refresh()

    cookiesDict = {}

    for cookie in driver.get_cookies():
        cookiesDict[cookie["name"]] = str(cookie["value"])

    driver.close()
    driver.quit()

    headers = {
        'authority': 'key-drop.com',
        'accept': '*/*',
        'accept-language': 'es-ES,es;q=0.9',
        'referer': 'https://key-drop.com/es/skins/upgrader',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    response = requests.get('https://key-drop.com/es/skins/Upgrader/my_items', cookies=cookiesDict, headers=headers)

    for item in response.json()["data"]["elements"]:
        # Balance to add to item
        balance_to_add = math.floor(((value_item_base + value_item_base*(math.floor(item["price"] / value_item_base))) * 0.88 - item["price"]) * 100) / 100
        # Item Value to upgrade
        item_value_to_upgrade = (value_item_base + value_item_base*(math.floor(item["price"] / value_item_base)))

        params = {
            'page': '0',
            'text': '',
            'min_price': item_value_to_upgrade - 0.01,
            'rarity': '',
            'order': 'ASC',
        }

        response = requests.get('https://key-drop.com/es/skins/Upgrader/skins_base', params=params, cookies=cookiesDict,
                                headers=headers)

        print(balance_to_add)

        json_data = {
            'userSkins': [
                item["id"],
            ],
            'upgradeSkins': [
                response.json()["data"]["elements"][0]["id"],
            ],
            'userBalance': balance_to_add,
        }

        response = requests.post('https://key-drop.com/es/skins/Upgrader/upgrade', cookies=cookiesDict, headers=headers,
                                 json=json_data)

        if response.json()["status"] == True:
            if response.json()["upgrade"] == True:
                print("Upgrade conseguido.")
            else:
                print("Upgrade fallido.")
        else:
            print("Error.")

        time.sleep(5)

def bypass_cf(session_id):
    try:
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        driver.get('https://key-drop.com/token')
        time.sleep(3)
        driver.add_cookie({"name": "session_id", "value": session_id})
        driver.refresh()

        # Utilizar expresión regular para encontrar el token
        match = re.search(r'ey\S+', driver.page_source)

        if match:
            token = match.group()
            token = token.rstrip('</body></html>')

        driver.close()
        driver.quit()
        return 'valid', token
    except Exception as err:
        return 'invalid', f'There was an error bypassing cloudflare, make sure your session_id is valid! {err}'


def start(session_id):
    answer = bypass_cf(session_id)
    if answer[0] == 'valid':
        upgradeWeapons(session_id, answer[1])
    else:
        print("Token error")

start(session_id)
