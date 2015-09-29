#! bin/python

import csv, json, requests, sys, time
from bs4 import BeautifulSoup

filepath = "IRONMAN_Results"

raceURLS = [("im_arizona_2014","http://www.ironman.com/triathlon/events/americas/ironman/arizona/results.aspx"),
            ("im_austrailia_2015","http://www.ironman.com/triathlon/events/asiapac/ironman/australia/results.aspx"),
            ("im_austria_2015","http://www.ironman.com/triathlon/events/emea/ironman/austria/results.aspx"),
            ("im_barcelona_2014","http://www.ironman.com/triathlon/events/emea/ironman/barcelona/athletes/results.aspx"),
            ("im_boulder_2015","http://www.ironman.com/triathlon/events/americas/ironman/boulder/results.aspx"),
            ("im_brazil_2015","http://www.ironman.com/triathlon/events/americas/ironman/brazil/results.aspx"),
            ("im_cairns_2015","http://www.ironman.com/triathlon/events/asiapac/ironman/cairns/results.aspx"),
            ("im_canada_2015","http://www.ironman.com/triathlon/events/americas/ironman/canada/results.aspx"),
            ("im_chattanooga_2014","http://www.ironman.com/triathlon/events/americas/ironman/chattanooga/results.aspx?rd=20140928"),
            ("im_coeurdalene_2015","http://www.ironman.com/triathlon/events/americas/ironman/coeur-dalene/results.aspx"),
            ("im_copenhagen_2015","http://www.ironman.com/triathlon/events/emea/ironman/copenhagen/results.aspx"),
            ("im_cozumel_2014","http://www.ironman.com/triathlon/events/americas/ironman/cozumel/results.aspx"),
            ("im_florida_2014","http://www.ironman.com/triathlon/events/americas/ironman/florida/results.aspx"),
            ("im_fortazela_2014","http://www.ironman.com/triathlon/events/americas/ironman/fortaleza/results.aspx"),
            ("im_france_2015","http://www.ironman.com/triathlon/events/emea/ironman/france/results.aspx"),
            ("im_frankfurt_2015","http://www.ironman.com/triathlon/events/emea/ironman/frankfurt/results.aspx"),
            ("im_japan_2015","http://www.ironman.com/triathlon/events/asiapac/ironman/japan/results.aspx"),
            ("im_lakeplacid_2015","http://www.ironman.com/triathlon/events/americas/ironman/lake-placid/results.aspx"),
            ("im_lanzarote_2015","http://www.ironman.com/triathlon/events/emea/ironman/lanzarote/results.aspx"),
            ("im_maastrichtlimburg_2015","http://www.ironman.com/triathlon/events/emea/ironman/maastricht/results.aspx"),
            ("im_malaysia_2014","http://www.ironman.com/triathlon/events/asiapac/ironman/malaysia/results.aspx"),
            ("im_mallorca_2014","http://eu.ironman.com/triathlon/events/emea/ironman/mallorca/results.aspx?rd=20140927"),
            ("im_maryland_2014","http://www.ironman.com/triathlon/events/americas/ironman/maryland/results.aspx"),
            ("im_melbourne_2015","http://www.ironman.com/triathlon/events/asiapac/ironman/melbourne/results.aspx"),
            ("im_monttremblant_2015","http://www.ironman.com/triathlon/events/americas/ironman/mont-tremblant/results.aspx"),
            ("im_newzealand_2015","http://www.ironman.com/triathlon/events/asiapac/ironman/new-zealand/results.aspx"),
            ("im_southafrica_2015","http://www.ironman.com/triathlon/events/emea/ironman/south-africa/results.aspx"),
            ("im_sweden_2015","http://www.ironman.com/triathlon/events/emea/ironman/kalmar/results.aspx"),
            ("im_switzerland_2015","http://www.ironman.com/triathlon/events/emea/ironman/switzerland/results.aspx"),
            ("im_taiwan_2015","http://www.ironman.com/triathlon/events/asiapac/ironman/taiwan/results.aspx"),
            ("im_texas_2015","http://www.ironman.com/triathlon/events/americas/ironman/texas/results.aspx"),
            ("im_uk_2015","http://www.ironman.com/triathlon/events/emea/ironman/uk/results.aspx"),
            ("im_wales_2014","http://www.ironman.com/triathlon/events/emea/ironman/wales/results.aspx?rd=20140914"),
            ("im_westernaustralia_2014","http://www.ironman.com/triathlon/events/asiapac/ironman/western-australia/results.aspx"),
            ("im_wisconsin_2014","http://www.ironman.com/triathlon/events/americas/ironman/wisconsin/results.aspx?rd=20140907")]

def main(args):
    scriptStartTime = time.time()
    for race in raceURLS:
        getRaceData(race[0], race[1])

    totalExecutionTime = time.time()
    print "Finished scraping data for {} races. Execution time: {}(s)".format(len(raceURLS), totalExecutionTime)

