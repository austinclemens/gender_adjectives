from __future__ import division
import nltk
from nltk.corpus import names
from nltk.stem.lancaster import *
from textblob import TextBlob
from nltk import sent_tokenize, word_tokenize, chunk
from datetime import timedelta
import praw
import string
import enchant
import operator
import requests
import os
import twitter
import csv
import time
import datetime
import pickle

female_nouns=['matron','countess','baroness','dame','gal','mom','mama','crone','lady','ms.','mrs.','miss','missus','mistress','she','her','woman','mother','girl','aunt','wife','daughter','actress','princess','waitress','female','grandmother','sister','niece','queen','bitch','whore','cunt','slut','dyke','skank']
male_nouns=['gentleman','sir','mr.','mister','he','his','man','father','boy','uncle','husband','son','actor','prince','waiter','male','grandfather','brother','nephew','king','fag','faggot','fairy','gay']
female_names=names.words('female.txt')
male_names=names.words('male.txt')
exclude = set(string.punctuation)
dictionary=enchant.Dict("en_US")
stemmer=LancasterStemmer()

corpora={}
folder_loc='/Users/austinclemens/Desktop/gender_adjectives/'

##### DOWNLOAD TEXTS

def downloadgamergate():
	# tokenize
	r=praw.Reddit(user_agent='/austinclemens gendered-adjectives project')
	currentstart=datetime.date(2016,2,11)
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

		with open(folder_loc+"corpora/kotakuinaction2.csv",'a+') as cfile:
			cwriter=csv.writer(cfile)
			for line in day_comments:
				cwriter.writerow([line.encode('ascii','ignore')])

def downloadmovies():
	# tokenize
	r=praw.Reddit(user_agent='/austinclemens gendered-adjectives project')
	currentstart=datetime.date(2016,6,25)
	currentend=currentstart+timedelta(days=1)

	while int(currentend.strftime('%s'))<1475854178:
		day_comments=[]
		print currentstart
		a=praw.helpers.submissions_between(r,'movies',lowest_timestamp=int(currentstart.strftime('%s')),highest_timestamp=int(currentend.strftime('%s')))
		currentstart=currentstart+timedelta(days=1)
		currentend=currentstart+timedelta(days=1)

		for sub in a:
			sub.replace_more_comments(limit=None,threshold=0)
			all_comments=praw.helpers.flatten_tree(sub.comments)
			for comment in all_comments:
				day_comments.append(comment.body)

		with open(folder_loc+"corpora/movies.csv",'a+') as cfile:
			cwriter=csv.writer(cfile)
			for line in day_comments:
				cwriter.writerow([line.encode('ascii','ignore')])\

def downloadtelevision():
	# tokenize
	r=praw.Reddit(user_agent='/austinclemens gendered-adjectives project')
	currentstart=datetime.date(2016,4,1)
	currentend=currentstart+timedelta(days=1)

	while int(currentend.strftime('%s'))<1475854178:
		day_comments=[]
		print currentstart
		a=praw.helpers.submissions_between(r,'television',lowest_timestamp=int(currentstart.strftime('%s')),highest_timestamp=int(currentend.strftime('%s')))
		currentstart=currentstart+timedelta(days=1)
		currentend=currentstart+timedelta(days=1)

		for sub in a:
			sub.replace_more_comments(limit=None,threshold=0)
			all_comments=praw.helpers.flatten_tree(sub.comments)
			for comment in all_comments:
				day_comments.append(comment.body)

		with open(folder_loc+"corpora/television.csv",'a+') as cfile:
			cwriter=csv.writer(cfile)
			for line in day_comments:
				cwriter.writerow([line.encode('ascii','ignore')])

def downloadbooks():
	# tokenize
	r=praw.Reddit(user_agent='/austinclemens gendered-adjectives project')
	currentstart=datetime.date(2016,4,1)
	currentend=currentstart+timedelta(days=1)

	while int(currentend.strftime('%s'))<1475854178:
		day_comments=[]
		print currentstart
		a=praw.helpers.submissions_between(r,'books',lowest_timestamp=int(currentstart.strftime('%s')),highest_timestamp=int(currentend.strftime('%s')))
		currentstart=currentstart+timedelta(days=1)
		currentend=currentstart+timedelta(days=1)

		for sub in a:
			sub.replace_more_comments(limit=None,threshold=0)
			all_comments=praw.helpers.flatten_tree(sub.comments)
			for comment in all_comments:
				day_comments.append(comment.body)

		with open(folder_loc+"corpora/books.csv",'a+') as cfile:
			cwriter=csv.writer(cfile)
			for line in day_comments:
				cwriter.writerow([line.encode('ascii','ignore')])

