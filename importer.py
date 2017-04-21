#-*- coding: utf-8 -*-
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
slugList = []

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
	blogEntity['tags'] = []	
	blogEntity['slug'] = ''
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

def checkList():
	for blogEntity in blogList:
		slug = blogEntity['slug']
		if slug == '':
			print('Error: ', blogEntity['title'], ' has a null slug.')
			return False
	return True

def writeDb():
	if checkList():
		client = MongoClient('localhost', 27017)
		db = client['blog']
		if input('Do you want to remove all pre-existing entries?(y/n) ') == 'y':
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
	content = content.replace('/./dokuwiki/bin/lib/exe/fetch.php?media=', 'http://zephray.cnvintage.org/img/')
	#handle more. Add it after the third occurance of </p>
	more = content.find('</p>', content.find('</p>', content.find('</p>') + 1) + 1)
	if (more != -1):
		more = more + 4
		content = content[:more] + '\n<!-- more -->\n' + content[more:]
	blogEntity['content']['content'] = content
	tempht.close()
	os.remove('tempht')
	os.remove('tempdk')

def copyPhoto(rootDir):
	if not os.path.exists('img'):
			os.makedirs('img')
	for lists in os.listdir(rootDir):
		path = os.path.join(rootDir, lists)
		if os.path.isdir(path):
			copyPhoto(path)
		else:
			dstFile = path[len(imageRoot)+1:].replace('/',':')
			shutil.copy(path, 'img/'+dstFile)

def setCatMenu():
	for blogEntity in blogList:
		if blogEntity['category'] == 'Uncategorized':
			retry = True
			print('Article: ', blogEntity['title'])
			while retry:
				category = getCat()
				print('Category: ', category)
				if input('Looks good?(y/n) ') == 'y':
					retry = False
			blogEntity['category'] = category

def setTagMenu():
	for blogEntity in blogList:
		if blogEntity['tags'] == []:
			retry = True
			print('Article: ', blogEntity['title'])
			while retry:
				tags = getTags()
				print('Tags: ', tags)
				if input('Looks good?(y/n) ') == 'y':
					retry = False
			blogEntity['tags'] = tags	

def setSlugMenu():
	for blogEntity in blogList:
		if blogEntity['slug'] == '':
			retry = True
			print('Article: ', blogEntity['title'])
			while retry:
				slug = input('Input a new slug: ')
				if slug in slugList:
					print('This slug already exist! Pick another.')
				elif input('Looks good?(y/n) ') == 'y':
					retry = False
			blogEntity['slug'] = slug
			slugList.append(slug)

def loadJson():
	fname = input('Enter file name: (posts.json) ')
	if fname == '':
		fname = 'posts.json'
	fjson = open(fname)
	tjson = '[' + fjson.read()
	fjson.close()
	tjson = tjson.replace('}\n', '},\n')
	tjson = tjson[:-2] + ']'
	jlist = json.loads(tjson)
	for jsonEntity in jlist:
		title = jsonEntity['title']
		for blogEntity in blogList:
			if (blogEntity['title'] == title):
				print('Importing for blog entity ', title, '.')
				try:
					tags = jsonEntity['tags']
					blogEntity['tags'] = tags
					for tag in tags:
						if tag not in tagList:
							tagList.append(tag)
				except KeyError:
					print('No tags for this entity in JSON. ')
				try:
					category = jsonEntity['category']
					blogEntity['category'] = category
					if category not in catList:
						catList.append(category)
				except KeyError:
					print('No category for this entity in JSON. ')
				try:
					slug = jsonEntity['slug']
					blogEntity['slug'] = slug
					slugList.append(slug)
				except KeyError:
					print('No slug for this entity in JSON. ')		

def copyPhotoWrapper():
	copyPhoto(imageRoot)

def main():
	procDir(blogRoot)
	blogList.sort(key = date, reverse=True)
	for blogEntity in blogList:
		procEntity(blogEntity)
	print('Imported.')
	for blogEntity in blogList:
		render(blogEntity)
	print('Rendered.')

	options = { 1 : loadJson,
				2 : setCatMenu,
				3 : setTagMenu,
				4 : setSlugMenu,
				5 : copyPhotoWrapper,
				6 : writeDb }

	selection = 1
	while (selection != 0):
		print('Menu: ')
		print('1. Import Json')
		print('2. Change Category...')
		print('3. Change Tags...')
		print('4. Change Slug...')
		print('5. Copy Photo')
		print('6. Writed to DB')
		print('0. Exit')
		selection = int(input(''))
		if (selection != 0):
			options[selection]()

if __name__ == '__main__':
	main()
