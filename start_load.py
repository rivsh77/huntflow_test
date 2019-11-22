# -*- coding: utf-8 -*-
# Variables
API_ENDPOINT = 'https://dev-100-api.huntflow.ru'
UA = "App/1.0 (test@huntflow.ru)"

# Libraries
import requests, re
import json
import xlrd
from requests_toolbelt.multipart.encoder import MultipartEncoder
from os import listdir
from os.path import isfile, join


def get_account_id(access_token):
    r = requests.get('%s/accounts' % API_ENDPOINT,
                     headers={'user-agent': UA, 'Authorization': 'Bearer ' + access_token})
    # {"items": [{"member_type": "manager", "name": "\u0425\u0430\u043d\u0442\u0444\u043b\u043e\u0443 \u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0435", "nick": "huntflow", "production_calendar": null, "id": 2}]}
    j = r.text
    account_id = json.loads(j)["items"][0]["id"]
    print(account_id)
    return account_id
	
def get_vacancy_id(account_id, access_token, position_nm):
    r = requests.get('%s/account/%s/vacancies' % (API_ENDPOINT, account_id),
                     headers={'user-agent': UA, 'Authorization': 'Bearer ' + access_token})
    # {"items": [{"member_type": "manager", "name": "\u0425\u0430\u043d\u0442\u0444\u043b\u043e\u0443 \u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0435", "nick": "huntflow", "production_calendar": null, "id": 2}]}
    j = r.text
    print(j)
    for record in json.loads(j)['items']:
		pos_name = record["position"] #.encode('utf-8')
		v_id = record["id"]
		print(pos_name)
		print(v_id)
		if pos_name == position_nm:
			vac_id = v_id
    
    return vac_id
	
def get_vacancystatuses_id(account_id, access_token, status_nm):
    r = requests.get('%s/account/%s/vacancy/statuses' % (API_ENDPOINT, account_id),
                     headers={'user-agent': UA, 'Authorization': 'Bearer ' + access_token})
    # {"items": [{"member_type": "manager", "name": "\u0425\u0430\u043d\u0442\u0444\u043b\u043e\u0443 \u0422\u0435\u0441\u0442\u043e\u0432\u043e\u0435", "nick": "huntflow", "production_calendar": null, "id": 2}]}
    j = r.text
    print(j)
    for record in json.loads(j)['items']:
		st_name = record["name"].encode('utf-8')
		s_id = record["id"]
		print(st_name)
		print(s_id)
		if st_name == status_nm:
			st_id = s_id
		else:
			st_id = 'null'		
    
    return st_id


def xlsParse(xlsfile):
    wb = xlrd.open_workbook(xlsfile)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)

    store = []

    for rx in range(1, sheet.nrows):
        packet = {
            "dolzhn": sheet.row(rx)[0].value,
            "fio": sheet.row(rx)[1].value,
            "zp": sheet.row(rx)[2].value,
            "comment": sheet.row(rx)[3].value,
            "status": sheet.row(rx)[4].value
        }
        store.append(packet)
    print(store)
    return store


def post_applicants(account_id, access_token, candidate, acc_file_id):
    try:
        last_name = candidate["fio"].split()[0]
        first_name = candidate["fio"].split()[1]
        middle_name = candidate["fio"].split()[1]
        position = candidate["dolzhn"]
        money = candidate["zp"]
        data_js = {
            'last_name': last_name,
            'first_name': first_name,
            'middle_name': middle_name,
            'position': position,
			'money': money,
			'externals': [{"auth_type": "NATIVE", "files": [{"id": acc_file_id}]}]
        }
        print(data_js)
        js_data2 = json.dumps(data_js)
        r = requests.post('%s/account/%s/applicants' % (API_ENDPOINT, account_id), data=js_data2,
                          headers={'user-agent': UA, 'Authorization': 'Bearer ' + access_token})
        print(r.text)
        j = r.text
        cand_id = json.loads(j)["id"]
        return cand_id

    except Exception as err:
        print('\n\n********************\n********************\n\.\nException caught:\n\n%s ' % (err))
		
