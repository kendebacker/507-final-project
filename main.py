from bs4 import BeautifulSoup
import requests
import json

BASE_URL = 'https://en.wikipedia.org'
NETWORK_LIMIT = 3

def getLinksFromPage(page):
    try:
        res = requests.get(f"{BASE_URL}{page['url']}")
        obj = BeautifulSoup(res.text, "html.parser")
        main_article = obj.find("div", class_="mw-content-ltr mw-parser-output")
        # https://stackoverflow.com/questions/47724241/beautifulsoup-find-all-tags-before-stopping-condition-is-met
        articleReferences = main_article.find("span", class_="mw-headline", id='References')
        articleParagraphs = articleReferences.find_all_previous("p", recursive = False)
        links = []
        for para in articleParagraphs:
            link_list = para.find_all("a")
            for link in link_list:
                # https://stackoverflow.com/questions/11716380/beautifulsoup-extract-text-from-anchor-tag
                if link["href"][0:5] == "/wiki":
                    links.append((link["href"].split("/")[-1].replace("_"," "), link["href"], page["url"]))
        return links
    except:
        return []

def createNetwork():
    try:
        network  = fetchCache("wikiNetwork.json")
        count = NETWORK_LIMIT
        stack = []
    except:
        network = {}
        count = 0
        startPage = {"name":"University of Michigan", "url":"/wiki/University_of_Michigan", "links":{}}
        stack = getLinksFromPage(startPage)
        network[startPage["url"]] = startPage
    while count < NETWORK_LIMIT and len(stack) > 0:
        tempStack = []
        while len(stack) > 0:
            curPage = stack.pop()
            if curPage[1] not in network:
                newWikiPage = {"name":curPage[0], "url":curPage[1], "links":{}}
                network[curPage[1]] = newWikiPage
                network[curPage[2]]["links"][newWikiPage["url"]] = newWikiPage["name"]
                if count+ 1 < NETWORK_LIMIT:
                    tempStack.extend(getLinksFromPage(newWikiPage))
        stack = tempStack
        count +=1
        makeCache(network, "wikiNetwork.json")
        makeCache({"stack": stack}, "wikiStack.json")
    knownPages = {}
    for key in network:
        knownPages[network[key]["name"].lower()] = 0
    return [network, knownPages]

    
def findConnection(network, term):
    stack = ["/wiki/University_of_Michigan"]
    network["/wiki/University_of_Michigan"]["parent"] = None
    termUrl = ""
    while len(stack) > 0:
        tempStack = []
        while len(stack) > 0:
            parentUrl = stack.pop()
            if network[parentUrl]["name"].lower() == term.lower():
                termUrl = parentUrl
                break
            for childUrl in network[parentUrl]["links"]:
                network[childUrl]["parent"] = parentUrl
                tempStack.append(childUrl)
        stack = tempStack
        if termUrl != "":
            break
    path = []
    while network[termUrl]["parent"] != None:
        path.append(network[termUrl]["name"])
        termUrl = network[termUrl]["parent"]
    path.append(network[termUrl]["name"])
    path.reverse() 
    return " --> ".join(path)

# Code from https://docs.google.com/presentation/d/1BHPzpBnZOtTwObtQpA1rzynxYgsWxvUXG98QSu3v0Z8/edit#slide=id.gf5d8039965_1_13
def fetchCache(filepath):
    ''' gets saved data
    
    Parameters
    ----------
    filepath:  str
        filepath

    Returns
    -------
    dictionary of stored data
    '''

    file = open(filepath, 'r')
    fileContents = file.read()
    data = json.loads(fileContents)
    file.close()
    return data

# Code from https://docs.google.com/presentation/d/1BHPzpBnZOtTwObtQpA1rzynxYgsWxvUXG98QSu3v0Z8/edit#slide=id.gf5d8039965_1_19
def makeCache(dict, filepath):
    ''' saves dict to file
    Parameters
    ----------
    dict: dict
        dictionary to save
    filepath: str
        filepath
    Returns
    -------
    None
    '''
    formattedJSON = json.dumps(dict)
    fw = open(filepath,"w")
    fw.write(formattedJSON)
    fw.close() 

def runThreeDegrees(network, knownPages):
    while True:
        print("Enter a term to search or wikipedia url. Enter 'exit program' to exit the program.\n")
        userSearchTerm = input()
        if userSearchTerm.lower() == "exit program":
            break
        if "wikipedia.org" in userSearchTerm:
            try:
                url = userSearchTerm.split("wikipedia.org")[1]
                correctTerm = network[url]["name"]
                answer = findConnection(network, correctTerm)
                print(f"Found! The path is below.\n{answer}\n")
            except:
                print("The search was unsuccessfull, please search another term.\n")
        else:
            if userSearchTerm.lower() in knownPages:
                answer = findConnection(network, userSearchTerm)
                print(f"Found! The path is below.\n{answer}\n")
            else:
                print("""Sorry, the term was not found. To ensure this is not a 
                      vocab/terminology issue, you can put insert the full URL of the page. If you'd rather not type 'No'.\n""")
                userSearchTwo = input()
                if userSearchTwo.lower() == "exit program":
                    break
                if "wikipedia.org" in userSearchTwo:
                    try:
                        url = userSearchTwo.split("wikipedia.org")[1]
                        correctTerm = network[url]["name"]
                        answer = findConnection(network, correctTerm)
                        print(f"Found! The path is below.\n{answer}\n")
                    except:
                        print("The search was unsuccessfull, please search another term.\n")

def checkPage(term):
    termModified = "_".join(term.split(" "))
    url = f"https://en.wikipedia.org/wiki/{termModified}"
    res = requests.get(url)
    if str(res.status_code)[0] == "2":
        return url.split("wikipedia.org")[1]
    return None

def selectLinkFromPage(url):
    links = getLinksFromPage({"name":"", "url":url, "links": {} })
    links.sort()
    for i in range(len(links)):
        print(f"{i+1}. {links[i][0]}")
    print("Please enter the number of the page that you would like to go to.\n")
    while True:
        userInput = input()
        if userInput.lower() == "exit program":
            return None
        try:
            return links[int(userInput) - 1][1]
        except:
            print("Please insert a valid number.\n")

def runWikipediaGame():
    term1 = None
    term2 = None
    while term1 == None:
        print("Please insert the starting article topic.\n")
        userinput = input()
        term1 = checkPage(userinput)
    while term2 == None:
        print("Please insert the ending article topic.\n")
        userinput = input()
        term2 = checkPage(userinput)
    while term1.lower() != term2.lower() and term1.lower() != "exit program":
        term1 = selectLinkFromPage(term1)
    
def main():
    network, knownPages = createNetwork()
    print(len(knownPages))
    #runWikipediaGame()
    runThreeDegrees(network, knownPages)

if __name__ == '__main__':
    main()
