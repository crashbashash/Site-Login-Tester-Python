#!/bin/python3

from os import system, path, _exit
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionBuilder, ActionChains
from typing import List, Dict, Tuple
from random import randint
from time import sleep
from threading import Thread

class GoodStuff:
    running: bool = False
    accountsCreated: int = 0
    maxAccounts: int = 0
    failedAccounts: int = 0
    threadStatus: str = ""
    t_driver: webdriver = None
    runLoc: str = path.dirname(path.realpath(__file__))+"/"

    #Function called when class is created
    def __init__(self, max: int):
        self.maxAccounts = max

    #Function to change the thread status
    def ChangeStatus(self, text: str):
        self.threadStatus = f"{text} | Created: {self.accountsCreated} | Failed: {self.failedAccounts}"

    #Function to generate a UK phone number
    def GenPhoneNumber(self, prefix: str = "07", length: int = 9) -> str:
        number: str = prefix

        for _ in range(0,length):
            number += str(randint(0,9))

        return number
    
    #Function to generate a first and last name
    def GenName(self, firstNamesList: List[str], lastNamesList: List[str]) -> Tuple[str, str]:
        name: Tuple[str, str] #Instantiate the Tuple used to store the name

        firstName: str = firstNamesList[randint(0, len(firstNamesList)-1)].replace("\n", "") #Generate first name
        lastName: str = lastNamesList[randint(0, len(lastNamesList)-1)].replace("\n", "") #Generate last name

        while True: #Main generation loop
            done: bool = True #Bool to determine if the bot has created a suitable name

            for letter in firstName: #Loop through characters in the first name
                if not letter.isalpha: #Check if the current character isn't a letter
                    done = False #Set the done bool to false
            
            if done: #Only check the characters in the second name if the first name only has letters
                for letter in lastName: #Loop through characters in the last name
                    if not letter.isalpha: #Check if the current character isn't a letter  
                        done = False #Set the done bool to false

            if not done: #Check if a suitable name hasn't been created
                ##Generate the last and first names again
                firstName: str = firstNamesList[randint(0, len(firstNamesList)-1)].replace("\n", "")
                lastName: str = lastNamesList[randint(0, len(lastNamesList)-1)].replace("\n", "")
            else:
                break #Break out of name gen loop when a suitable name has been created
        
        ##Add both names to the name tuple
        name = ( firstName.capitalize(), lastName.capitalize() )

        return name #Return the name tuple

    #Function to generate an email from a name
    def GenEmail(self, name: Tuple[str, str]) -> str:
        email: str #Create the email variable
        #List of email domains to use
        emailDomainList: List[str] = [ "hotmail.co.uk", "hotmail.com", "live.co.uk", "live.com", "gmail.com", "googlemail.com", "yahoo.co.uk", "yahoomail.com" ]

        domain: str = emailDomainList[randint(0, len(emailDomainList)-1)] #Select a random domain to use

        #Get the first and last name to use
        firstName: str = str(name[0])
        lastName: str = str(name[1])

        firstName = firstName.replace(' ', '')
        lastName = lastName.replace('', '')

        email = f"{firstName}{lastName}{randint(0,999)}@{domain}" #Create the users email using the info created above

        return email #Return the email string

    #Function to generate a password from a list of passwords
    def GenPassword(self, passList: List[str], maxLen: int = 11) -> str:
        password: str = passList[randint(0, len(passList)-1)].replace("\n", "") ##Get a random password from the list given

        while (not password[0].isalpha and not password[1].isalpha): #Check if the first and second chars of the pass are alphabetic
            password = passList[randint(0, len(passList)-1)]

        password += str(randint(0, 9)) #Ensure atleast 1 number is added to the pass

        for _ in range(len(password), maxLen): ##Add random numbers to the end of the password
            password += str(randint(0, 9))
        
        return password.capitalize() #Return the formatted password

    #Function to wait for an element to load
    def WaitForElementToLoad(self, driver: webdriver, by: By, locator: str, timeOut: int = 120) -> bool:
        #try:
        WebDriverWait(driver, timeOut).until(EC.presence_of_element_located((by, locator))) #Wait for elem to become visible
        return driver.find_element(by, locator).is_displayed and driver.find_element(by, locator).is_enabled #Return the status of the elem
        #except:
          #  return False #Return false if it errors out
    
    def ScrollToElem(self, driver: webdriver, by: By, selector: str, timeOut: int = 120) -> bool:
        
        if self.WaitForElementToLoad(driver, by, selector, timeOut):
            try:
                elem = driver.find_element(by, selector) #Find the specified elem
                ActionChains(driver).move_to_element(elem) #Scroll to the element
                return True #Return true if it succeeds without error
            except:
                return False #Return false if it errors out
        
        return False #Return false if the elem fails to load

    #Function used to write text to an element
    def WriteTextToElem(self, driver: webdriver, by: By, selector: str, text: str, _clear: bool = True, timeOut: int = 120) -> bool:
        if self.WaitForElementToLoad(driver, by, selector, timeOut): #Wait for the elem to load
            try:
                self.ScrollToElem(driver, by, selector, timeOut) #Scroll to element
                if _clear:
                    driver.find_element(by, selector).clear() #Clear the elems text if desired
                driver.find_element(by, selector).send_keys(text) #Send the desired keys to the element
                return True #Return true for success
            except Exception as e:
                print(e)
                return False #Return false if it spits an error
        
        return False #Return false if the elem hasn't loaded

    #Function used to select an option in a drop-down box element
    def SelectDropDownOption(self, driver: webdriver, by: By, selector: str, option: int = -1, strOption: str = "", timeOut: int = 120) -> bool:
        if self.WaitForElementToLoad(driver, by, selector, timeOut):
            try:
                elem = Select(driver.find_element(by, selector)) #Get the drop down box elem
                self.ScrollToElem(driver, by, selector, timeOut) #Scroll to the elem

                if option != -1: #If a number has been specified then search by index
                    elem.select_by_index(option)
                else: #If a number has not been specified then search by string
                    elem.select_by_visible_text(strOption)
                return True #Return true if it succeeds
            except:
                pass
        return False #Return false if anything fails

    #Function used to click on an element
    def ClickElem(self, driver: webdriver, by: By, selector: str, timeOut: int = 120) -> bool:
        if self.WaitForElementToLoad(driver, by, selector, timeOut): #Wait for elem to load
            try:
                self.ScrollToElem(driver, by, selector, timeOut) #Scroll to elem
                driver.find_element(by, selector).click() #Click element
                return True #Return true for success
            except:
                pass

        return False #Return false if it fails to load the elem

    #Function used to generate chrome driver info
    def GenDriverInfo(self, headless: bool = True, debug: bool = False) -> Options:
        options: Options = Options()

        if headless:
            options.add_argument("-headless")
        if not debug:
            options.add_argument("--log-level=3")
            options.add_argument("--silent")
        
        return options
        
    #Function used to create accounts on a fake dating site
    def DatingSiteCreatorThread(self, headless: bool = True, debug: bool = False):
        self.running = True

        firstNamesList: List[str] = open(self.runLoc+'Lists/FirstNames.txt').readlines() #Get the first name list
        lastNamesList: List[str] = open(self.runLoc+'Lists/LastNames.txt').readlines() #Get the last name list
        passwordList: List[str] = open(self.runLoc+'Lists/Passwords.txt').readlines() #Get the password list

        url: str = "https://cpafeels.com/rgn/p/r/7/" #Url to the site we are creating login info for

        resetCount: int = 0 #Store the amount of times the bot has relaunched chrome
        resetCounter: int = 0 #Store the reset counter

        driverOptions: Options = self.GenDriverInfo(headless, debug) #Generate driver info

        self.t_driver = None

        while True: #Main creator loop
            if self.accountsCreated % 15 == 0 and self.t_driver != None and self.accountsCreated > 0: ##Every 250 accounts reset the chrome driver
                self.ChangeStatus('Relaunching chrome driver to attempt to fix lag problems')
                self.t_driver.close()
                self.t_driver = None
            
            if self.t_driver == None: #Check if webdriver isn't running
                self.t_driver = webdriver.Chrome(executable_path=self.runLoc+"Drivers/chromedriver.exe", options=driverOptions) #Start the webdriver back up
            
            if self.accountsCreated >= self.maxAccounts: #Exit the bot if the account count hits the max accs
                self.ChangeStatus("Finished creating the allocated number of accounts...")
                self.t_driver.close()
                self.running = False
                return

            if self.accountsCreated % 100 == 0 and self.accountsCreated > 0: ##Every 100 accounts created the resetCount gets set to 0
                resetCount = 0
            
            if resetCount > 6: #If we have relaunched chrome more than 6 times then we will quit out of the bot
                self.t_driver.close()
                self.ChangeStatus('Relaunched chrome too often, thread will be closed...')
                self.running = False
                return
            elif resetCounter > 6: ##If we have failed to create an account more than 6 times in a row then relaunch chrome
                resetCounter = 0
                resetCount += 1
                self.t_driver.close()
                self.t_driver = None
                continue
            elif resetCounter > 0: ##If the reset counter is above 0 then we must have failed recently so increment the fail count
                self.failedAccounts += 1

            gender: int = randint(0, 2) ## 0 = Male; 1 = Female
            lookingFor: int = randint(0, 2) ## 0 = Male; 1 = Female

            name: Tuple[str, str] = self.GenName(firstNamesList, lastNamesList) ##Generate and store the accounts name

            #Variables to store the accounts first and last name
            firstName: str = name[0]
            lastName: str = name[1]

            email: str = self.GenEmail(name) #Generate and store the accounts email address
            password: str = self.GenPassword(passwordList) #Generate and store the accounts password

            self.ChangeStatus(f"Navigating to url '{url}'")

            try:
                self.t_driver.get(url) #Navigate to the fake website
            except:
                self.failedAccounts += 1
                continue

            self.ChangeStatus("Choosing gender for the account and the gender to look for...")

            selector: str
            if gender == 0: #Set gender selector to man
                selector = "[for='man']"
            else: #Set gender selector to woman
                selector = "[for='woman']"
            
            if not self.ClickElem(self.t_driver, By.CSS_SELECTOR, selector): #Click the gender
                resetCounter += 1
                continue #If it fails restart the loop

            if lookingFor == 0: #Set the looking for gender selector to man
                selector = "[for='lookingMan']"
            else: #Set the looking for gender selector to woman
                selector = "[for='lookingWoman']"

            if not self.ClickElem(self.t_driver, By.CSS_SELECTOR, selector): #Click the looking for gender
                resetCounter += 1
                continue #if it fails restart the loop
            
            sleep(0.500)

            if not self.ClickElem(self.t_driver, By.CSS_SELECTOR, "[class='next-step-btn vb-nextstep-unique-class']"): #Click the next button (literally the only time we can use it)         
                resetCounter += 1
                continue #If it fails restart the loop

            self.ChangeStatus("Choosing the birthday and name of the account...")

            if not self.SelectDropDownOption(self.t_driver, By.ID, "day", option=randint(1,20)): #Try to select a random day
                resetCounter += 1
                continue #Reset bot if it fails

            if not self.SelectDropDownOption(self.t_driver, By.ID, "month", option=randint(1,12)): #Try to select a random month
                resetCounter += 1
                continue #Reset bot if it fails

            if not self.SelectDropDownOption(self.t_driver, By.ID, "year", strOption=str(randint(1921,2000))): #Try to select a random year
                resetCounter += 1
                continue #Reset bot if it fails

            if not self.WriteTextToElem(self.t_driver, By.ID, "firstname", f"{firstName} {lastName}"): #Try to write the accounts name
                resetCounter += 1
                continue #Reset bot if it fails
            
            sleep(1) #Wait to ensure the name is written

            if not self.WriteTextToElem(self.t_driver, By.ID, "firstname", Keys.RETURN, _clear=False): #Try to progress to the next page
                resetCounter += 1
                continue #Reset bot if it fails
            
            sleep(1)

            self.ChangeStatus("Accepting the terms of service and choosing an email and password for the account...")

            if not self.ClickElem(self.t_driver, By.CLASS_NAME, "terms-input"): #Try to accept the terms of service
                resetCounter += 1
                continue #Reset bot if it fails

            if not self.WriteTextToElem(self.t_driver, By.ID, "email", email): #Try to write the email to the email text field
                resetCounter += 1
                continue #Reset bot if it fails

            sleep(0.500) #Wait to ensure it is written correctly

            if not self.WriteTextToElem(self.t_driver, By.ID, "password", password): #Try to write the password to the password text field
                resetCounter += 1
                continue #Reset bot if it fails

            sleep(0.500) #Wait to ensure the text is written correctly

            if not self.WriteTextToElem(self.t_driver, By.ID, "password", Keys.RETURN, _clear=False): #Try to progress to the next page
                resetCounter += 1
                continue #Reset bot if it fails

            self.ChangeStatus("Waiting for success...")

            if self.WaitForElementToLoad(self.t_driver, By.CSS_SELECTOR, "[class='content welcome']"):
                self.accountsCreated += 1 #Increment the accounts created by 1

                self.ChangeStatus("Finished creating account! Signing out of the account now...")

                accInfo: str = f"{firstName} | {lastName} | {email} | {password}\n\n" #Store the account information

                self.ChangeStatus("Writing account information to file...")

                while True:
                    try:
                        with open(self.runLoc+"DatingAccs.txt", "a+") as f:
                            f.write(accInfo)
                            break
                    except:
                        continue

                sleep(1) #Wait 1 sec to ensure the page is read

                try:
                    self.t_driver.get("https://amourfeel.com/") #Navigate to the dating site homepage
                except:
                    resetCounter = 10
                    continue

                self.ChangeStatus("Trying to sign out of account...")

                if self.WaitForElementToLoad(self.t_driver, By.CLASS_NAME, "prof_photo"): #Wait for the profile button to appear
                    attempts: int = 0
                    soAttempt: int = 0

                    reset: bool = False

                    while True:
                        if not self.ClickElem(self.t_driver, By.CLASS_NAME, "prof_photo"): #Wait for the profile button to appear
                            if not self.ClickElem(self.t_driver, By.CLASS_NAME, "popup_close", timeOut=30): #Try to close the annoying popup
                                if attempts == 2:
                                    reset = True
                                    break
                                attempts += 1
                                continue
                        
                        if not self.ClickElem(self.t_driver, By.CLASS_NAME, "so", timeOut=10): #Try to click the sign out button
                            if soAttempt == 2:
                                reset = True
                                break
                            soAttempt += 1
                            continue

                        break

                    if reset:
                        resetCounter = 10
                        continue
                else: #If it fails to load force a chrome relaunch
                    resetCounter = 10
                    continue

                self.ChangeStatus("Signed out of account, restarting bot now...")

                if self.WaitForElementToLoad(self.t_driver, By.CLASS_NAME, "bt_si"): #If it logs out then set the reset count back to 0 and restart the loop
                    resetCounter = 0
                else: #If it fails then force a chrome relaunch
                    resetCounter = 10
                    continue


