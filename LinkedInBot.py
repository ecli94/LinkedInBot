#If you do not have the required packages installed,
#this script will not work properly.

#Author: Echo Li

import requests
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth2Session
import csv

#https://www.linkedin.com/search/results/people/?keywords=mindfulness&origin=GLOBAL_SEARCH_HEADER
#https://www.linkedin.com/search/results/people/?keywords=meditation&origin=GLOBAL_SEARCH_HEADER
#https://www.linkedin.com/search/results/groups/?keywords=meditation&origin=GLOBAL_SEARCH_HEADER

#For OAuth2 authentication
#client_id = 
#client_secret =
#redirect_uri = 

def authenticate(url):
	oauth = OAuth2Session(client_id, redirect_uri)
	authorization_url, state = oauth.authorization_url(
		'https://www.linkedin.com/oauth/v2/authorization')
	token = oauth.fetch_token(
		'https://www.linkedin.com/oauth/v2/accessToken',
		client_secret = client_secret)
	return oauth

def getInfo(url, stage):
	
	oauth = authenticate()
	response = oauth.get(url)
	soup = BeautifulSoup(response.textsoup, 'lxml')
	if response.headers['Content-Type'] =='text/html':
		if stage == 1:
			links = getLinks(soup)
			return links
		elif stage == 2:
			data = getProfile(response.text)
			return data
	else:
		return
		
def getLinks(soup):
	links = []
	baseURL = "https://www.linkedin.com"
	for link in soup.find_all('a'):
		if link.get('href').startswith('/in/'):
			links.append(baseURL + link)
	return links
	
def getProfile(soup):
	email = "N/A"
	for link in soup.find_all('a'):
		if link.get('href').startswith('mailto:') and not link.get('href').endswith('linkedin.com'):
			email = link.get('href')[7:]
	name = soup.find_all('h1', class_='pv-top-card-section__name')[0].contents[0]
	url = soup.find_all('a', class_='pv-contact-info__contact-item pv-contact-info__contact-link')[0].contents[0]
	title = soup.find('h2', class_='pv-top-card-section__headline')[0].contents[0]
	info = {"email": email, "name": name, "url": url, "title": title}
	return info
			
def crawler(url, type):
	pagesToCrawl = url
	pagesToVisit = []
	profileInfo = []
	pagesCrawled = []
	
	while pagesToCrawl != []:
		if pagesToCrawl[0] in pagesCrawled:
			pagesToCrawl = pagesToCrawl[1:]
		else:
			currURL = pagesToCrawl[0]
			pagesCrawled = pagesCrawled + currURL
			pagesToCrawl = pagesToCrawl[1:]
			try: 
				if type == "search":
					info = getInfo(currURL, 1)
					pagesToVisit = pagesToVisit + links
				elif type == "profile":
					info = getInfo(currURL, 2)
					profileInfo.append(info[email])			#email
					profileInfo.append(info[name])			#name
					profileInfo.append(info[url])			#URL
					profileInfo.append(info[title])			#title
			except:
				print("Page Not Found")
	
	if type == "search":
		return pagesToVisit
	elif type == "profile":
		return profileInfo
		
def main():
	relatedURL = []
	profileList = []
	criteria = [["people", "mindfulness"], ["people", "meditation"]]
	for item in criteria:
		# LinkedIn will not yield results for profiles further than page 100 for given search criteria
		for x in range(1, 101):
			payload = {"keywords": item[1], "page": x}
			r = requests.get("https://www.linkedin.com/search/results/" + item[0] + "/", params=payload)
			profileLinks = crawler([r.url], "search")
			relatedURL = relatedURL + profileLinks
	for profile in relatedURL:
		profileInfo = crawler(profile, "profile")
		profileList.append(profileInfo)
	writeToCSV(profileList)
	
##########################################################################################################		
##########################################################################################################		
		
def writeToCSV(data):
	output = open("LinkedIn_Profiles.csv", 'w', newline='')
	writer = csv.writer(output, delimiter=';', quotechar='"')
	writer.writerow(('E-mail Address', 'Profile Name', 'Profile URL', 'Title'))
	writer.writerows(data)
	output.close()
	
if __name__ == "__main__":
	main()