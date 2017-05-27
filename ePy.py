'''
Created on May 15, 2017

@author: Blu3spirits & JuggernautAlpha
@version: 3.9
'''

import requests, re, csv, sys, configparser, logging, smtplib, time
from bs4 import BeautifulSoup
from pathlib import Path
from smtplib import SMTPException

class eLib(object):
    '''
    initialize all variables including a dictionary and array and an int
    '''
    def __init__(self):
        self.url = self.result = self.object = self.string = self.title = self.price = self.link = ""
        self.user_terms = {}
        self.banned_array = []
        self.j = 0
        self.sender = "regimebot@gmail.com"
        self.recievers = [''] #TODO: Add recipients
        self.message_base = ""
        self.day_array = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', 'TODAY', 'TOMORROW', 'HOURS', 'MINUTES', 'SECONDS']
    '''
    this function takes a string and makes it into a float, because prices
    '''
    def toFloat(self, string):
        try:
            price = float(string)
            return price
        except:
            pass
    '''
    this function writes whatever is passed into it to a .csv file.
    it currently writes the title, price, and link to a desired item
    '''
    def writeToLog(self, title, ctime, price, link):
        with open('log.csv', 'a+', newline='') as cfile:
            writer = csv.writer(cfile, quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow((re.sub(',', '', title), ctime, price, link))
    '''this function is a cluster fuck. Okay? Just accept that.
    SO to get started. We get link title and price by doing a regex onto a condensed for loop
    On price we are only concerned with 1-7 lengths
    
    then we do a fuck ton of if statements that kind of reminds me of an algorithm (hint hint)
        inside this algorithm, we have a log writing method being called so we actually write down our desired data
    '''
    def applyParams(self):
        p = re.compile(r'\s+')
        link = re.sub(p, '', ''.join([links.get('href') for links in self.result.select('a.vip')]))
        title = re.sub(p, '', ''.join([e.get_text() for e in self.result.select('a.vip')]))
        price = re.sub(p, '', ''.join([e.get_text() for e in self.result.select('span.bold')]))
        calculated_time = 0
        
        for i in self.day_array:
            if self.result.select('span.%s.timeMs' %i) == []:
                pass
            else:
                test = (self.result.select('span.%s.timeMs'%i)[0])
                collect_time = int((re.search(r'(\d+)', str(test)).group()))
                time_now = int(time.time() * 1000)
                calculated_time = (collect_time - time_now) /1000/60/60
                if calculated_time > 24:
                    calculated_time = calculated_time / 24
                else:
                    pass
                
        price = price[1:7]
        # TODO: Effieciency (Free time when you're stuck on something)
            # No longer chain functions together. Run everything from the main.
        if "newlisting" in title.lower():
            pattern = re.compile('(\s*)Newlisting(\s*)')
            title = re.sub(pattern, '', title)
        if (any(key in title.lower() for key in self.banned_array) or self.user_terms["search_term"] not in title):
            pass
        elif "Trendingat" in price:
            pattern = re.compile('(\s*)Trendingat(\s*)')
            price = self.object.toFloat((re.sub(pattern, '\\n\1Average\2', price)))
            if price == None:
                pass
            else:
                if price < self.user_terms['max_price']:
                    #print("Time: %s\nTitle: %s\nPrice: %s\nLink: %s\n" %(calculated_time, title, price, link))
                    self.object.writeToLog(title, calculated_time, (re.sub(pattern, '\\n\1Average\2', price)), link)
                else:
                    self.object.j += 1
        else:
            price = self.object.toFloat(price)
            if price == None:
                pass
            else:
                if price < self.user_terms['max_price']:
                    #print("Time: %s\nTitle: %s\nPrice: %s\nLink: %s\n" %(calculated_time, title, price, link))
                    self.object.writeToLog(title, calculated_time, price, link)
                else:
                    self.object.j += 1
        return self.object.j
    '''
    this function gets the page through requests, then soups it. After that we create a generator object
    containing all listings on the page
    from there we append those listings to an array using a condensed for loop.
    We get ahold of our banned keys
    then for every listing we apply our parameters. Remember the cluster fuck?
    that cluster fuck also returns an int for every time that it parses a page that has a price over what is defined
    when that int is over 15 it kills the entire program (this may be changed later)
    '''
    def getPage(self):
        page = requests.get(self.url).text
        soup = BeautifulSoup(page, "html.parser")
        idNum = []
        var = (e.get('id') for e in soup.find_all('li'))
        [idNum.append(x) for x in var if isinstance(x, str) and "item" in x]
        self.object.bannedArray = self.object.getBannedKeys()
        for i in range(len(idNum)):
            self.object.result = soup.find('li', attrs={"id":idNum[i]})
            self.object.j = self.object.applyParams()
            if self.object.j > 15:
                self.object.notifyUser()
                exit()
    '''
    this function grabs ahold of our banned keywords from a file and returns an array of them
    '''
    def getBannedKeys(self):
        bannedArray = []
        with open('banned_keywords.file', 'r') as f:
            [bannedArray.append((x.strip('\n'))) for x in f]
        return bannedArray
    '''
    this function gets the desired links from a file. Make sure you sort by price!
    '''
    def getItems(self):
        items = []
        with open('itemlist.file', 'r') as f:
            [items.append(x.lower()) for x in f]
        return items
    
    def notifyUser(self):
        try:
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.starttls()
            smtpObj.login(self.sender, "@TODO:Password")
            self.object.message_base = """From: ePy.py <regimebot@gmail.com>
To: %s
Subject: Update Message

This is a test message""" %(self.recievers)
            #smtpObj.sendmail(self.sender, self.user_email, self.message_base)
            smtpObj.quit()
            print("Message Sent!")
        except SMTPException:
            print("Unable to send message")

'''
this class is entirely dedicated to the user lists, it was mostly written because I was fucking around with this stuff
and it was interesting
'''
class eList(object):
    filename = url = soup = ""
    def getFile(self):
        userList = []
        with open(self.filename, 'r+') as f:
            [userList.append(x) for x in f]
        return userList
    
    def getTime(self):
        pattern = re.compile(r'\s+')
        timeGen = (e.get_text() for e in self.soup.find_all(attrs={'id':'vi-cdown_timeLeft'}))
        test = [re.sub(pattern, '', x) for x in timeGen]
        return test[0]
    
    def getPage(self):
        page = requests.get(self.url).text
        soup = BeautifulSoup(page, "html.parser")
        return soup
    
    def getTitle(self):
        '''
        these generators are really the only confusing thing. Basically it's an object.
        '''
        titleGen = (e.get_text() for e in self.soup.select('h1'))
        test = [x[16:] for x in titleGen]
        return test[0]
        
    def getBid(self):
        priceGen = (e.get_text() for e in self.soup.find_all(attrs={'id':'prcIsum'}))
        test = [x for x in priceGen]
        if test == []:
            priceGen = (e.get_text() for e in self.soup.find_all(attrs={'id':'prcIsum_bidPrice'}))
            test = [x for x in priceGen]
            if test == []:
                testGen = (e.get_text() for e in self.soup.select('span.statusLeftContent'))
                test = [x.strip('\n') for x in testGen if "ended" in x]
                if test[0] == "Bidding has ended on this item. ":
                    return "end"
            else:
                return test[0]
        else:
            return test[0]

'''
this is the help command!
'''
def help_command():
    commands = '''Available commands:
    -l <filename> or --list <filename>
        This starts a subroutine that with the user specified list parses through the list and returns the title and price of their watchlist
    -h or --help
        This prints this dialogue
                '''
    print(commands)
    exit()
'''
this is the userlist_command. or -l || --list
''' 
def userlist_command(elib, elist, logger):
    elist.filename = sys.argv[2]
    if Path(elist.filename).is_file():
        pass
    else:
        logger.log(40, "User specified list not found, file created. Check current directory. You may have to refresh.")
        open('mylist.txt', 'a+').close()
        exit()
    list = elist.getFile()
    if list == []:
        logger.error("Fatal: Please populate your personal list")
        exit()
    else:
        logger.log(30, "Starting list parsing. Depending on the list this could take a bit")
        temp = []
        for y in list:
            elist.url = y
            elist.soup = elist.getPage()
            title = elist.getTitle()
            price = elist.getBid()
            if price == "end" or price == None:
                logger.log(40, "There is an error in your list. One of the items no longer exists. It will be removed")
                price = "$$$$1000000"
            else:
                time = elist.getTime()
            if (float(price[4:]) < elib.user_terms['max_price']):
                temp.append(y)
                print("Title: %s\nCurrentBid: %s\nTimeLeft: %s" %(title, price, time))
                print(y)
        with open('mylist.txt', 'w') as file:
            for y in temp:
                file.write(y)
    exit()
'''
main function
if I have to describe what a main function is, you need to go to codeacademy.com or something...
'''
def main():
    #initialize our class objects
    elist = eList()
    elib = eLib()
    '''
    this is fucky. 
    We are making a variable in our class, to access our functions inside the class. 
    Are you confused yet?
    '''
    elib.object = elib
    '''
    setting up other basic objects and such and getting variables and setting them
    '''
    elib.banned_array = elib.getBannedKeys()
    logger = logging.getLogger()
    itemlist = elib.getItems()
    if Path('config.ini').is_file():
        pass
    else:
        logger.log(40, "config.ini not found!")
    config = configparser.ConfigParser()
    config.read('config.ini')
    elib.user_terms = {
            'search_term':config['SETTINGS']['search_term'],
            'max_price':float(config['SETTINGS']['max_price'])
              }
    elib.user_email = config['SETTINGS']['email']
    i = 2
    j = 50
    try:
        if sys.argv[1] != None:
            if sys.argv[1] == '-l' or sys.argv[1] == '--list':
                userlist_command(elib, elist, logger)   
            elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
                help_command()
    except IndexError:
        logger.log(30, "No commands found, moving to default configurations and running")
        pass
    '''
    this is the main meat of the program.
    it first truncates anything in log.csv. Because duplicates are fucking annoying
    For every url in our itemlist
    get the page, remake the url, apply parameters, you get the point
    Oh and ebay increments pages and something called _skc=x.
    We are setting that with i and j respectively.
    '''
    if Path('log.csv').is_file():
        open('log.csv', 'w').close()
    for url in itemlist:
        elib.url = url
        elib.getPage()
        baseurl = url
        newterm = re.sub(' ','+',elib.user_terms['search_term'])
        newrep = re.sub(' ','\+',elib.user_terms['search_term'])
        while(True):
            if "ipg=" in url:
                pattern = re.compile(r'(\s*)' + newrep + r'&_ipg=50(\s*)')
            elif "ipg" not in url:
                pattern = re.compile(r'(\s*)' + newrep + r'&(\s*)')
            elib.url = re.sub(pattern, newterm +('&_pgn=%d&_skc=%d' % (i, j)), baseurl)
            elib.getPage()
            i += 1
            j += 50
if __name__ == '__main__':
    main()
