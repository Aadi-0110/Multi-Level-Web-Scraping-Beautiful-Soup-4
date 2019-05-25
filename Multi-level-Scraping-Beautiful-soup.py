from bs4 import BeautifulSoup
import json
import re
import requests

def has_id_but_no_class(tag):
    return tag.has_attr('id') and not tag.has_attr('class')

def make_description(llist):
    for tag in llist:
        if tag.text[:6] == "<p><p>":
            pass
        elif tag.text[:9] == "<p><p><p>":
            pass
        else:
            data = re.sub('<strong>|<\/strong>,|<\/strong>|\n|<p>|</p>|Address:|', '', str(tag.text))
            data = re.sub('\r', " ", str(data))
            return data
            

def make_address(llist):
    s = {}
    location = {}
    try:
        ad = llist[0]
        ad = re.sub('<strong>|<\/strong>,|<\/strong>|\n|<p>|</p>|Address:|\r', '', str(ad))
        s['addressLine1'] = ad
        x = llist[1]
        x = re.sub('<strong>|<\/strong>,|<\/strong>|\n|<p>|</p>|\r', '', str(x))
        x = x.rstrip(' ')
        x = x.lstrip(" ")
        j = x.split(",")
        for i in j:
            k,v = i.strip(" ").split(":")
            s[k.strip(" ").lower()] = v.strip(" ")

        t = llist[2].find('a')['href']
        tj = re.sub('http:\/\/maps\.google\.com\/\?q=', '', str(t))
        lat, long = tj.split(",")
        location["latitude"] = lat
        location["longitude"] = long
    #     print(s)
    except:
        pass
    return s,location

def get_details(url):
    finald = {}
    url = 'http://jainmandir.org' + url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all(has_id_but_no_class)
    div_des = divs[1].find_all('p')
    div_contact = divs[2].find_all('p')
    div_services = divs[3].find_all(class_='service-text')
    div_our_work = [i['href'] for i in divs[4].find_all('a')]
#     print(div_contact, div_services, div_our_work)
    address, location = make_address(div_contact)
    images = div_our_work
    desc = make_description(div_des)
#     print(div_des, desc)
#     print(finald["Contact"])
    return address, location, images, desc


# states = ['Rajasthan', 'Bengal', 'Orissa', 'Jharkhand', 'Delhi', 'Karnataka', 'Kerela', 'Bihar', 'Madhya', 'Andhra', 'Telengana', 'Maharashtra', 'Chattisgarh', 'Punjab', 'Haryana', 'Uttar', 'Himachal']
states=['Andhra', 'Arunachal', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal', 'Jammu', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil', 'Telangana', 'Tripura', 'UttarPradesh', 'Uttarakhand', 'Bengal', 'Andaman', 'Chandigarh', 'Dadra', 'Daman', 'Lakshadweep', 'Delhi', 'Puducherry']
l = []
file = open('final_jain_temples.json', 'a+')
error = open('error.log', 'a+')
#states = ['Rajasthan','Bengal','Jharkhand']
for state in states:
    url = 'http://jainmandir.org/MainPage/Search/' + state
    res = requests.get(url)
    soup = BeautifulSoup(res.text , 'html.parser')
    table = soup.find(class_='table table-bordered table-responsive')
    thead = table.find('thead')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')
    for tr in trs:
        try:
            newd = {"publishType": "PUBLISHED",
          "verificationType": "VERIFIED",
          "type": "MANDIR",
          "kshetra": "ATISHAY",
          "mulnayak": "TIRTHANKAR",
          "panth": "TERAPANTH"}
            tds = tr.find_all('td')
            newd["name"] = tds[0].text
            newd["sect"] = tds[1].text
            newd["address"], newd["location"], newd["images"], newd["description"] = get_details(tds[2].find('a')["href"])
            l.append(newd)
        except:
            print(tr, file=error)
            print("error occured")
    print("done ==> {}%".format((states.index(state)/len(states))*100))
z = json.dumps(l)
print(z, file=file)
file.close()
error.close()