def downloadtwitter():
	# tokenize
	credentials=open(folder_loc+'twitter_creds.txt','r').read().split('\n')
	api = twitter.Api(consumer_key=credentials[0],consumer_secret=credentials[1],access_token_key=credentials[2],access_token_secret=credentials[3])
	b=api.GetStreamSample(stall_warnings=True)

	with open(folder_loc+"corpora/tweets2.csv",'a+') as cfile:
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

##### LOAD TEXTS FOR ANALYSIS

def getoutlist(getfunction,tokenize=0):
	# pass this one of the getfunctions, it will spit out a complete method1 list
	corpus=getfunction()
	parsed=parse(corpus,tokenize)
	biglist=compare_genders(parsed)
	outlist=method1(biglist)
	return outlist

def gettwitter():
	#don't tokenize
	out=[]
	twit_list=os.listdir(folder_loc+'corpora/twitter/')
	for text in twit_list:
		if text[-3:]=='csv':
			text=open(folder_loc+"corpora/twitter/"+text,'r').read().decode('ascii','ignore')
			text=text.split('\n')
			text=[sent_tokenize(tweet) for tweet in text]
			text2=[]
			for tweet in text:
				for sent in tweet:
					text2.append(sent)
			final=[]
			for sent in text2:
				final.append(word_tokenize(sent))
			out.append(final)
	return out

def getggate():
	# don't tokenize
	out=[]
	ggate_list=os.listdir(folder_loc+'corpora/ggate/')
	for text in ggate_list:
		if text[-3:]=='csv':
			text=open(folder_loc+"corpora/ggate/"+text,'r').read().decode('ascii','ignore')
			text=text.split('\n')
			text=[line for line in text if len(line)>2 and line[0]!='>' and line[0:2]!='">']
			text=[sent_tokenize(post) for post in text]
			text2=[]
			for post in text:
				for sent in post:
					text2.append(sent)
			final=[]
			for sent in text2:
				final.append(word_tokenize(sent))
			out.append(final)
	return out	

def getmedia():
	# don't tokenize
	out=[]
	media_list=os.listdir(folder_loc+'corpora/media/')
	for text in media_list:
		if text[-3:]=='csv':
			text=open(folder_loc+"corpora/media/"+text,'r').read().decode('ascii','ignore')
			text=text.split('\n')
			text=[line for line in text if len(line)>2 and line[0]!='>' and line[0:2]!='">']
			text=[sent_tokenize(post) for post in text]
			text2=[]
			for post in text:
				for sent in post:
					text2.append(sent)
			final=[]
			for sent in text2:
				final.append(word_tokenize(sent))
			out.append(final)
	return out	

def getdickens():
	# don't tokenize
	from nltk.corpus import gutenberg
	dickens=[]
	dickens_list=os.listdir(folder_loc+"corpora/dickens/")
	for text in dickens_list:
		if text[-3:]=='txt':
			text=open(folder_loc+"corpora/dickens/"+text,'r').read().decode('ascii','ignore')
			text=sent_tokenize(text)
			final=[]
			for sent in text:
				final.append(word_tokenize(sent))
			dickens.append(final)
	return dickens

def getausten():
	# don't tokenize
	from nltk.corpus import gutenberg
	austen=[gutenberg.sents('austen-emma.txt'),gutenberg.sents('austen-persuasion.txt'),gutenberg.sents('austen-sense.txt')]
	austen_list=os.listdir(folder_loc+"corpora/austen/")
	for text in austen_list:
		if text[-3:]=='txt':
			text=open(folder_loc+"corpora/austen/"+text,'r').read().decode('ascii','ignore')
			text=sent_tokenize(text)
			final=[]
			for sent in text:
				final.append(word_tokenize(sent))
			austen.append(final)
	return austen

def getreuters():
	# don't tokenize
	from nltk.corpus import reuters
	reuterslist=[]
	for article in reuters.fileids():
		reuterslist.append(reuters.sents(article))
	return reuterslist

def getslate():
	# don't tokenize
	out=[]
	slate_list=os.listdir(folder_loc+'corpora/slate/')
	for text in slate_list:
		if text[-3:]=='txt':
			text=open(folder_loc+"corpora/slate/"+text,'r').read().decode('ascii','ignore')
			text=sent_tokenize(text)
			final=[]
			for sent in text:
				final.append(word_tokenize(sent))
			out.append(final)
	return out

