#!/usr/bin/env python

import argparse
import sys
import re
import urllib
import lxml.html
import os
import time
import Queue
import threading

def _main():
	argParser = argparse.ArgumentParser(description="Scan any wordpress powered website and identify plugins installed. Originally taken from https://github.com/an1zhegorodov/WP-plugin-scanner, modified by wget.")
	argParser.add_argument('-s', '--scan', metavar='<website url>', dest='url', help='scan website at <website url>')
	argParser.add_argument('-u', '--update', type=int, metavar='<page number>', dest='pageN', help='update the list of plugins from wordpress.org up to <page number>')
	argParser.add_argument('-p', '--pause', type=int, metavar='<seconds>', dest='pause', help='sleep (in seconds) between each request, default: 0')
	argParser.add_argument('-t', '--threads', type=int, metavar='<thread count>', dest='threads', help='scanning threads, default: 1')
	argParser.add_argument('-l', '--list', metavar='<plugin list path>', dest='list', help='path to wp plugin list separated by newline, default: plugin.txt')
	args = argParser.parse_args()
	try:
		if args.pause == None:
			args.pause = 0
		if args.list == None:
			currentDir = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
			args.list = currentDir + 'plugins.txt'
		if args.threads == None:
			args.threads = 1
		if args.url == args.pageN == None:
			argParser.print_help()
		elif args.url != None:
			scan(args.url, args.pause, args.threads, args.list)
		else:
			update(args.pageN)
	except IOError as e:
		print e

def _isUrl(url):
	pattern = re.compile('^https?://[\w\d\-\.]+/(([\w\d\-]+/)+)?$')
	if pattern.match(url):
		return True
	else:
		return False

def _isWebsiteAlive(url):
	if urllib.urlopen(url).getcode() == 200:
		return True
	else:
		return False

def _parseHrefs(html):
	doc = lxml.html.document_fromstring(html)
	pattern = re.compile('/plugins/([\w\d\-]+)/')
	pluginsList = []
	links = doc.cssselect('div.plugin-block h3 a')
	for link in links:
		plugin = pattern.search(link.get('href')).group(1)
		pluginsList.append(plugin)
		print plugin + '[+]'
	return pluginsList

def _writePlugins(pluginsList):
	currentDir = os.path.dirname(os.path.realpath(__file__)) + os.path.sep
	pluginsFile = open(currentDir + 'plugins.txt', 'w')
	pluginsFile.write('\n'.join(pluginsList))
	pluginsFile.close()

def _thread(id,q,url,delay):
	while not q.empty():
		plugin = q.get()
		code = urllib.urlopen(url + 'wp-content/plugins/' + plugin + '/').getcode()
		if code != 404:
			print plugin + '[+]'
		if delay > 0:
			time.sleep(delay)
		q.task_done()

def scan(url, delay, threads, list):
	if _isUrl(url) != True:
		print 'The url you entered should match this pattern ^https?://[\w\d\-\.]+/(([\w\d\-]+/)+)?$'
		return
	elif _isWebsiteAlive(url) != True:
		return
	pluginsFile = open(list, 'r')
	q = Queue.Queue()
	for line in pluginsFile.read().split('\n'):
		if line:
			q.put(line)
	print "Spawning "+str(threads)+" threads..."
	tlist = []
	for i in range(1,threads+1):
		t = threading.Thread(target=_thread, args=(i,q, url, delay))
		t.setDaemon(True)
		t.start()
	try:
		while True:
			time.sleep(0.1)
	except KeyboardInterrupt:
		print "Ctrl+C got, exiting"
		sys.exit(1)

def update(pageN):
	pluginsList = []
	if pageN == 1:
		html = urllib.urlopen('http://wordpress.org/extend/plugins/browse/popular/').read()
		pluginsList = _parseHrefs(html)
	elif pageN == 2:
		html = urllib.urlopen('http://wordpress.org/extend/plugins/browse/popular/').read()
		pluginsList = _parseHrefs(html)
		html = urllib.urlopen('http://wordpress.org/extend/plugins/browse/popular/page/2/').read()
		pluginsList = pluginsList + _parseHrefs(html)
	else:
		html = urllib.urlopen('http://wordpress.org/extend/plugins/browse/popular/').read()
		pluginsList = _parseHrefs(html)
		for page in range(2, pageN+1):
			html = urllib.urlopen('http://wordpress.org/extend/plugins/browse/popular/page/' + str(page) + '/').read()
			pluginsList = pluginsList + _parseHrefs(html)
			print "Page "+str(page)+" parsed."
			time.sleep(8) # Wordpress.org bans you if you'll set lower delay as of 10.11.2013
			
	_writePlugins(pluginsList)

if __name__ == "__main__":
	_main()