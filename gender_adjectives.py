from __future__ import division
import nltk
from nltk.corpus import names
from nltk.corpus import twitter_samples
from nltk.corpus import gutenberg
from nltk.stem.lancaster import *
from textblob import TextBlob
from nltk import sent_tokenize, word_tokenize, chunk
from datetime import timedelta
import string
import enchant
import operator
import requests
import os
import twitter
import csv
import time
import datetime

female_nouns=['matron','countess','baroness','dame','gal','mom','mama','crone','lady','ms.','mrs.','miss','missus','mistress','she','her','woman','mother','girl','aunt','wife','daughter','actress','princess','waitress','female','grandmother','sister','niece','queen','bitch','whore','cunt','slut','dyke','skank']
male_nouns=['gentleman','sir','mr.','mister','he','his','man','father','boy','uncle','husband','son','actor','prince','waiter','male','grandfather','brother','nephew','king','fag','faggot','fairy','gay']
female_names=names.words('female.txt')
male_names=names.words('male.txt')
exclude = set(string.punctuation)
dictionary=enchant.Dict("en_US")
stemmer=LancasterStemmer()

corpora={}
folder_loc='/Users/austinclemens/Desktop/gender_adjectives/'

def getgamergate():
	r=praw.Reddit(user_agent='/austinclemens gendered-adjectives project')
	currentstart=datetime.date(2015,5,11)
	currentend=currentstart+timedelta(days=1)

	while int(currentend.strftime('%s'))<1475854178:
		day_comments=[]
		print currentstart
		a=praw.helpers.submissions_between(r,'KotakuInAction',lowest_timestamp=int(currentstart.strftime('%s')),highest_timestamp=int(currentend.strftime('%s')))
		currentstart=currentstart+timedelta(days=1)
		currentend=currentstart+timedelta(days=1)

		for sub in a:
			sub.replace_more_comments(limit=None,threshold=0)
			all_comments=praw.helpers.flatten_tree(sub.comments)
			for comment in all_comments:
				day_comments.append(comment.body)

		with open(folder_loc+"kotakuinaction.csv",'a+') as cfile:
			cwriter=csv.writer(cfile)
			for line in day_comments:
				cwriter.writerow([line.encode('ascii','ignore')])

def gettwitter():
	credentials=open(folder_loc+'twitter_creds.txt','r').read().split('\n')
	api = twitter.Api(consumer_key=credentials[0],consumer_secret=credentials[1],access_token_key=credentials[2],access_token_secret=credentials[3])
	b=api.GetStreamSample(stall_warnings=True)

	with open(folder_loc+"tweets2.csv",'a+') as cfile:
		cwriter=csv.writer(cfile)
		i=1
		for line in b:
			tweet=twitter.Status.NewFromJsonDict(line)
			if tweet.lang=='en':
				try:
					cwriter.writerow([tweet.text.encode('ascii','ignore')])
					print i
					i=i+1
				except:
					print "ERROR: ",tweet.text

def getdickens():
	dickens=[]
	dickens_list=os.listdir(folder_loc+"dickens/")
	for text in dickens_list:
		if text[-3:]=='txt':
			text=open(folder_loc+"dickens/"+text,'r').read().decode('ascii','ignore')
			text=sent_tokenize(text)
			final=[]
			for sent in text:
				final.append(word_tokenize(sent))
			dickens.append(final)
	return dickens

def getausten():
	austen=[gutenberg.sents('austen-emma.txt'),gutenberg.sents('austen-persuasion.txt'),gutenberg.sents('austen-sense.txt')]
	austen_list=os.listdir(folder_loc+"austen/")
	for text in austen_list:
		if text[-3:]=='txt':
			text=open(folder_loc+"austen/"+text,'r').read().decode('ascii','ignore')
			text=sent_tokenize(text)
			final=[]
			for sent in text:
				final.append(word_tokenize(sent))
			austen.append(final)

	return austen

def getslate():

def get_gutenberg(textnumber):
	r = requests.get('http://www.gutenberg.org/files/'+textnumber+'/'+textnumber+'.txt')
	raw=r.text
	return raw

