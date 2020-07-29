import json
import requests
import time


proxy_ip_list = []

print('***** Start Getting Proxy List *****')

url = 'https://ip.jiangxianli.com/api/proxy_ips'
param = {'country': '中国'}

while True:
    r = requests.get(url, param)
    r = json.loads(r.text)
    data = r['data']['data']
    next_page_url = r['data']['next_page_url']

    proxy = [f'{i["protocol"]}://{i["ip"]}:{i["port"]}' for i in data]
    proxy_ip_list.extend(proxy)

    if not next_page_url:
        break
    else:
        url = next_page_url
        time.sleep(1)
