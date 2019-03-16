#!/usr/bin/python3
from selectolax.parser import HTMLParser
import urllib.request
import json
import sys
import os
import threading

lock = threading.Lock()
global vidsDict
vidsDict = {}

TMP_FILE_PATH = "/tmp/gitmanikytplayer.m4a"

class fetchInfoThread(threading.Thread):
	def __init__(self, ctr, url):
		threading.Thread.__init__(self)
		self.ctr = ctr
		self.url = url
	def run(self):
		global vidsDict
		info = self.getInfo(self.url)
		if info != None:
			lock.acquire()
			vidsDict[self.ctr] = info
			lock.release()

	def getInfo(self, url):
		noembedurl = "http://noembed.com/embed?url=" + url
		response = urllib.request.urlopen(noembedurl).read()
		info = json.loads(response.decode())
		try:
			return (url, info["title"], info["author_name"])
		except KeyError as ke:
			pass
			# print("KeyError in getInfo:", url)

def main():
	sys.stderr.write("\x1b[2J\x1b[H\n")
	resetLine()
	print("Welcome to GitmanikYTPlayer!")
	print("Made by Gitmanik 2019 (github.com/Gitmanik)\n")
	query = input("Enter video title: ")
	if query == "":
		main()

	vidsURLs = getURLs(query)

	threadList = []

	ctr = 1
	for href in vidsURLs:
		thread = fetchInfoThread(ctr, "https://www.youtube.com" + href)
		thread.start()
		threadList.append(thread)
		ctr += 1

	for t in threadList:
		t.join()

	printVids(vidsDict)
	playing = None

	while playing == None:
		try:
			playing = vidsDict[selectNumber()]
		except KeyError:
			playing = None

	print("Downloading", playing[1])
	clearTemp()
	os.system("youtube-dl -q -f 140 -o" + TMP_FILE_PATH + " " + playing[0])
	print("Playing", playing[1], "\nTo stop playing press Ctrl+C")
	os.system("ffplay -nodisp -autoexit " + TMP_FILE_PATH + " >/dev/null 2>&1")

	main()

def clearTemp():
	try:
		os.remove(TMP_FILE_PATH)
	except FileNotFoundError:
		pass

def resetLine():
	sys.stdout.write("\033[F") #Back to previous line
	sys.stdout.write("\033[K") #Clear line

def selectNumber():
	selected = input("Which? (Q/q) to return: ")
	try:
		if selected == "Q" or selected == "q":
			main()
		return int(selected)
	except ValueError:
		resetLine()
		selectNumber()


def printVids(vidsDict):
	for ctr, vid in sorted(vidsDict.items()):
		print(ctr, ":", vid[2], "-", vid[1])

def getURLs(query):
	query = urllib.parse.quote(query)
	url = "https://www.youtube.com/results?search_query=" + query
	response = urllib.request.urlopen(url)
	vids = []
	for candidate in HTMLParser(response.read()).css("a.yt-uix-tile-link"):
		if candidate.attributes['href'].startswith("/watch?v="):
			vids.append(candidate.attributes['href'])
	return vids

if __name__ == "__main__":
	main()