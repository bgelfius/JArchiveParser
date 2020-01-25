from enum import Enum

class Round(Enum):
    Jeopardy = 1
    DoubleJeopardy =2
    FinalJeopardy = 3

class JGame:
    roundOneCat = [0] * 6
    roundOneClue = [[0 for i in range(5)] for j in range(6)] 
    roundOneAnswer = [[0 for i in range(5)] for j in range(6)] 
    roundTwoCat = [0] * 6
    roundTwoClue = [[0 for i in range(5)] for j in range(6)] 
    roundTwoAnswer = [[0 for i in range(5)] for j in range(6)] 
    roundThreeCat = ""
    roundThreeClue = ""
    roundThreeAnswer = ""
    _gameNumber = 0
    _gameURL = ""
    idx  = 0
    _DBConnection = ""
    _seasonID = 0
    _gameID = 0
    _processedIND = 0

    #def __init__(self, gameNumber, dbconnection):
    def set_processedIND(self, processedIND):
        self._processedIND = processedIND
    def get_processedIND(self):
        return self.processedIND
    processedIND = property(get_processedIND, set_processedIND ) 

    def set_seasonID(self, seasonID):
        self._seasonID = seasonID
    def get_seasonID(self):
        return self._seasonID
    seasonID = property(get_seasonID, set_seasonID ) 

    def set_gameID(self, gameID):
        self._gameID = gameID
    def get_gameID(self):
        return self._gameID
    gameID = property(get_gameID, set_gameID ) 

    def set_DBConnection(self, dbconnection):
        self._DBConnection = dbconnection
    def get_DBConnection(self):
        return self._DBConnection

    DBConnection = property(get_DBConnection, set_DBConnection ) 

    def set_gameNumber(self, gamenumber):
        self._gameNumber = gamenumber
    def get_gameNumber(self):
        return self._gameNumber

    gameNumber = property(get_gameNumber, set_gameNumber ) 

    def set_gameURL(self, gameurl):
        self._gameURL = gameurl
    def get_gameURL(self):
        return self._gameURL

    gameURL = property(get_gameURL, set_gameURL ) 
        
    def addQuestionAnswer(self, round, categorynumber, cluenumber , clue, answer):
        cur = self.DBConnection.cursor()
        sql = """INSERT INTO [dbo].[Questions]
           ([question_text]
           ,[answer_text]
           ,[question_amt]
           ,[category_id])
            VALUES
           (?, ?, ?, ?)"""
        if (round == 'J'):
            cur.execute(sql, clue, answer, 0, self.roundOneCat[int(categorynumber) - 1])
            clueID = cur.execute("SELECT @@IDENTITY AS id").fetchval()
        elif (round == 'DJ'):
            cur.execute(sql, clue, answer, 0, self.roundTwoCat[int(categorynumber) - 1])
            clueID = cur.execute("SELECT @@IDENTITY AS id").fetchval()
        else:
            cur.execute(sql, clue, answer, 0, self.roundThreeCat)
            clueID = cur.execute("SELECT @@IDENTITY AS id").fetchval()
    

        cur.commit()


      
    def addCat(self, round, category):
        cur = self.DBConnection.cursor()
        sql = """INSERT INTO [dbo].[Categories]
            ([category]
            ,[round_id]
            ,[game_id])
                values(?, ?, ?)"""
        if (round ==1):
            #self.roundOneCat[self.idx] = category
            cur.execute(sql,category, Round.Jeopardy.value, self.gameID)
            catID = cur.execute("SELECT @@IDENTITY AS id").fetchval()
            self.roundOneCat[self.idx] = catID
            
            if (self.idx == 5):
                self.idx = 0
            else:
                self.idx = self.idx + 1
        elif (round == 2):
#            self.roundTwoCat[self.idx] =  category
            cur.execute(sql,category, Round.DoubleJeopardy.value, self.gameID)
            catID = cur.execute("SELECT @@IDENTITY AS id").fetchval()
            self.roundTwoCat[self.idx] =  catID
            if (self.idx == 5):
                self.idx = 0
            else:
                self.idx = self.idx + 1
        else:
            #self.roundThreeCat = category
            cur.execute(sql,category, Round.FinalJeopardy.value, self.gameID)
            catID = cur.execute("SELECT @@IDENTITY AS id").fetchval()
            self.roundThreeCat = catID
            
        
        cur.commit()


    def printCats(self):
        print("Round 1")
        for cat in self.roundOneCat:
            print(cat)
        
        print("Round 2")
        for cat in self.roundTwoCat:
            print(cat)
        
        print("Round 3")
        print(self.roundThreeCat)

    def printClues(self):
        print("Round 1")
        idx = 0
        
        clueno = 0
        for clue in self.roundOneClue:
            print ("category:" + self.roundOneCat[idx])
            clueno = 0
            for ctext in clue:
                print(ctext)
                print(self.roundOneAnswer[idx][clueno])
                clueno += 1
            idx += 1  
        
        print("Round 2")
        idx = 0 
        clueno = 0
        for clue in self.roundTwoClue:
            print ("category:" + self.roundTwoCat[idx])
            clueno = 0
            for ctext in clue:
                print(ctext)
                print(self.roundOneAnswer[idx][clueno])
                clueno += 1
            idx += 1  
          
       
        print("Round 3")
        print(self.roundThreeCat)
        print(self.roundThreeClue)  
        print(self.roundThreeAnswer)

    def InsertGameRecord(self):
        cur = self.DBConnection.cursor()
        if cur.execute("select * from games where game_url = ? and processed_ind = 0", self.gameURL).rowcount == 0:
            cur.execute("""INSERT INTO [dbo].[Games]
                ([game_name]
                ,[game_url]
                ,[season_id]
                ,[processed_ind])
                VALUES (?,?,?,?)
                """, self.gameNumber, self.gameURL, self.seasonID, 1)
            self.gameID =  cur.execute("SELECT @@IDENTITY AS id").fetchval()
            cur.commit()
            self.processedIND = 0
        else:
            self.processedIND = 1

        

     
    
