from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from songline import Sendline
import time
import datetime 
import csv 
from bs4 import BeautifulSoup as soup

opt = webdriver.ChromeOptions()
opt.add_argument('headless') #hidden mode of chorme driver
opt.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=opt) #create driver
options = webdriver.ChromeOptions()
url = 'https://ddcportal.ddc.moph.go.th/portal/apps/opsdashboard/index.html#/20f3466e075e45e5946aa87c96e8ad65'
driver.get(url) # open web
time.sleep(3)

page_html = driver.page_source
data = soup(page_html,'html.parser') # Scan data
#html.parser: แปลง source code ให้กลับไปเป็น html

driver.close()

#ขั้นตอนการดึงข้อมูลจาก html

raw = data.find("body", {"class": "claro ember-application"})

ember89 = raw.find("div",{"id":"ember89","class":"dock-element ember-view"})

g = ember89.findAll('text')

#จำนวนผู้ป่วยที่ update จาก dashboard
g[1]

covid_num = g[1].text

print("=========Ene Scraping==========")


########################
#ส่วนของการ savefile

currentDT = datetime.datetime.now()
key = currentDT.strftime("%Y-%m-%d %H:%M:%S")
value = covid_num


# csv_file = 'covid19-thai-recorded.csv'
#Openfile
with open('covid19-thai-recorded.csv') as f:
    d = dict(filter(None, csv.reader(f)))

#ดูประวัติ dictionary
print(d)
 
#Get the last number of covid19's patients
while True:
    try: 
        last_covid19  =   d[  list( d.keys())[-1] ] 
        break

    except ValueError:
        last_covid19  =   covid_num
    


#Update dictionary
d.update( {key  : last_covid19 } )


#Save
with open('covid19-thai-recorded.csv', 'w', newline="") as csv_file:  
    writer = csv.writer(csv_file)
    for k, v in d.items():
       writer.writerow([k, v])






########################
#ส่วนการส่ง Line

#Send to Line
#อย่าลืมสร้าง Token นะครับ

token_me = ' ... '
token_line_group = ' ... '


currentDT = datetime.datetime.now()

print ( currentDT.strftime("%Y-%m-%d %H:%M:%S") )

time_today =  str( currentDT.strftime("%Y-%m-%d  %H:%M:%S") )

text_ = 'ขณะนี้มียอดผู้ป่วย Covid19 ในประเทศไทยที่ยืนยันแล้ว \nจำนวน ' + covid_num + ' คน \nข้อมูลวันที่ '+ time_today

print(text_)


last_covid19    = int( last_covid19  )
covid_num       = int( covid_num ) 

if (covid_num > last_covid19):

    text_  = text_  + '\nมียอดผู้ป่วยเพิ่มขึ้น : ' + str( covid_num - last_covid19 ) + ' คน'

    messenger = Sendline( token_me  )
    messenger.sendtext(text_)

    messenger = Sendline( token_line_group )
    messenger.sendtext(text_)

elif (covid_num < last_covid19):
        
    text_  = text_  + '\nมียอดผู้ป่วยลดลง: ' + str(  last_covid19 - covid_num )+ ' คน'
    
    messenger = Sendline( token_me  )
    messenger.sendtext(text_)


    messenger = Sendline(token_line_group)
    messenger.sendtext(text_)

else :
    messenger = Sendline( token_me  )
    messenger.sendtext(text_)

    messenger = Sendline( token_line_group )
    messenger.sendtext(text_)