def parse(corpora,tokenize=0):
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
				twit=[ch.replace('.','') for ch in twit if ch not in exclude]
				twit=[ch for ch in twit if ch!='']
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
		final_dict[unstemmed_opt]=[unstemmed_opt,adjective_dict[key][0],adjective_dict[key][1],adjective_dict[key][2],adjective_dict[key][3],adjective_dict[key][4][0]]

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
	# at one time this did the division to get female/male but now that's done in js.
	# It still appends a placeholder because I'm lazy and don't want to redo all the indexing in G1
	biglist=[]
	for key in adjective_dict:
		biglist.append(adjective_dict[key])

	# hm - should some sort of culling happen based on overall frequency?
	biglist.sort(key=lambda x:x[1])
	biglist.sort(key=lambda x:x[-1])
	for item in biglist:
		if item[3]==0:
			item.append('inf')
		if item[3]!=0:
			item.append(item[2]/item[3])

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

def method2(biglist):
	# another way to look at biglist. Leave in polarity=0, remove infrequent terms
	outlist=[]
	for term in biglist:
		if term[1]>2:
			outlist.append(term)

	for term in outlist:
		print term

	return outlist


# MISC

def wordlist():
	# get all words from the pickles, flatten them out and put them in a list
	picklelist=os.listdir(folder_loc+'parsed_pickles/')
	biglist=[]
	for pick in picklelist:
		if pick[-2:]=='.p':
			pick=pickle.load(open(folder_loc+"parsed_pickles/"+pick,'rb'))
			for word in pick.keys():
				biglist.append(pick[word])

	outlist=[]
	for word in biglist:
		if word[4]!=0 and word[1]>2 and word[0] not in outlist:
			outlist.append(word[0])

	return outlist

def dicts():
	# produce dictionaries for each pickle for use in G3
	picklelist=os.listdir(folder_loc+'parsed_pickles/')
	wordlist=[]

	for pick in picklelist:
		biglist={}
		if pick[-2:]=='.p':
			picka=pickle.load(open(folder_loc+"parsed_pickles/"+pick,'rb'))
			for word in picka.keys():
				if picka[word][1]>2 and picka[word][4]!=0:
					biglist[word]=[picka[word][2],picka[word][3],picka[word][4],picka[word][1]]
					if word not in wordlist:
						wordlist.append(word)

			print '==========================================='
			print pick
			print biglist
			
	print 'WORDS'
	print wordlist

def average_polarity(thresshold=1):
	# get average male and female polarities for each text
	# specify thresshold<1 to eliminate super high frequency words ('much', 'own', etc)
	picklelist=os.listdir(folder_loc+'parsed_pickles/')

	for pick in picklelist:
		if pick[-2:]=='.p':
			print pick
			male_polarity=0
			female_polarity=0
			male_density=0
			female_density=0
			picka=pickle.load(open(folder_loc+"parsed_pickles/"+pick,'rb'))
			freqs=[]

			for word in picka.keys():
				freqs.append(picka[word][1])

			freqs=sorted(freqs)

			for word in picka.keys():
				word=picka[word]
				if word[1]<freqs[int(len(freqs)*thresshold-1)]:
					male_density=male_density+word[3]
					female_density=female_density+word[2]
					male_polarity=male_polarity+word[3]*word[4]
					female_polarity=female_polarity+word[2]*word[4]

			print male_density,female_density
			print male_polarity,female_polarity
			print male_polarity/male_density,female_polarity/female_density

def average_polarity2(thresshold=1.2):
	# get average male and female polarities for each text
	# this one excludes words if they do not have a *strong* male/female bias
	picklelist=os.listdir(folder_loc+'parsed_pickles/')

	for pick in picklelist:
		if pick[-2:]=='.p':
			print pick
			male_polarity=0
			female_polarity=0
			male_density=0
			female_density=0
			picka=pickle.load(open(folder_loc+"parsed_pickles/"+pick,'rb'))
			freqs=[]

			for word in picka.keys():
				freqs.append(picka[word][1])

			freqs=sorted(freqs)

			for word in picka.keys():
				word=picka[word]
				if word[3]!=0:
					if word[2]/word[3]>thresshold or word[2]/word[3]<(1/thresshold):
						male_density=male_density+word[3]
						female_density=female_density+word[2]
						male_polarity=male_polarity+word[3]*word[4]
						female_polarity=female_polarity+word[2]*word[4]

			print male_density,female_density
			print male_polarity,female_polarity
			print male_polarity/male_density,female_polarity/female_density





