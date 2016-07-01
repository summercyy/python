#encoding: utf8
#python3
import urllib
import urllib.request
import re
import os
import zlib
import queue
import time
import threading

visited_url = {""}
to_visit_url = queue.Queue(maxsize = 0)
to_visit_url.put("http://m.sohu.com/")
url_num = 0
filepath = 'msohu/'
filename = 'log.txt'

class Check(threading.Thread):
	def __init__(self, url):
		threading.Thread.__init__(self)

	def run(self):
		check_url(url)


#获得http请求响应码
def get_status(target_url):
	try:
		status = urllib.request.urlopen(target_url).code
		return status
	except BaseException as msg:
		print(msg)

#获得网页内容
def get_data(target_url):
	try:
		req = urllib.request.Request(target_url, headers={'Accept-Encoding': 'gzip'})
		page = urllib.request.urlopen(req)
		content_encoding = page.info().get("Content-Encoding")
		if content_encoding == 'gzip':
			data = zlib.decompress(page.read(),16+zlib.MAX_WBITS)
		elif content_encoding == None:
			data = page.read()
		else:
			return ""
		return data
	except BaseException as msg:
		print(msg)

#从网页内容中找出符合要求的url
def find_url_match(content):
	if content == None:
		return
	global to_visit_url
	url_str = '<a href="?(http://[^<>" ]*m.sohu.com/[^<>" ]*|/[^<>" ]+)"'
	url_pattern = re.compile(url_str)
	for match in url_pattern.finditer(content):
		#print(match.group(1))
		new_url = match.group(1)
		if new_url[0] == '/':
			new_url = "http://m.sohu.com" + new_url
		to_visit_url.put(new_url)
	return 

def check_url(target_url):
	global visited_url
	#print("in check_url")
	if target_url in visited_url:
		return
	try:
		global url_num, filepath, filename
		status = get_status(target_url)
		visited_url.add(target_url)
		url_num += 1
		if status == 200:
			#with open(filepath+filename, 'a') as savingData:
			#	current_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
			#	log = current_time+'\t'+str(status)+'\t'+target_url+'\n'
			#	savingData.write(log)
			data = get_data(target_url)
			find_url_match(data.decode('utf-8'))
		else:
			with open(filepath+filename, 'a') as savingData:
				current_time = time.strftime('%Y-%m-%d  %H:%M:%S', time.localtime(time.time()))
				log = current_time+'\t'+str(status)+'\t'+target_url+'\n'
				savingData.write(log)
		return 
	except BaseException as msg:
		print(msg)




print("begin")

#创建目录
if os.path.isdir(filepath):
	pass
else:
	os.mkdir(filepath)

#创建文件
with open(filepath+filename, 'w') as writing:
	writing.write("Test m.sohu.com: \n")

#递归检测
while not(to_visit_url.empty()):
	url = to_visit_url.get()
	#print(url)
	check_thread = Check(url) #使用线程
	check_thread.run()

print("Finish")

