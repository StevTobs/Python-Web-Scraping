#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Covid19-Thai
Copyright (C) 2020 Akanit Kwangkaew
www.facebook.com/codingjingjo
"1.4"

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from songline import Sendline
import time
import datetime 
import csv 
from bs4 import BeautifulSoup as soup
import json

class Covid19_thai:

    def __init__(self, url, csv_path):
        self.csv_path = csv_path
        print("Loading .", end ="")
        # driver = webdriver.Chrome(executable_path='C:/path/to/chromedriver.exe')
        opt = webdriver.ChromeOptions()
        opt.add_argument('headless') #hidden mode of chorme driver
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        print(".", end ="")
        driver = webdriver.Chrome(options=opt, executable_path = '/Users/TopBook/Google Drive/CODE/AUTORUN/chromedriver')
        # driver = webdriver.Chrome(options=opt) #create driver   
        print(".", end ="")    
        driver.get(url) # open web
        print(".", end ="")
        time.sleep(3)
        print(".", end ="")
        page_html = driver.page_source
        print(".", end ="")
        #html.parser: แปลง source code ให้กลับไปเป็น html
        self.data = soup(page_html,'html.parser')
        print(".", end ="")
        driver.close()
        print(".")
    
#    def get_patient_url_1(self):
#
#        self.ref_url_1 = "covid19.workpointnews.com"
#        
#
#        #ดึงจำนวนผู้ป่วย
#        raw = self.data.find("div", {"class": "css-ttf0vs e9w21k51"})
#        # print(raw)
#        covid19_patient_thai = raw.find("div", {"class": "css-b10qi3 e2xuun72"})
#        self.covid_num = covid19_patient_thai.text
#
#        #ดึงจำนวนผู้ป่วยที่เปลี่ยนแปลง
#       
#        covid_change = raw.find("div", {"class": "css-rwqtsj e2xuun73"})       
#        self.covid_change_num = covid_change.text
#        print(covid_change)
#        #รักษาหายแล้ว
# 
#        covid_recover = raw.find("div", {"class": "e9w21k54 css-1w3ca84 e2xuun70"})
#        covid_recover = covid_recover.find("div", {"class": "css-9bda02 e2xuun72"})
#        
#        self.covid_recover_num = covid_recover.text
#
#
#        #ดึงจำนวนผู้เสียชีวิต
#        # <div class="e9w21k55 css-9se48y e2xuun70"><div class="css-1mxp76p e2xuun71">เสียชีวิต</div><div class="css-bj5ob2 e2xuun72">1</div></div>
#        
#        covid_dead = raw.find("div", {"class": "e9w21k55 css-ntnmqw e2xuun70"})
#       
#        self.covid_dead_num = covid_dead.find("div", {"class": "css-9bda02 e2xuun72"}).text
#
#        return self.covid_num, self.covid_change_num, self.covid_recover_num, self.covid_dead_num, self.ref_url_1
    
    def get_patient_url_2(self):

        self.ref_url_2 = 'https:/covid19.th-stat.com/api/open/today'
        x = json.loads(self.data.text)
        
        #print(self.data.text)
        
        self.covid_num = x["Confirmed"]
        self.covid_change_num = x["NewConfirmed"]
        self.covid_recover_num = x["Recovered"]
        self.covid_dead_num = x["Deaths"]

        
       
        return self.covid_num, self.covid_change_num, self.covid_recover_num, self.covid_dead_num, self.ref_url_2

    def get_previous_patient(self):

        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1)
        covid_num, dummy, dummy, dummy, dummy = self.get_patient_url_2()
        
        csv_path = self.csv_path

        #Openfile
        with open(csv_path+ 'covid19-thai-recorded.csv') as f:
            d = dict(filter(None, csv.reader(f)))
        
        
        while True:
            try: 
                #Get the last number of covid19's patients
                last_covid19  =   d[  list( d.keys())[-1] ] 
                break

            except ValueError:
                last_covid19  =   covid_num

        return last_covid19 

    def update_to_csv (self, chk):
        csv_path = self.csv_path
        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1)
        covid_num, dummy, dummy, dummy, dummy  = self.get_patient_url_2()
        covid_num = int(covid_num.replace(',', ''))
        
        currentDT = datetime.datetime.now()

        #เตรียมข้อมูลที่จะ Update
        key = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        value = covid_num
     
        with open(csv_path + 'covid19-thai-recorded.csv') as f:
            d = dict(filter(None, csv.reader(f)))

        #Update dictionary
        d.update( {key  : value} )

        #Save
        with open( csv_path + 'covid19-thai-recorded.csv', 'w', newline="") as csv_file:  
            writer = csv.writer(csv_file)
            for k, v in d.items():
                writer.writerow([k, v])
        print("Saved to CSV!!")

        if( chk == True ):
            #Backup

            with open(csv_path + 'covid19-thai-recorded_backup.csv') as f:
                d = dict(filter(None, csv.reader(f)))

            #Update dictionary
            
            key = currentDT.strftime("%Y-%m-%d")
            value = covid_num
            d.update( {key  : value} )
            with open( csv_path + 'covid19-thai-recorded_backup.csv' , 'w', newline="") as csv_file:  
                writer = csv.writer(csv_file)
                for k, v in d.items():
                    writer.writerow([k,  v])
            
            print("Backed up to CSV!!")
    
    def report(self):
        
        currentDT = datetime.datetime.now()       
        time_today =  str( currentDT.strftime("%d-%m-%Y %H:%M:%S") )

       
        covid_num, covid_change_num, covid_recover_num, covid_dead_num, ref_url_2 = self.get_patient_url_2()

        chk_change , text = self.check_change()

        report_text = 'ยอดผู้ป่วย COVID19 ในไทย\nสะสม: '+str(covid_num)+' คน ' + str(covid_change_num)

        # report_text = report_text + '\n ' + covid_change_num
        report_text = report_text + '\nรักษาหาย: '+str(covid_recover_num)+' คน'
        report_text = report_text + '\nเสียชีวิต: '+str(covid_dead_num) +' คน'
        report_text = report_text + '\nTime: '+ time_today
        report_text = report_text + '\nSource: '+ ref_url_2
        # print(report_text )

        return report_text

    def send_Line(self, token):

        text = self.report()

        for k , tk in token.items() :
            messenger = Sendline( tk )
            messenger.sendtext(text)
            print('Sent to :'+ k )

    def check_change(self):

        chk_change = False
        text = ""


        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1
        #covid_num, covid_change_num, covid_recover_num, covid_dead_num, ref_url_1  = self.get_patient_url_1()
        
        #Update
        covid_num, covid_change_num, covid_recover_num, covid_dead_num, ref_url_2  = self.get_patient_url_2()

        prev_patient = self.get_previous_patient( ) 
        prev_patient = int(prev_patient.replace(',', ''))

        last_patient = covid_num
        #last_patient = int(last_patient.replace(',', ''))

        #covid_recover_num = int( covid_recover_num.replace(',', ''))
        #covid_dead_num = int( covid_dead_num.replace(',', ''))

        if(prev_patient != last_patient and int(covid_recover_num) !=0 and int(covid_dead_num) != 0 ):  

            if(prev_patient < last_patient):
                text = covid_change_num
                chk_change = True
                return chk_change , text

            elif (prev_patient > last_patient and int(covid_recover_num) !=0 and int(covid_dead_num != 0) ) :   
                text = covid_change_num
                chk_change = True

                return chk_change , text
                             
        else:
            chk_change = False
            return chk_change , text


