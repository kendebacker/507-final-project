from bs4 import BeautifulSoup
import requests
import json
from flask import Flask, request
app = Flask(__name__)

"""
A lot of the flask stuff is straight from SI507_w12_L1_Flask.pptx
and the Flask template examples privided in class.
"""

BASE_URL = 'https://en.wikipedia.org'
NETWORK_LIMIT = 3
NETWORK ={}
KNOWN_PAGES={}
WIKI_GAME = [{"term": "", "url":""},{"term": "", "url":""},{"term": "", "url":""}]
WIKI_GAME_URLS=[]
STYLES ="""
body{
text-align: center;
}
.back-button{
position: absolute;
top: 15px;
left: 15px;
}
.reset-button{
position: absolute;
top: 15px;
left: 75px;
}
.urlGrid{
display: grid;
width: 100vw;
margin: auto;
grid-template-columns: 1fr 1fr 1fr;
flex-wrap: wrap;
justify-content: start;
align-items: start;
margin-top: 35px;
text-align: left;
column-gap: 15px;
width: 90%;
overflow: hidden;
flex-grow: 0;
}

.hidden{
display:none;
}
"""


# https://stackoverflow.com/questions/34853033/flask-post-the-method-is-not-allowed-for-the-requested-url

@app.route("/threeDegrees", methods=['POST', "GET"])
def threeDegrees():
    """
    Page for running the Three Degrees of U of M portion of my final project
    """
    if request.method == "POST":
        input = request.form["userInput"]
        result = runThreeDegrees(NETWORK, KNOWN_PAGES, input)
    else:
        result = ""
    return f"""
<style>
{STYLES}
</style>
<body>
<h1>Three Degrees of The University of Michigan</h1>
<form class="back-button" action="/" method="GET">
    <input type="submit" value="Back"/>
</form>

    <p>Enter either 1) a term to search or 2) the absolute URL of a Wikipedia page:</p>
<form action="/threeDegrees" method="POST">
    <p>
        Term of URL: <input name="userInput" type="text"/>
    </p>
    <input type="submit" value="Search"/>
    <p>{result}</p>
</form>  
</body>
"""

@app.route("/", methods=['POST', "GET"])
def index():
    """
    Home page for my final project, links to Three degrees of U of M and Wikipedia Game
    """

    return f"""
<style>
{STYLES}
</style>
<body>
    <h1>Ken's Final Project</h1>
    <p>Click below to view the Three Degrees of Michigan and the Wikipedia game. <br>I think the Three Degrees of Michigan is more neat so I would recommend viewing that first.</p>
    <div style="display: flex; width: 100%; justify-content: center;">
        <form action="/threeDegrees" method="GET">
            <input type="submit" value="Three Degrees of U of M"/>
        </form>
        <form style="margin-left: 25px" action="/wikipediaGame" method="GET">
            <input type="submit" value="Wikipedia Game"/>
        </form>
    </div>
</body>
"""


# https://www.geeksforgeeks.org/python-program-to-capitalize-the-first-letter-of-every-word-in-the-file/
# https://stackoverflow.com/questions/11774265/how-do-you-access-the-query-string-in-flask-routes
@app.route("/wikipediaGame", methods=['POST', "GET"])
def wikipediaGame():
    """
    Wikipedia game page, logic is quite messy at the moment, if had more time I would 
    try to make it neater
    """
    global WIKI_GAME, WIKI_GAME_URLS
    resetBool = request.args.get("reset")
    chosenPage = request.args.get("chosenPage")
    winnerStatus = request.args.get("winner")
    if resetBool == "true":
        resetWikiGame()
    enterAdvice = "Enter a topic"
    inputType = "text"
    currentUrls =""
    winningBanner = ""
    hidden = ""
    hidden2 = ""
    if winnerStatus == "true":
        winningBanner = "Congratulations you did it!"
        hidden2 = "hidden"
    if request.method == "POST":
        if WIKI_GAME[1]["term"] != "":
            hidden = "hidden"
        input = request.form["userInput"]
        if WIKI_GAME[0]["term"] == "":
            WIKI_GAME[0]["term"] = input
        elif WIKI_GAME[1]["term"] == "":
            WIKI_GAME[1]["term"] = input
        else:
            WIKI_GAME[2]["term"] = chosenPage
            for url in WIKI_GAME_URLS:
                if url[0] == chosenPage:
                    WIKI_GAME[2]["url"] = url[1]
        urls = runWikipediaGame(WIKI_GAME[0]["term"], WIKI_GAME[1]["term"], WIKI_GAME[2]["url"])
        WIKI_GAME[0]["url"] = urls[0]
        WIKI_GAME[1]["url"] = urls[1]
        if WIKI_GAME[0]["url"] == "":
            WIKI_GAME[0]["term"] = ""
        if WIKI_GAME[1]["url"] == "":
            WIKI_GAME[1]["term"] = ""
        if urls[1] == urls[0] and WIKI_GAME[0]["term"] != "":
            hidden2 = "hidden"
            hidden ="hidden"
            winningBanner = "Congratulations you did it!"
        if WIKI_GAME[1]["term"] != "" and WIKI_GAME[2]["term"] == "":
            urls = runWikipediaGame(WIKI_GAME[0]["term"], WIKI_GAME[1]["term"], WIKI_GAME[0]["url"])
            WIKI_GAME[2]["term"] = WIKI_GAME[0]["term"]
            WIKI_GAME[2]["url"] = WIKI_GAME[0]["url"]
            hidden ="hidden"
        WIKI_GAME_URLS = urls[2]
        currentUrls = ""
        for url in WIKI_GAME_URLS:
            winner = "false"
            if WIKI_GAME[1]["url"].lower() == url[1].lower():
                winner = "true"
            # https://stackoverflow.com/questions/11687970/what-is-the-proper-way-to-separate-query-string-parameters-in-a-url
            currentUrls = f"""{currentUrls}<form action="/wikipediaGame?chosenPage={url[0]}&winner={winner}" method="POST">
                                                <input hidden name="userInput"/>
                                                <input type="submit" value="{url[0]}"/>
                                            </form>"""
    return f"""
<style>
{STYLES}
</style>
<body>
<h1>The Wikipedia Game</h1>
<form class="back-button" action="/" method="GET">
    <input type="submit" value="Back"/>
</form>
<h2>{winningBanner}</h2>
<form action="/wikipediaGame?reset=false" method="POST">
    <p {hidden} >
        {enterAdvice}: <input name="userInput" type="text"/>
    </p>
    <input {hidden} type="submit" value="Search"/>
</form>
<p>Starting Page: <a href='{BASE_URL}{WIKI_GAME[0]["url"]}'>{WIKI_GAME[0]["term"].title()}</a></p>
<p>Target Ending Page: <a href='{BASE_URL}{WIKI_GAME[1]["url"]}'>{WIKI_GAME[1]["term"].title()}</a></p>
<p>Current Page: <a href='{BASE_URL}{WIKI_GAME[2]["url"]}'>{WIKI_GAME[2]["term"].title()}</a></p>
<form class="reset-button" action="/wikipediaGame?reset=true" method="POST">
    <input hidden name="userInput" type="{inputType}"/>
    <input type="submit" value="Reset Game"/>
</form>
<div class="urlGrid {hidden2}">{currentUrls}</div>  
</body>
"""

