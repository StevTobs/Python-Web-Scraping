'''

Covid19-Thai
Copyright (C) 2004 Akanit Kwangkaew
www.facebook.com/codingjingjo
"1.1"

'''


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from songline import Sendline
import time
import datetime 
import csv 
from bs4 import BeautifulSoup as soup


class Covid19_thai:

    def __init__(self, url, csv_path):
        self.csv_path = csv_path
        print("Loading ...", end ="")
        opt = webdriver.ChromeOptions()
        opt.add_argument('headless') #hidden mode of chorme driver
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        print(".", end ="")
        driver = webdriver.Chrome(options=opt) #create driver   
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

    def get_patient_url_1(self):

        self.ref_url_1 = "covid19.workpointnews.com"
        

        #ดึงจำนวนผู้ป่วย
        raw = self.data.find("div", {"class": "css-ttf0vs e9w21k51"})
        covid19_patient_thai = raw.find("div", {"class": "css-5455pe e2xuun72"})
        self.covid_num = covid19_patient_thai.text

        #ดึงจำนวนผู้ป่วยที่เปลี่ยนแปลง
        # <div class="css-rwqtsj e2xuun73">(เพิ่ม 188 คน) เมื่อ 22/3/2020</div>
        raw = self.data.find("div", {"class": "css-rwqtsj e2xuun73"})       
        self.covid_change_num = raw.text

        #รักษาหายแล้ว
 
        raw = self.data.find("div", {"class": "e9w21k54 css-xn1zjs e2xuun70"})
        raw = raw.find("div", {"class": "css-bj5ob2 e2xuun72"})
        self.covid_recover_num = raw.text


        #ดึงจำนวนผู้เสียชีวิต
        # <div class="e9w21k55 css-9se48y e2xuun70"><div class="css-1mxp76p e2xuun71">เสียชีวิต</div><div class="css-bj5ob2 e2xuun72">1</div></div>
        raw = self.data.find("div", {"class": "e9w21k55 css-9se48y e2xuun70"} )
        
        covid_dead = raw.find("div", {"class": "css-bj5ob2 e2xuun72"})
        self.covid_dead_num = covid_dead.text

        return self.covid_num, self.covid_change_num, self.covid_recover_num, self.covid_dead_num, self.ref_url_1

    def get_previous_patient(self):

        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1)
        covid_num, dummy, dummy, dummy, dummy = self.get_patient_url_1()
        
        csv_path = self.csv_path

        #Openfile
        with open(csv_path) as f:
            d = dict(filter(None, csv.reader(f)))
        
        #Get the last number of covid19's patients
        while True:
            try: 
                last_covid19  =   d[  list( d.keys())[-1] ] 
                break

            except ValueError:
                last_covid19  =   covid_num
        return last_covid19 

    def update_to_csv (self):
        csv_path = self.csv_path
        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1)
        covid_num, dummy, dummy, dummy, dummy  = self.get_patient_url_1()

        currentDT = datetime.datetime.now()

        #เตรียมข้อมูลที่จะ Update
        key = currentDT.strftime("%Y-%m-%d %H:%M:%S")
        value = covid_num
     
        with open(csv_path) as f:
            d = dict(filter(None, csv.reader(f)))

        #Update dictionary
        d.update( {key  : value} )

        #Save
        with open( csv_path , 'w', newline="") as csv_file:  
            writer = csv.writer(csv_file)
            for k, v in d.items():
                writer.writerow([k, v])
    
    def report(self):
        
        currentDT = datetime.datetime.now()       
        time_today =  str( currentDT.strftime("%d-%m-%Y %H:%M:%S") )

        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1)
        covid_num, covid_change_num, covid_recover_num, covid_dead_num, ref_url_1 = self.get_patient_url_1()

        chk_change , text = self.check_change()

        report_text = text + '\nขณะนี้มียอดผู้ป่วย COVID19 ในประเทศไทย\nจำนวน: '+covid_num+' คน'
        report_text = report_text + '\n ' + covid_change_num
        report_text = report_text + '\nรักษาหาย: '+covid_recover_num+' คน'
        report_text = report_text + '\nเสียชีวิต: '+covid_dead_num +' คน'
        report_text = report_text + '\nTime: '+ time_today
        report_text = report_text + '\nSource: '+ ref_url_1
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


        #ดึงข้อมูลจากแหล่งข่าวที่ 1 (url_1)
        covid_num, dummy, dummy, dummy, dummy  = self.get_patient_url_1()

        prev_patient = int( self.get_previous_patient( ) )
        last_patient = int( covid_num)

        print("prev_patient", prev_patient)
        print("last_patient", last_patient)

        if(prev_patient != last_patient):  

            if(prev_patient < last_patient):
                text = 'มียอดผู้ป่วยเพิ่มขึ้น '+ str(last_patient - prev_patient)  
                chk_change = True
                return chk_change , text

            elif (prev_patient > last_patient) :   
                text = 'มียอดผู้ป่วยลดลง' + str( prev_patient - last_patient)  + ' :)'
                chk_change = True

                return chk_change , text
                             
        else:
            chk_change = False
            return chk_change , text


if __name__ == "__main__":

    #แหล่งข่าว url1: Work Point News
    url_1 = 'https://covid19.workpointnews.com/?fbclid=IwAR0WRCG6g4vr6amf5XiXNpIzRImCpK3b3nMK2vGuyMCpwYEB7Maan0Z_BKM'
    covid19_thai = Covid19_thai(url_1, 'covid19-thai-recorded.csv')
    covid19_thai.report()

    #เช็คยอดผู้ป่วยที่เปลี่ยนแปลง
    chk, dmm  = covid19_thai.check_change()

    #ส่ง Line เมื่อยอดผู้ป่วยเปลี่ยนแปลง
    if(chk == True ):

        token = {   "token"          : '< input your token here!!! >'}
        covid19_thai.send_Line( token )