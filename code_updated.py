import requests as re
from bs4 import BeautifulSoup
import json
import os
import csv
from pprint import pprint
CSV_FILE_NAME='data.csv'
CSV_FILE_HEADER=['Device Name', 'Manufacturer Name', 'Series', 'Model Name', 'Product Link']

requestHeader={
  'accept': 'application/json, text/javascript, */*; q=0.01',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'cookie':'__cfduid=d8bb3bd2f21c3f43b54efde7a84a153051585681204; language=en; currency=GBP; PHPSESSID=cksoro6vtr5k982lcksgegpuu4; _ga=GA1.3.267546626.1585681209; _gid=GA1.3.1771523794.1585681209; _vwo_uuid_v2=D847DEE4A6D59A5F0F533375F99A83C5E|0cd6811ebbab404d0df4ad456fa83ad4; _hjid=5f348cba-18e2-4000-9911-5974d0781fa4; _hjIncludedInSample=1; wcsid=rfvVy4nOoj6rU90E7N6Jn0Kda2XzPo62; hblid=JwR4wm0yQZ0NOKUd7N6Jn0K2dPaE6BrX; _okdetect=%7B%22token%22%3A%2215856812128000%22%2C%22proto%22%3A%22https%3A%22%2C%22host%22%3A%22www.kingstonmemoryshop.co.uk%22%7D; olfsk=olfsk8693925687035082; _okbk=cd4%3Dtrue%2Cvi5%3D0%2Cvi4%3D1585681215273%2Cvi3%3Dactive%2Cvi2%3Dfalse%2Cvi1%3Dfalse%2Ccd8%3Dchat%2Ccd6%3D0%2Ccd5%3Daway%2Ccd3%3Dfalse%2Ccd2%3D0%2Ccd1%3D0%2C; _ok=3684-498-10-6857; _gat=1; _oklv=1585682533768%2CrfvVy4nOoj6rU90E7N6Jn0Kda2XzPo62; _gali=wizcategory_id_device',
  'origin': 'https://www.kingstonmemoryshop.co.uk'
}

def init(overwrite=False):
  if not os.path.exists(CSV_FILE_NAME) or overwrite:
    with open(CSV_FILE_NAME,'w',newline='',encoding='utf-8-sig') as csvfile:
      filewriter = csv.DictWriter(csvfile, fieldnames=CSV_FILE_HEADER)
      filewriter.writeheader()

def writeRow(rowDict,removeExtra=False):
  # print(rowDict)
  with open(CSV_FILE_NAME,'a',newline='',encoding='utf-8-sig') as csvfile:
    filewriter = csv.DictWriter(csvfile, fieldnames=CSV_FILE_HEADER)
    if removeExtra:
      extra_header=set(rowDict.keys())-set(CSV_FILE_HEADER)
      if extra_header != set(): print(extra_header)
      for e in extra_header:
        del rowDict[e]
    filewriter.writerow(rowDict)

init(True)

URL_GET_DEVICE='https://www.kingstonmemoryshop.co.uk/index.php?route=product/wizard/getJsonDevice'
URL_GET_MANUFACTURER='https://www.kingstonmemoryshop.co.uk/index.php?route=product/wizard/getJsonBrands'
URL_GET_MODELS='https://www.kingstonmemoryshop.co.uk/index.php?route=product/wizard/getJsonModels'


postData='wizcategory_id='
device_page=re.post(URL_GET_DEVICE,headers=requestHeader,data=postData)
if device_page.status_code!=200: print('[!] Page status code: ',device_page.status_code)

devices_json=device_page.json()
for device in devices_json['devices']:
  print("#",device['name'])
  dataDict={}
  dataDict['Device Name']=device['name']
  device_id=device['wiztype_id']
  
  #MANUFACTURER POST Request part
  manufacturer_postData='wiztype_id='+str(device_id)+'&'+postData
  manufacturer_page=re.post(URL_GET_MANUFACTURER,headers=requestHeader,data=manufacturer_postData)
  if manufacturer_page.status_code!=200: print('[!] Page status code: ',manufacturer_page.status_code)
  manufacturers_json=manufacturer_page.json()
  if manufacturers_json==[]:continue
  for manufacturer in manufacturers_json['manufacturers']:
    dataDict['Manufacturer Name']=manufacturer['name']
    print(" >",dataDict['Manufacturer Name'])
    manufacturer_id=str(manufacturer['manufacturer_id'])
    
    #MODEL POST Request part
    model_postData=manufacturer_postData+'&manufacturer_id='+manufacturer_id
    model_page=re.post(URL_GET_MODELS,headers=requestHeader,data=model_postData)
    if model_page.status_code!=200: print('[!] Page status code: ',model_page.status_code)
    model_json=model_page.json()

    # >>> Select a MODEL
    for model in model_json["models"]:
      dataDict['Series']=""
      dataDict['Model Name']=model["name"]
      dataDict['Product Link']=model["href"]
      writeRow(dataDict)

    # >>> Select a SERIES
    for series in model_json["configurator_series"]:
      # SERIES MODEL POST Request part
      dataDict['Series']=series['name']
      conf_series=series['keyword']
      wizcategory_id=str(series['wizcategory_id'])
      wiztype_id=str(series['wiztype_id'])
      series_model_postData='mh=device-grid-item&wizcategory_id='+wizcategory_id+'&wiztype_id='+wiztype_id+'&manufacturer_id='+manufacturer_id+'&configurator_series='+str(conf_series)

      series_model_page=re.post(URL_GET_MODELS,headers=requestHeader,data=series_model_postData)
      if series_model_page.status_code!=200: print('[!] Page status code: ',series_model_page.status_code)
      series_model_json=series_model_page.json()
      # >>> Select a MODEL inside a series
      for model in series_model_json["models"]:
        dataDict['Model Name']=model["name"]
        dataDict['Product Link']=model["href"]
        writeRow(dataDict)
