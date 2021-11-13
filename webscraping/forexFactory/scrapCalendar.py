
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
import cloudscraper
from datetime import timedelta



class CalendarDataFeed:
    
    def __init__(self, startYear, endYear, calendarSite = "https://www.forexfactory.com/calendar?day=" ):
        self.startYear = startYear
        self.endYear = endYear
        self.calendarSite = calendarSite
        self.filename = ''
        self.saveLocation = ''
        self.loadLocation = ''
        self.calName = ''
        
        self.TimeDictionary = {
                                "1": "13",
                                "2": "14",
                                "3": "15",
                                "4": "16",
                                "5": "17",
                                "6": "18",
                                "7": "19",
                                "8": "20",
                                "9": "21",
                                "10": "22",
                                "11": "23",
                                "12": "12"
                                }
        
        self.calendarMonths = {
                                1: "jan",
                                2: "feb",
                                3: "mar",
                                4: "apr",
                                5: "may",
                                6: "jun",
                                7: "jul",
                                8: "aug",
                                9: "sept",
                                10: "oct",
                                11: "nov",
                                12: "dec"
                                }

             
    def getDailyEvents(self, calendarSite, caldate, timeZone ='UTC'):
        try:
            parseURL = calendarSite + str(self.calendarMonths[caldate.month]) + str(caldate.day) + "." + str(caldate.year)
            scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
            content = scraper.get(parseURL).text
            soup = BeautifulSoup(content, "html.parser")
            table =  soup.find_all("tr", {"class":"calendar_row"})
            forcal = []
            for item in table:
                dict= {}      
                dict['Currency'] =  item.find_all("td", {"class": "calendar__currency"})[0].text
                dict['Event'] =  item.find_all("td", {"class": "calendar__event"})[0].text
                dict['Time_Eastern'] =  item.find_all("td", {"class": "calendar__time"})[0].text
                impact = item.find_all("td", {"class": "impact"})      
                for icon in range(0, len(impact)):
                    try:
                        dict['Impact'] = impact[icon].find_all("span")[0]["title"].split('  ', 1)[0]
                    except:
                        dict['Impact'] = ''
                dict['Actual'] =  item.find_all("td", {"class": "calendar__actual"})[0].text
                dict['Forecast'] =  item.find_all("td", {"class": "calendar__forecast"})[0].text
                forcal.append(dict)      
            df = pd.DataFrame(forcal)
            df['Currency'] = df.Currency.str.replace(r'\n', '')
            df['Time_Eastern'] = df['Time_Eastern'].fillna("0")
            df['Time_Eastern'] = df['Time_Eastern']
            newDayTime = []
            for item in range(0,len(df)):
                if ('Day' in df.iloc[item][2]):
                    newDayTime.append(24)
                elif ("pm" in df.iloc[item][2]):
                    hour = df.iloc[item][2].replace("pm", '').replace("am", '').replace(u'\xa0', ' ').strip()
                    afternoon = hour[0:hour.find(":")]
                    afternoon = self.TimeDictionary[afternoon]
                    newTime = afternoon +hour[hour.find(":"):]
                    newDayTime.append(newTime)  
                elif ("am" in df.iloc[item][2]):
                     if (len(df.iloc[item][2].replace("pm", '').replace("am", '')+ ":00") == 7):
                         temp = "0" + df.iloc[item][2].replace("pm", '').replace("am", '')
                         newDayTime.append(temp)
                     else:
                         newDayTime.append(df.iloc[item][2].replace("pm", '').replace("am", ''))
                else:
                    newDayTime.append("0")
            df["Time"] = newDayTime
            df["Date"] = str(caldate.year) + "." + str(caldate.month) + "." + str(caldate.day)
            df["TimeIndex"] = self.DateConverter(df)
            df["Event"] = df["Event"].str.lstrip()
            df["Event"] = df["Event"].str.rstrip()
            df = df.drop(['Time_Eastern', 'Impact', 'Forecast'], axis = 1)
            return df
        except Exception as e:
            print('Error updating economic calendar Error could be: ', str(e))


    def getDaySeveralCalender(self, urls, caldate, timeZone ='UTC'):
        try:
            for site in urls:
                frame = self.getDailyEvents(site, caldate, timeZone ='UTC')
                result = pd.concat([pd.DataFrame(),frame])
            result = result.sort_values(by='Time', ascending=True)
            result = result.reset_index(drop=True)
            return result
        except Exception as e:
            print('Error updating economic calendar Error could be: ', str(e))
        

    def saveCalendar(self, data, saveLocation, filename):
        try:
            self.saveLocation = saveLocation
            self.filename = filename
            data.to_csv(self.saveLocation + self.filename + ".csv", index = True)
            print('Saving complete...')
        except:
            print('Error saving file')
      

    def loadhistCalendar(self, loadLocation, calName):
        try:
            self.loadLocation = loadLocation
            self.calName = calName
            histcal  = pd.read_csv(self.loadLocation + self.calName + '.csv')
            return histcal
        except Exception as e:
            print('Error loading economic calendar Error could be: ', str(e))
        

    def loadhistCalendarTimeIndexVersion(self, loadLocation, calName, timeZone ='UTC'):
        try:
            self.loadLocation = loadLocation
            self.calName = calName
            histcal  = pd.read_csv(self.loadLocation + self.calName + '.csv')
            histcal["TimeIndex"] = self.DateConverter(histcal)
            histcal = histcal[['Date',
                                 'Time',
                                 'Currency',
                                 'Event',
                                 'Impact',
                                 'Actual',
                                 'Forecast',
                                 'Previous',
                                 'TimeIndex']]
            histcal["Date"] = [ item.date() for item in histcal["TimeIndex"]]
            return histcal
        except Exception as e:
            print('Error loading economic calendar Error could be: ', str(e))


    def createFullDay(self, frames):
        result = pd.concat(frames)
        todaysEvents = result.sort_values(by='Time', ascending=True)
        return todaysEvents
    
    
    def currencyPairs(self, data, curr1 = 'EUR', curr2 = 'CHF'):
        currPair = data[ (data["Currency"] == curr1) &
                         (data["Currency"] == curr2)]
        return currPair
    
    
    def downloadCalendar(self, calendarSite, startDate, endDate, timeZone ='UTC'):
        try:
            for caldate in self.daterange(startDate, endDate):
                currentDay = self.getDailyEvents(self, calendarSite, caldate, timeZone ='UTC')
                result = pd.concat([pd.DataFrame(),currentDay])
            return result
        except Exception as e:
            print('Error creating new Date column: ', str(e))


    def eventInFuture(self, calendar, priceFeedTime, delta, timeIndex = "TimeIndex"):
        newTime = priceFeedTime + timedelta(minutes=delta)
        if calendar[calendar[timeIndex] == newTime]["Event"].isnull().iloc[0]:
            if len(calendar[calendar["TimeIndex"] == newTime]["Event"]) > 1:
                return calendar[calendar["TimeIndex"] == newTime]["Event"]
            else:
                return calendar[calendar["TimeIndex"] == newTime]["Event"].iloc[0]

    
    '''END Corefunctions'''
    
    '''Start Helperfunction'''


    def DateConverter(self, data, dateColumn = "Date", dayTimeColumn = "Time",  timeZone ='UTC'):
        try:
            formTime = '%Y.%m.%d %H:%M'
            tempDF = pd.DataFrame()
            datum = []
            for index,row in data.iterrows():
                try:
                    datum.append(datetime.strptime(row[dateColumn] + " " + str(row[dayTimeColumn]), formTime))
                except:
                    datum.append(datetime.strptime(row[dateColumn] + " " + '00:00', formTime))
            tempDF["TempTime"] = datum
            dateTS = [item.tz_localize(timeZone) for item in tempDF["TempTime"]]
            return dateTS
        except Exception as e:
            print('Error creating new Date column: ', str(e))

        
    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)
            
            
            
            
    