import urllib.request # instead of urllib2 like in Python 2.7
from bs4 import BeautifulSoup
import requests
import time
import re 
import pyodbc
from JGame  import JGame


global jg 
global conn 

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=LEGOLAS;'
                      'Database=Jeopardy;'
                      'Trusted_Connection=yes;')

def grabGameDetails(game, seasonID):
  time.sleep(5) # sleep 5 seconds as to not overwhelm server

  page_link = game
  page_response = requests.get(page_link, timeout=5)
  page_content = BeautifulSoup(page_response.content, "lxml")
  x = re.search('#([0-9]+)', page_content.title.text)
  
 
  if x:
    jg = JGame()
    jg.gameNumber = x.group(1)
    jg.DBConnection =  conn
    jg.gameURL = game
    jg.seasonID = seasonID
    
  jg.InsertGameRecord()
 
  if jg.processedIND == 0:
    catTags = page_content.find_all("td", attrs={"class":"category_name"})
    i = 0
    for cat in catTags:
      if (i < 6):
        jg.addCat(1, cat.text)
        i=i+1
      elif (i > 5 and i < 12):
        jg.addCat(2, cat.text)
        i=i+1
      else:
        jg.addCat(3, cat.text)
        i = 0
    grabQuestionsAnswers(page_content, jg)



def grabQuestionsAnswers(gamepage, jg):
  clueTags = gamepage.find_all("td", attrs={"class":"clue_text"})
  #valueTags = gamepage.find_all("td", attrs={"class":"clue_value"})
 
  for clue in clueTags:
    x = re.search('clue_([J|D|F]+)_*([1-6])*_*([1-5])*', clue.attrs["id"])
    if x:
      #jg.addClue(x.group(1),x.group(2),x.group(3), clue.text )
      answerTags = gamepage.find_all("div",attrs={"onclick":"togglestick('" + x.group(0) +"_stuck')"})
      for answer in answerTags:
        y = re.search('<em class=[\\]*\"correct_response[\\]*\">[<i>]*(.+)[<\/i>]*<\/em>',answer.attrs["onmouseover"])
        if y:
          #jg.addAnswer(x.group(1),x.group(2),x.group(3), y.group(1) )
          jg.addQuestionAnswer(x.group(1),x.group(2),x.group(3),clue.text, y.group(1) )
      
  

def grabSeasonData(seasonURL, seasonID):
  time.sleep(5) # sleep 5 seconds as to not overwhelm server

  page_link = 'http://www.j-archive.com/' + seasonURL
  page_response = requests.get(page_link, timeout=5)
  page_content = BeautifulSoup(page_response.content, "lxml")
  aTags = page_content.find_all('a')

  for game in aTags:
    if (game.attrs["href"].find('showgame.php') != -1):
        grabGameDetails(game.attrs["href"], seasonID)

  cur = conn.cursor()
  cur.execute("""UPDATE [dbo].[Seasons]
             SET processed_IND = 1
             WHERE season_id = ?""",seasonID)
  cur.commit()

def processSeasons(seasonlist):
  #print (seasonlist.head)
  seasons = []

  aTags = seasonlist.find_all('a')
  for season in aTags:
    if (season.attrs["href"].find('showseason.php') != -1):
      if (season.attrs["href"].find("http") == -1):
        seasons.append(season.attrs["href"])


  seasons.reverse()
  cur = conn.cursor()

  for season in seasons:
    x = re.search('.*\?season=(\w+)', season)
    if x:
      if cur.execute("select * from seasons where season_url = ?", season).rowcount == 0:
        cur.execute("""INSERT INTO [dbo].[Seasons]
             ([season_name]
             ,[season_url])
            values(?, ?)""",x.group(1), season)
        cur.commit()
        sID = cur.execute("select season_id from seasons where season_url = ?", season).fetchval()
        grabSeasonData(season, sID)
      else:
        if cur.execute("""
                      select * from dbo.seasons s 
                      where s.season_url = ? and s.processed_ind is null""", season):
          sID = cur.execute("select season_id from seasons where season_url = ?", season).fetchval()
          grabSeasonData(season, sID)
        else:
          print(cur)

  cur.close()



def main():
  
  page_link = 'http://www.j-archive.com/listseasons.php'
  page_response = requests.get(page_link, timeout=5)
  page_content = BeautifulSoup(page_response.content, "lxml")
  processSeasons(page_content)
  
  
if __name__ == "__main__":
  main()