def resetWikiGame():
    ''' resets global wikipedia game state
    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    global WIKI_GAME 
    WIKI_GAME = [{"term": "", "url":""},{"term": "", "url":""},{"term": "", "url":""}]

def getLinksFromPage(page):
    ''' fetches links from a wikipedia page and organizes them
    Parameters
    ----------
    page: obj
        an object with a url (str), name (str) and links (list) properties 

    Returns
    -------
    list of links
    '''
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
    ''' function for creating wiki network for three degrees of michigan
    Parameters
    ----------
    None

    Returns
    -------
    network: dict
    knownPages: dict
    '''
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
    ''' fetches links from a wikipedia page and organizes them
    Parameters
    ----------
    network: dict
        wiki network
    term: str
        term searching for

    Returns
    -------
    path: string
    '''
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
        path.append(f"<a href='{BASE_URL}{termUrl}'>{network[termUrl]['name']}</a>")
        termUrl = network[termUrl]["parent"]
    path.append(f"<a href='{BASE_URL}{termUrl}'>{network[termUrl]['name']}</a>")
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

def runThreeDegrees(network, knownPages, userInput):
    ''' fetches links from a wikipedia page and organizes them
    Parameters
    ----------
    network: dict
        wiki network
    knownPages: dict
        dict of known pages
    userInput: str
        user search input

    Returns
    -------
    string
    '''
    if userInput == None:
        return "Enter a term to search or wikipedia url. Enter 'exit program' to exit the program."
    elif userInput.lower() == "exit program":
        return "exit program"
    elif "wikipedia.org" in userInput:
        try:
            url = userInput.split("wikipedia.org")[1]
            correctTerm = network[url]["name"]
            answer = findConnection(network, correctTerm)
            return f"{answer}"
        except:
            return "The search was unsuccessfull, please search another term.\n"
    elif userInput.lower() in knownPages:
            answer = findConnection(network, userInput)
            return f"{answer}"
    else:
        return "Sorry, the term was not found. To ensure this is not a vocab/terminology issue, try inserting the full URL of the page."
    
def checkPage(term):
    ''' validates wikipedia page exists
    Parameters
    ----------
    term: string
        search term

    Returns
    -------
    string (url) | None
    '''
    termModified = "_".join(term.split(" "))
    url = f"https://en.wikipedia.org/wiki/{termModified}"
    res = requests.get(url)
    if str(res.status_code)[0] == "2":
        return url.split("wikipedia.org")[1]
    return None

def selectLinkFromPage(url):
    ''' gets links from page for wikipedia game
    Parameters
    ----------
    url: string

    Returns
    -------
    links: list
    '''
    if url =="":
        return []
    linksRaw = getLinksFromPage({"name":"", "url":url, "links": {} })
    links = []
    seenLinks  = {}
    for link in linksRaw:
        if link[1] not in seenLinks and "File:" not in link[1] and "#" not in link[1]:
            seenLinks[link[1]] = 0
            links.append(link)
    links.sort()
    return links


def runWikipediaGame(term1, term2, currentPage):
    ''' get output for wikipedia game
    Parameters
    ----------
    term1: string
    term2: string
    currentPage: string

    Returns
    -------
    links: list
    '''
    url1 = checkPage(term1)
    url2 = checkPage(term2)
    if currentPage != None:
        url3 = selectLinkFromPage(currentPage)
    else:
        url3 = ""
    if url1 == None:
        url1 =""
    if url2 == None:
        url2 = ""
    return [url1, url2, url3]
    
def main():
    # https://stackoverflow.com/questions/423379/using-global-variables-in-a-function
    global NETWORK, KNOWN_PAGES
    NETWORK, KNOWN_PAGES = createNetwork()
    app.run(debug=True)

if __name__ == '__main__':
    main()
