#!/usr/bin/python
import json
import urllib2
import getpass
import base64
import sys
import os
import subprocess

username = raw_input("Please enter your bitbucket username: ")
password = getpass.getpass("Please enter your bitbucket password: ")
project = raw_input("Please enter the bitbucket project key: ")

# curl -s  -k --user wpaul https://source.gci.com/rest/api/1.0/projects/SDIA/repos?limit=1000 > repos.json
print("Calling https://source.gci.com/rest/api/1.0/projects/" + project + "/repos?limit=1000")
request = urllib2.Request("https://source.gci.com/rest/api/1.0/projects/" + project + "/repos?limit=1000")
base64string = base64.b64encode('%s:%s' % (username, password))
request.add_header("Authorization", "Basic %s" % base64string)   
response = urllib2.urlopen(request).read()

# with open('repos.json') as fp:
#   response = fp.read()

data = json.loads(response)

if data.get("isLastPage") == False:
	sys.exit("Too many repositories returned (>1000).  Script aborted!")

dirlist = [ item for item in os.listdir(".") if os.path.isdir(os.path.join(".", item)) ]

for repo in data.get("values"):
	if repo.get("slug") in dirlist:
		print(repo.get("slug") + " already exists.  Pulling latest.")
		os.chdir(repo.get("slug"))
		output = subprocess.check_output(["git", "pull"])
		os.chdir("..")
	else:
		print(repo.get("slug") + " does not exist.  Cloning.")
		cloneLinks = repo.get("links").get("clone")
		httpCloneLink = next((x for x in cloneLinks if x.get("name") == "http"), None)
		httpCloneUrl = httpCloneLink.get("href")
		output = subprocess.check_output(["git", "clone", httpCloneUrl])