if __name__ == "__main__":

    #แหล่งข่าว url1: Work Point News
    #url_1 = 'https://covid19.workpointnews.com/?fbclid=IwAR0WRCG6g4vr6amf5XiXNpIzRImCpK3b3nMK2vGuyMCpwYEB7Maan0Z_BKM'
    url_2 = 'https:/covid19.th-stat.com/api/open/today'
    #Path for MAC
    PATH_MAC = '/Users/TopBook/Google Drive/CODE/AUTORUN/'
    covid19_thai = Covid19_thai(url_2, PATH_MAC)
    txt = covid19_thai.get_patient_url_2()


    # chk, dmm  = covid19_thai.check_change()
    covid19_thai.report()

    #https:/covid19.th-stat.com/api/open/today
  


    

if __name__ == "__main__":

    #แหล่งข่าว url1: Work Point News
    # url = 'https://covid19.workpointnews.com/?fbclid=IwAR0WRCG6g4vr6amf5XiXNpIzRImCpK3b3nMK2vGuyMCpwYEB7Maan0Z_BKM'
    # url = "https://covid19-cdn.workpointnews.com/api/constants.json"
    url_2 = 'https:/covid19.th-stat.com/api/open/today'
    #Path for MAC
    PATH_MAC = '/Users/TopBook/Google Drive/CODE/AUTORUN/'
    covid19_thai = Covid19_thai(url_2, PATH_MAC+ 'covid19-thai-recorded.csv')
    # print( covid19_thai.report())

    token_all = {   "user1 (ตังเอง)"           : '< user 1 - Token >',
                    "ีuser2"       : '< please insert Token >',
                    "user3"        : '< please insert Token >',
                    "user4"         : '< please insert Token >',
                    "user5" : '< please insert Token >' 
            }
    chk, dmm  = covid19_thai.check_change()

    covid19_thai.get_patient_url_2()

    if( chk == False ):

        token = {   "user1 (ตังเอง)"          : '< please insert Token >'}
        covid19_thai.send_Line( token)
        messenger = Sendline(  token [ "user1 (ตังเอง)" ]    )
        messenger.sendtext("The program is running...")
        print("The program is running...")

    elif( chk ):
        
        # covid19_thai.send_Line(  token_all )
        print("Send to ALL ")
    
    covid19_thai.update_to_csv(chk)