def parse(corpora,tokenize=1):
	# for any corpora where you're starting with sentences
	total_females=0
	total_males=0
	corp_words=0
	adjective_dict={}

	for corpus in corpora:
		for twit in corpus:
			# tokenize and tag
			if tokenize==1:
				twit=''.join(ch for ch in twit if ch not in exclude)
				tags=nltk.pos_tag(nltk.word_tokenize(twit))
			else:
				twit=[ch for ch in twit if ch not in exclude]
				tags=nltk.pos_tag(twit)

			# set up lists for nouns and adjectives found in sentence
			nouns=[]
			adjectives=[]

			# do a stupid thing here to eliminate last names (hopefully, usually, maybe)
			for i,word in enumerate(tags):
				corp_words=corp_words+1

				if word[1]=="PRP" or word[1]=="PRP$" or word[1]=="NN":
					nouns.append(word)

				if word[1]=="NNS":
					if len(TextBlob(word[0]).words)>0:
						word=(TextBlob(word[0]).words.singularize()[0],word[1])
						nouns.append(word)

				if word[1]=="NNP":
					try:
						if tags[i+1][1]=="NNP":
							tags[i+1]=(tags[i+1][0],"-")
						nouns.append(word)
					except:
						nouns.append(word)

				if word[1]=="JJ" or word[1]=="JJR" or word[1]=="JJS":
					adjectives.append(word)

			# determine whether males or females are in nouns
			female=0
			male=0
			for noun in nouns:
				if noun[0].lower() in female_nouns:
					female=1
				if noun[0].lower() in male_nouns:
					male=1
				if word[1]=="NNP" and word[0] in female_names:
					female=1
				if word[1]=="NNP" and word[0] in male_names:
					male=1

			# Screen out co-occurrences of males and females. These are often erroneous.
			if female+male==1:

				total_females=total_females+female
				total_males=total_males+male
				# now you have the noun and adjective lists, add to dictionary
				# each adjective entry in dict should be: total,females,males,polarity,list of non-stemmed versions
				for adj in adjectives:
					if dictionary.check(adj[0].lower())==True and len(adj[0])>2:
						if stemmer.stem(adj[0].lower()) in adjective_dict.keys():
							temp=adjective_dict[stemmer.stem(adj[0].lower())]
							unstemmed=temp[4]
							if adj[0].lower() in unstemmed[0]:
								unstemmed[1][unstemmed[0].index(adj[0].lower())]=unstemmed[1][unstemmed[0].index(adj[0].lower())]+1
							else:
								unstemmed[0].append(adj[0].lower())
								unstemmed[1].append(1)
							adjective_dict[stemmer.stem(adj[0].lower())]=[temp[0]+1,temp[1]+female,temp[2]+male,TextBlob(adj[0]).sentiment[0],unstemmed]
						else:
							adjective_dict[stemmer.stem(adj[0].lower())]=[1,female,male,TextBlob(adj[0]).sentiment[0],[[adj[0].lower()],[1]]]

	final_dict={}

	for key in adjective_dict.keys():
		# convert from number of male/female mentions to % of male/female mentions that are associated with adj
		adjective_dict[key][1]=100*adjective_dict[key][1]/total_females
		adjective_dict[key][2]=100*adjective_dict[key][2]/total_males

		# replace stemmed adjective with most popular unstemmed option
		unstemmed_opt=adjective_dict[key][4][0][adjective_dict[key][4][1].index(max(adjective_dict[key][4][1]))]
		final_dict[unstemmed_opt]=[unstemmed_opt,adjective_dict[key][0],adjective_dict[key][1],adjective_dict[key][2],adjective_dict[key][3]]

	print "FEMALES FOUND: ",total_females
	print "MALES FOUND: ",total_males
	print "WORDS IN CORPUS: ",corp_words
	return final_dict

def sort_adjectives(adjective_dict,female=1):
	if female==0:
		female=2

	biglist=[]
	for key in adjective_dict.keys():
		if adjective_dict[key][female]>0:
			biglist.append([key,adjective_dict[key][female]])

	biglist.sort(key=lambda x:x[1])
	biglist.reverse()
	for row in biglist:
		print row

def compare_genders(adjective_dict):
	biglist=[]
	for key in adjective_dict:
		biglist.append(adjective_dict[key])

	# hm - should some sort of culling happen based on overall frequency?
	biglist.sort(key=lambda x:x[1])

	for item in biglist:
		try:
			item.append(item[2]/item[3])
		except:
			item.append(float('inf'))

	biglist.sort(key=lambda x:x[-1])
	return biglist

def method1(biglist):
	# one possible way of looking at the biglist - remove polarity=0, remove extremely infrequent terms, rank the rest
	outlist=[]
	for term in biglist:
		if term[4]!=0 and term[1]>2:
			outlist.append(term)

	for term in outlist:
		print term

	return outlist