class Program:
    #Function called when class is created
    def __init__(self):
        while True:
            system('cls')
            print("Welcome to the Site Login Tester\n\n")

            print("Choose the website: \n\n")

            print("1. AmourFeels (cpafeels.com)\n")

            print("0. Exit\n\n")

            website = input("Please select a website to test: ").replace(" ", "")

            if website == "1": ##Check if the user wants to test the fake dating site
                self.DatingSiteOptions()
                break
            elif website == "0": #Check if the user want to quit
                break
            else:
                input("\nIncorrect website selected, hit ENTER/RETURN to continue...")

    #Function used to display information about the creator threads
    def DisplayThreadInfo(self, accountsCreated: int, failedAccounts: int, botStatus: List[str] = None):
        system('cls')

        print("Accounts Created: " + str(accountsCreated)) #Display how many accounts have been created
        print("Failed Accounts: " + str(failedAccounts)) #Display how many accounts have failed to be created

        if botStatus != None: #Display thread statuses
            i = 0
            for status in botStatus:
                i += 1
                print(f"\nBot {i} Status: {status}")
    
    def DisplayDatingTitle(self): #Display the dating site title
        system('cls')
        print("Amour Feels Setup\n\n")
    
    #Function to setup the dating site creator thread
    def DatingSiteCreatorThreadSetup(self, threads: int = 2, accounts: int = 1000):
        threadInfo: List[GoodStuff] = []
        threadsList: List[Thread] = []
        for _ in range(0, threads): #Create the amount of threads desired
            goodStuff: GoodStuff = GoodStuff(accounts/threads)
            t: Thread = Thread(target=goodStuff.DatingSiteCreatorThread, args=(True, False))

            threadsList.append(t)

            goodStuff.ChangeStatus("Launching thread...")
            t.start()
            goodStuff.running = True
            threadInfo.append(goodStuff)
        
        t_running: int = -1

        while t_running != 0:
            t_running = 0

            accountsCreated: int = 0
            failedAccounts: int = 0
            threadStatus: List[str] = []

            for g in threadInfo:
                if (g.running):
                        t_running += 1
                accountsCreated += g.accountsCreated
                failedAccounts += g.failedAccounts
                threadStatus.append(g.threadStatus)

            self.DisplayThreadInfo(accountsCreated, failedAccounts, botStatus=threadStatus)

            sleep(1)

        input('Hit ENTER/RETURN to continue...')
        _exit()
    
    #Function to allow the user to setup the dating site creator
    def DatingSiteCreatorSetup(self):
        while True: #Thread setting loop
            self.DisplayDatingTitle()

            threads: str = input("How many threads do you wish to use: ")

            if not threads.isnumeric:
                self.DisplayDatingTitle()

                print("\nPlease input a valid amount of threads to be used...")
                input("\nHit ENTER/RETURN to continue...")
                continue
            else:
                break
        
        while True: #Account setting loop
            self.DisplayDatingTitle()

            accounts: str = input("How many accounts do you wish to make: ")

            if not accounts.isnumeric: #Check if accounts is not a number
                self.DisplayDatingTitle()

                print("\nPlease input a valid amount of accounts to be created...")
                input("\nHit ENTER/RETURN to continue...")
                continue
            elif int(accounts) > 1000: #Check if user is trying to spam site too much
                self.DisplayDatingTitle()

                print("\nThis software is inteded for demo purposes, you cannot create more than 10 accounts at a time")
                input("\nHit ENTER/RETURN to continue....")
                continue
            else:
                break
        
        self.DisplayDatingTitle()

        print("Launching login info creator threads...")
        sleep(1.5)

        self.DatingSiteCreatorThreadSetup(int(threads), int(accounts))

    #Function used to show the user the options available for the fake dating site
    def DatingSiteOptions(self):
        while True:
            self.DisplayDatingTitle()

            print("1. Login Info Creator\n")
            print("0. Exit\n\n")

            choice: str = input("Choose what to test: ").replace(" ", "")
            
            if choice == "1": #Check if the user has selected the login info creator
                self.DatingSiteCreatorSetup()
                break
            elif choice == "0": #Check if the user has gone back
                break
            else: #Check if the user has failed to input the correct choice
                input("Invalid choice selected, hit ENTER/RETURN to continue...")
                continue
        
    

if __name__ == '__main__':
    p = Program()