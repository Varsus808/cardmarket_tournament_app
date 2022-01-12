import requests
import re
import time
import os
import numpy

def get_version_urls_for_all_cards(cardlist):
	
	urls_of_all_cards = []
	for elem in cardlist:
		search_url = ""
		search_url += "https://www.cardmarket.com/de/Magic/Products/Singles?idExpansion=0&searchString=%5B"
		#check elem syntax
		search_url += elem
		search_url += "%5D&exactMatch=on&idRarity=0&sortBy=price_asc&perSite=100" #<-- define these as param maybe?
		#exactMatch=on <-- only the exact name
		#idRarity=0 dunno
		#sortBy=price_asc <-- sort by cheapest first
		#perSite=100 <-- show up to 100 versions

		r = requests.get(search_url)
		matches = re.finditer("<div class=\"row no-gutters\">", r.text) #find start of all versions section
		matches_editions_positions = [match.start() for match in matches]

		keystring = "<a href=\"" #find the partial version url
		keystring_len = len(keystring)
		card_edition_specific_url = []
		for i in range(len(matches_editions_positions)):
			if i > len(matches_editions_positions): #if to make an exception for the last iteration
				substr = r.text[matches_editions_positions[i]:matches_editions_positions[i+1]]
			else:
				substr = r.text[matches_editions_positions[i]:]
			a = substr.find(keystring) #length 9
			b = substr.find('\">', a)
			card_edition_specific_url.append("https://www.cardmarket.com" + substr[a+keystring_len:b] + "?sellerCountry=7&language=1,3") 
			#last part is for seller_location DE and languages eng and ger
			#sellerCountry=7 <-- Germany
			#language=1,3 <-- englisch, german
			print(card_edition_specific_url[i])	
		urls_of_all_cards.append(card_edition_specific_url)
	return urls_of_all_cards

def parse_cardlist(file):
	#format cardlist into url encoded version
	#assumption that the encoding has to be done by hand and not by built in url-encode function
	#possible optimisation

	cardlist = []
	ammount_of_cards = []
	for line in file:
		
		temp_lst = line.split(' ')

		if temp_lst == []:
			continue
		elif temp_lst[0].isdecimal() == False:
			continue

		ammount_of_cards.append(int(temp_lst[0]))
		temp = ""
		if line[-1] == '\n':
			line = line [:-1]
		
		for char in line:
			if char == ' ':
				temp += '+'
			elif char == '\'':
				temp += '-'
			elif char == '/':
				temp += "%2F"
			else:
				temp += char
		cardlist.append(temp[len(temp_lst[0])+1:])
	return cardlist, ammount_of_cards


def pop_specific_elements(lst, keyword):
	temp = list(lst) #deatch for memory shenannigans
						#if we were to use lst we would modifiy the original instance aswell
	while keyword in temp:
		temp.remove(keyword)
	return temp


def find_lowest_price(lst_seller):
	
	lst_tmp = pop_specific_elements(lst_seller, -1)
	if lst_tmp == []:
		return "Card not found", 0
	else:
		minimum = min(lst_tmp)
		index = lst_seller.index(minimum)
		return minimum, index


def find_lowest_seller(text):
	keyword = "<div class=\"d-flex align-items-center justify-content-end\"><span class=\"font-weight-bold color-primary small text-right text-nowrap\">"
	price_start = text.find(keyword)
	if price_start == -1:
		return -1
	price_end = text.find("</span></div>", price_start)
	keyword_len = len(keyword)
	lowest_price = ""
	for elem in text[price_start+keyword_len:price_end-2]:
		if elem == ',':
			lowest_price += '.'
		elif elem == '.':
			continue
		else:
			lowest_price += elem
	
	return float(lowest_price)

def get_prices(filename, in_path, out_path):

	file_r = open(in_path + str(filename), "r")
	file_w = open(out_path + "checked_"+str(filename), "w+")
	
	cardlist, ammount_of_cards = parse_cardlist(file_r)
	print(cardlist)
	file_r.close()

	urls_of_all_cards = get_version_urls_for_all_cards(cardlist)

	print("got all the urls")
	print("cards in your list:", len(urls_of_all_cards))

	total_price = 0
	num_of_unfound_cards = 0
	too_expensive_cards = 0
	unfound_cards = []
	for i in range(len(urls_of_all_cards)):
		print("we are at", i+1, "from", len(urls_of_all_cards))
		ppv_lst = []
		for j in range(len(urls_of_all_cards[i])):

			version_part = urls_of_all_cards[i][j][len("https://www.cardmarket.com/de/Magic/Products/Singles"):]
			if 'WCD' not in version_part and 'Pro-Tour'not in version_part:
				#cuts all goldbordered cards
				r = requests.get(urls_of_all_cards[i][j])
				ppv_lst.append(find_lowest_seller(r.text))
				print("ppv:", ppv_lst)
				if ppv_lst[j] == 0.02: #lowest threshold for card prices
					break
				
			else:
				ppv_lst.append(-1) 

				#all instances of -1, whether through goldborder detection or card not found will not be accounted when calculation min
				
				print("goldbordered version of card not taken into account:" + urls_of_all_cards[i][j])
				

		lowest_price, index_of_low = find_lowest_price(ppv_lst)
		if lowest_price != "Card not found":
			total_price += float(lowest_price) * ammount_of_cards[i]
			if lowest_price > 6:
				too_expensive_cards += 1
		else:
			num_of_unfound_cards += 1
			print(num_of_unfound_cards)
			unfound_cards.append(cardlist[i])


		
		if urls_of_all_cards[i] == []:
			url_to_print = "No version found on cardmarket"
		else:
			url_to_print = str(urls_of_all_cards[i][index_of_low])
		print(str(lowest_price) +' '+ str(cardlist[i]) +' '+ str(ammount_of_cards[i])+' times '+ url_to_print)
		file_w.write(str(lowest_price) +' '+ str(cardlist[i]) +' '+ str(ammount_of_cards[i])+' times '+ url_to_print +'\n')
		time.sleep(5)


	#formating shennanigans

	if total_price != 0:
		print("Your Deck costs:" +' '+ str(total_price) + '\n')
		string = '\n'
		if num_of_unfound_cards > 0:
			string += 'Your Deck costs at least:' + ' ' + str(total_price) + '\n\n'
			string += 'From your decklist' + str(num_of_unfound_cards) + 'were not found.' + '\n'\
							'Please check all entries in your decklist for typos' + '\n'\
							'Your deck costs MORE than what was calculated. The Cards not found are marked in the output File,' + '\n'\
							'Look the prices of following cards up by hand:' + '\n\n'
			for elem in unfound_cards:
				string += '        -"' + elem + '"\n'

		else:		
			string += 'Your Deck costs:' +' '+ str(total_price) + '\n\n'
			string += 'All entries were found' + '\n'
		if too_expensive_cards > 0:
			string += str(too_expensive_cards) + 'card(s) exceed the limit of 6 Euros' + '\n'
		file_w.write(string)
	else:
		print("None of the cards in your decklist were found!")
	file_w.close()


def readlastline(f):
	for line in f:
	    pass
	return line


if __name__ == '__main__':

	path = os.path.abspath(__file__)[:-len(__file__)]
	
	if os.name == 'nt':
		in_path = path + "in\\"
		out_path = path + "out\\"
	elif os.name == 'posix':
		in_path = path + "in/"
		out_path = path + "out/"

	onlyfiles = [f for f in os.listdir(in_path) if os.path.isfile(os.path.join(in_path, f))]
	for decklist in onlyfiles:
		get_prices(decklist, in_path, out_path)