def post_applicants_vacancy(account_id, access_token, vacancy_id, status_id, comm, acc_file_id, appl_id):
    try:
		'''v = status_name.decode('utf-8')
		print(v)	 
		if status_name == "Отказ":		
			rejection_reason = comm
		else:
			rejection_reason = 'null'
		'''	
		data_js = {
            'vacancy': vacancy_id,
            'status': status_id,
            'comment': comm,
			'files': [{"id": acc_file_id}]
        }
		print(data_js)
		js_data2 = json.dumps(data_js)
		r = requests.post('%s/account/%s/applicants/%s/vacancy' % (API_ENDPOINT, account_id, appl_id),
                data=js_data2,headers={'user-agent': UA, 'Authorization': 'Bearer ' + access_token})
		print(r.text)

    except Exception as err:
        print('\n\n********************\n********************\n\.\nException caught:\n\n%s ' % (err))


def file_upload(account_id, access_token, file_path_account):
    try:

        mp_encoder = MultipartEncoder(
            fields={
                # plain file object, no filename or mime type produces a
                # Content-Disposition header with just the part name
                'file': (file_path_account, open(file_path_account, 'rb'), 'text/plain'),
            }
        )
        r = requests.post(
            '%s/account/%s/upload' % (API_ENDPOINT, account_id),
            data=mp_encoder,  # The MultipartEncoder is posted as data, don't use files=...!
            # The MultipartEncoder provides the content-type header with the boundary:
            headers={'user-agent': UA, 'Authorization': 'Bearer ' + access_token, 'Content-Type': mp_encoder.content_type}
        )
        print(r.text)
        j = r.text
        file_id = json.loads(j)["id"]
        file_url = json.loads(j)["url"]
        print(file_id)
        print(file_url)
        return file_id
 #{"name": "\u0422\u0430\u043d\u0441\u043a\u0438\u0438\u0306 \u041c\u0438\u0445\u0430\u0438\u043b.pdf", "id": 8, "content_type": "application/pdf", "url": "https://dev-100-store.huntflow.ru/uploads/named/y/t/u/ytu20vbmlgg1elxifgrz2inhlp7ex9x3.pdf/%25D0%25A2%25D0%25B0%25D0%25BD%25D1%2581%25D0%25BA%25D0%25B8%25D0%25B8%25CC%2586%2B%25D0%259C%25D0%25B8%25D1%2585%25D0%25B0%25D0%25B8%25D0%25BB.pdf?s=UHGjfOX_Hd66IZAp5go8YA&e=1574313358"}

    except Exception as err:
        print('\n\n********************\n********************\n\.\nException caught:\n\n%s ' % (err))

personal_access_token = '71e89e8af02206575b3b4ae80bf35b6386fe3085af3d4085cbc7b43505084482'
db_file = ("C:\\Specsoft\\lic_fee\\test.xlsx")
acc_id = get_account_id(personal_access_token)
candidates = xlsParse(db_file)
print(db_file)
file_path = db_file.rsplit('\\', 1)[0]

for c in candidates:
	pos_name = c["dolzhn"]
	stat_name = c["status"].encode('utf-8') 	#stat_name = candidates[0]["status"].encode('utf-8') #"Резюме у заказчика"
	comm = c["comment"].encode('utf-8')	        #comm = candidates[0]["comment"].encode('utf-8')
	fio = c["fio"]
	file_path_f = file_path + "\\" + pos_name + "\\" 
	files = listdir(file_path_f)
	mytxt = filter(lambda x: x.startswith(fio), files)
	file_path_acc = file_path_f + mytxt[0]
	print(file_path_acc)
	cur_file_id = file_upload(acc_id, personal_access_token, file_path_acc) #8
	print(cur_file_id)
	applicant_id = post_applicants(acc_id, personal_access_token, c, cur_file_id) #72
	print(applicant_id)
	vacancy_id = get_vacancy_id(acc_id, personal_access_token, pos_name)     #2
	print(vacancy_id)

	status_id = get_vacancystatuses_id(acc_id, personal_access_token, stat_name)
	print(status_id)	

	post_applicants_vacancy(acc_id, personal_access_token, vacancy_id, status_id, comm, cur_file_id, applicant_id) 