def getRaceData(raceName, raceURL):
    # Grab the total number of result pages
    soup = getPageData(raceURL)
    totalPages = int(soup.find(id="pagination").find_all('span')[-2].text)

    # Modify the race URL if we are looking at a previous years result.
    # This hack will assure we get the right # of pages for the specified url, 
    # while still allowing the script to traverse as normal
    raceURL=raceURL.split("?")[0]
    
    print "Collecting race data for {}".format(raceName)
    print "Getting {} pages of results from {}".format(totalPages, raceURL)
    
    startTime = time.time()
    resultsJSON = {}
    currentID = 0

    # Create CSV File to store results
    with open('{}/{}.csv'.format(filepath, raceName), 'w') as csvfile:
        fieldnames = ["name","genderRank","divRank","overallRank","bib","division",
                    "age","state","country","profession","points","swim","swimDistance",
                    "t1","bike","bikeDistance","t2","run","runDistance","overall"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate through available pages
        for page in range(1, totalPages+1):
            currTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print "\tCurrent status as of {}:   Page: {}   Progress: {}%".format(currTime, page, float(page/totalPages))
            
            # Get each pages data to parse href
            pageURL = raceURL + '?p=' + str(page)
            pageData = getPageData(pageURL)

            # Iterate through each athletes results page
            for link in getDetailedResultsLinks(pageData):
                resultPage = getPageData(raceURL + link)
                try:
                    athleteJSON = parseAthleteResult(resultPage)
                    writer.writerow(athleteJSON)
                    resultsJSON[currentID] = athleteJSON
                    currentID+=1
                except Exception, e:
                    print "\tError encountered on athlete page {}: {}".format(raceURL + link, e)

        csvfile.close()

    # Save JSON output
    with open('{}/{}.json'.format(filepath, raceName), 'w') as fp:
        json.dump(resultsJSON, fp)

    endTime = time.time()
    print "Finished scraping results for {}. Execution time: {}(s)".format(raceName, endTime - startTime)
    return True

# Return the BS object of the specified url
def getPageData(url):
    # Hardcoding a sleep to rate limit the requests. Trying to be a good citizen
    time.sleep(.5)
    data = requests.get(url).text
    return BeautifulSoup(data, "html.parser")


# Return the athletes result urls from results table
def getDetailedResultsLinks(data):
    hrefList = []
    for link in data.find_all("a", "athlete", href=True):
        hrefList.append(link['href'])
    return hrefList


# Return a dictionary with all of the desired athlete information from result page object
def parseAthleteResult(resultPage):
    # Create "schema" dictionary to store athlete result
    result = {
        "name":"",
        "genderRank":"",
        "divRank":"",
        "overallRank":"",
        "bib":"",
        "division":"",
        "age":"",
        "state":"",
        "country":"",
        "profession":"",
        "points":"",
        "swim":"",
        "swimDistance":"",
        "t1":"",
        "bike":"",
        "bikeDistance":"",
        "t2":"",
        "run":"",
        "runDistance":"",
        "overall":""
    }

    # This is a nasty hardcoded list to grab all of this data
    result["name"] = resultPage.find_all("h1")[0].text
    result["genderRank"] = resultPage.find(id="gen-rank").text.split(":")[1].strip()
    result["divRank"] = resultPage.find(id="rank").text.split(":")[1].strip()
    result["overallRank"] = resultPage.find(id="div-rank").text.split(":")[1].strip()

    # Populate result with info from general table
    generalInfoTable = resultPage.find(id="general-info")
    result["bib"] = generalInfoTable.tbody.find_all('td')[1].text
    result["division"] = generalInfoTable.tbody.find_all('td')[3].text
    result["age"] = generalInfoTable.tbody.find_all('td')[5].text
    result["state"] = generalInfoTable.tbody.find_all('td')[7].text
    result["country"] = generalInfoTable.tbody.find_all('td')[9].text
    result["profession"] = generalInfoTable.tbody.find_all('td')[11].text
    result["points"] = generalInfoTable.tbody.find_all('td')[13].text

    # Populate result with info from "athelete" table. Nice css typo
    athleteDetailsTable = resultPage.find(id="athelete-details")
    splitDetailsTable = resultPage.find("div", class_="athlete-table-details")
    result["swim"] = athleteDetailsTable.tbody.find_all('td')[1].text
    result["swimDistance"] = splitDetailsTable.find_all('tfoot')[0].find_all('td')[1].text
    result["t1"] = splitDetailsTable.find_all('table')[3].find_all('td')[1].text
    result["bike"] = athleteDetailsTable.tbody.find_all('td')[3].text
    result["bikeDistance"] = splitDetailsTable.find_all('tfoot')[1].find_all('td')[1].text
    result["t2"] = splitDetailsTable.find_all('table')[3].find_all('td')[3].text
    result["run"] = athleteDetailsTable.tbody.find_all('td')[5].text
    result["runDistance"] = splitDetailsTable.find_all('tfoot')[2].find_all('td')[1].text
    result["overall"] = athleteDetailsTable.tbody.find_all('td')[7].text
    
    return result
    

if __name__ == "__main__":
    main(sys.argv[1:])