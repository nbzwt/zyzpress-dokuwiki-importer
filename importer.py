# -*- coding: utf-8 -*-
import os
from datetime import datetime
from pymongo import MongoClient
import subprocess
import shutil
import json

blogRoot = 'dokuwiki/data/pages/blog'
imageRoot = 'dokuwiki/data/media'

blogList = []
tagList = []
catList = []

def procDir(rootDir):
	for lists in os.listdir(rootDir):
		path = os.path.join(rootDir, lists)
		if os.path.isdir(path):
			procDir(path)
		else:
			dateStr = rootDir[-4:] + lists[:4]
			blogEntity = {}
			blogEntity['path'] = path
			blogEntity['date'] = datetime.strptime(dateStr, '%Y%m%d')
			blogList.append(blogEntity)

def procEntity(blogEntity):
	f = open(blogEntity['path'])
	title = f.readline()
	content = f.read()
	title = title[7:-8]

	#remove the blank line in the beginning
	while (content[0] == '\n'):
		content = content[1:]
	#get rid of the ~~DISCUSSION~~
	content = content.replace('~~DISCUSSION~~', '')
	#remove the blank line in the end
	while (content[-1] == '\n'):
		content = content[:-1]

	blogEntity['title'] = title
	blogEntity['content'] = {'encoding': 'HTML', 'content': content}
	del blogEntity['path']
	blogEntity['category'] = 'Uncategorized'
	blogEntity['tags'] = [];	
	f.close()

def getTags():
	conti = True
	tags = []
	while (conti):
		print('Available tags:')
		i = 0
		for tag in tagList:
			i = i + 1
			print(i, ': ', tag)
		print('Current tags:')
		print(tags)
		x = int(input('Select a tag, 0 for new: '))
		if (x == 0):
			tag = input('Input a new tag: ')
			if (tag != ''):
				tags.append(tag)
				tagList.append(tag)
		else:
			tags.append(tagList[x-1])
		if input('Add another?(y/n) ') == 'n':
			conti = False
	return tags

def getCat():
	ncat = ''
	print('Available categories:')
	i = 0
	for cat in catList:
		i = i + 1
		print(i, ': ', cat)
	x = int(input('Select a category, 0 for new: '))
	if (x == 0):
		cat = input('Input a new category: ')
		ncat = cat
		catList.append(cat)
	else:
		ncat = catList[x-1]
	return ncat

def setCatTags(blogEntity):
	retry = True
	print('Aritcle: ', blogEntity['title'])
	while retry:
		category = getCat()
		tags = getTags()
		print('Category: ', category, ' Tags: ', tags)
		if input('Looks good?(y/n) ') == 'y':
			retry = False
	blogEntity['category'] = category
	blogEntity['tags'] = tags	

def writeDb():
	client = MongoClient('localhost', 27017)
	db = client['blog']
	db.posts.remove({})
	result = db.posts.insert_many(blogList)
	print("Finished. Inserted ids:")
	print(result.inserted_ids)

def date(blogEntity):
	return blogEntity['date'].timestamp()

def render(blogEntity):
	tempdk = open('tempdk', 'w')
	tempdk.write(blogEntity['content']['content'])
	tempdk.close()
	tempdk = open('tempdk')
	tempht = open('tempht', 'w')
	p = subprocess.Popen('./dokuwiki/bin/render.php', stdin=tempdk, stdout=tempht)
	p.wait()
	tempht.flush()
	tempdk.close()
	tempht.close()
	tempht = open('tempht')
	content = tempht.read();
	content = content.replace('/./dokuwiki/bin/lib/exe/fetch.php?media=', 'img/')
	#handle more. Add it after the second occurance of </p>
	more = content.find('</p>', content.find('</p>') + 1)
	if (more != -1):
		more = more + 4
		content = content[:more] + '\n<!-- more -->\n' + content[more:]
	blogEntity['content']['content'] = content
	tempht.close()
	os.remove('tempht')
	os.remove('tempdk')

def copyPhoto(rootDir):
	for lists in os.listdir(rootDir):
		path = os.path.join(rootDir, lists)
		if os.path.isdir(path):
			copyPhoto(path)
		else:
			dstFile = path[len(imageRoot)+1:].replace('/',':')
			shutil.copy(path, 'img/'+dstFile)

def loadJson():
	fjson = open('posts.json')
	jlist = json.loads(fjson.read())
	fjson.close()
	for jsonEntity in jlist:
		title = jsonEntity['title']
		tags = jsonEntity['tags']
		category = jsonEntity['category']
		for blogEntity in blogList:
			if (blogEntity['title'] == title):
				print('Importing category ', category, 'and tags ', tags, ' for blog entity ', title, '.')
				blogEntity['tags'] = tags
				blogEntity['category'] = category

def main():
	procDir(blogRoot)
	blogList.sort(key = date, reverse=True)
	for blogEntity in blogList:
		procEntity(blogEntity)
	print('Imported.')
	for blogEntity in blogList:
		render(blogEntity)
	print('Rendered.')
	if input('Do you want to copy the image folder?(y/n) ') == 'y':
		if not os.path.exists('img'):
			os.makedirs('img')
		copyPhoto(imageRoot)
	if input('Want to import the json?(y/n) ') == 'y':
		loadJson()
	if input('Want to change the category and tags?(y/n) ') == 'y':
		for blogEntity in blogList:
			setCatTags(blogEntity)
	if input('Write result to db (This will OVERWRITE the existing db!)?(y/n) ') == 'y':
		writeDb()

if __name__ == '__main__':
	main()
