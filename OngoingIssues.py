import smtplib
import time
import imaplib
import email
import sys
import re
import csv


ORG_EMAIL   = "@gmail.com"
#omitted for security
#FROM_EMAIL  = "" + ORG_EMAIL
#FROM_PWD    = ""
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

def readmail():
    BankDict = importCountryRegion()
    NameDict = importBankName()
    print(NameDict)
    try:
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)

        mail.select('inbox')

        type, message_numbers = mail.search(None, 'ALL')
        mail_ids = message_numbers[0]

        id_list = mail_ids.split()
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])

        print(message_numbers[0].split())

        for i in message_numbers[0].split():
            try:
                type, data = mail.fetch(i, '(RFC822)' )
                print(data)
                regex(data,BankDict,NameDict)
            except:
                errorOutput(data)

    except:
        print (sys.exc_info()[0])
    finally:
        mail.close()
        mail.logout()

#A function that better formats the regex split function, takes 3 strings, first split position, last split position and the string to be split
def between(a,b, string):
    try:
        temp1 = re.split(a,string)
        out = re.split(b,temp1[1])
        return out[0]
    except:
        return "no value"

def errorOutput(string):
    with open("errorOutput.csv", 'a') as outputfile:
        outputwriter  = csv.writer(outputfile, delimiter=",", quotechar='"',quoting=csv.QUOTE_MINIMAL)
        outputwriter.writerow(string)
        print("error")

    outputfile.close()

def output(array):

    with open("output.csv", 'a', newline='') as outputfile:
        outputwriter  = csv.writer(outputfile, delimiter=",", quotechar='"',quoting=csv.QUOTE_MINIMAL)
        outputwriter.writerow(array)
        print("done")

    outputfile.close()

def importCountryRegion():
    csv_columns = ['SiteID','SiteDisplay', 'CountryName']

    reader = csv.DictReader(open('currentBankIssues.csv', 'r'))
    BankDict = {'key':'value'}

    for row in reader:
        CountryRegion = row.popitem()[1]
        SiteDisplayName = row.popitem()[1]
        DSiteID = row.popitem()[1]
        BankDict[int(DSiteID)] = CountryRegion

    return BankDict

def importBankName():
    csv_columns = ['SiteID', 'SiteDisplay', 'CountryName']
    reader = csv.DictReader(open('currentBankIssues - Copy.csv', 'r'))
    NameDict = {'key':'value'}

    for row in reader:
        CountryRegion = row.popitem()[1]
        SiteDisplayName = row.popitem()[1]
        DSiteID = row.popitem()[1]
        NameDict[int(DSiteID)] = SiteDisplayName

    return NameDict

def fixDate(array):
    UKFormat = (array[1] + "/" + array[0] + "/" + array[2])
    return UKFormat

# TODO region, therefor import csv then search based on siteId, work out which entries should persist and which should be booted and when

def regex(s,BankDict,NameDict):
    array = []

    #This list only works for banks with a single hyphen
    brokenBanks = ['Virgin - Credit Cards(Credit Cards)',
                   'BMO - Online Banking(Banking)',
                   'The Co-operative Bank (new)(Banking)',
                   'TheCo-operativeBank(new)(Banking)',
                   'Best Buy - Credit Cards(Credit Cards)',
                   'Mechanics Bank- credit card(Credit Cards)']

    list = ['element 1', 'element 2', 'element 3']

    bankBroken = False

    #checks for broken bank
    for i in brokenBanks:
        if i in str(s):
            bankBroken = True

    try:
        #split html email string on yodlee email address
        m = re.split('To: customercare@yodlee.com',str(s[0]))
        #prints second element after splitting and removes "\r\nSubject:"
        o = re.split('Subject: ', str(m[1]))
        p = re.split(r'\\r\\n',o[1])
        n = ''.join(p)

        #splits string on " - " and saves bank name
        subject = re.split('-', n)

        if bankBroken == True:
            bankName = subject[0] + "-" + subject[1]
        else:
            bankName = subject[0]

        #print(subject[4])
        tempSent = between('Sent:', '\\\\', n)
        bracksent = between('b> ', '<b', tempSent)
        # removes extra tag leaving a datetime#

        sent = re.split(' \(', bracksent)

        array.append(sent[0])
        array.append(bankName)

        tempimpactedContainer = between('Impacted Container  :  ', 'Impact', n).translate({ord(c): None for c in '='})

        impactedContainer = "na"
        try:
            if "Banking" in tempimpactedContainer:
                impactedContainer = "Banking"
            if "Credit Cards" in tempimpactedContainer:
                impactedContainer = "Credit Cards"
            if "Banking" in tempimpactedContainer and "Credit Cards" in tempimpactedContainer:
                impactedContainer = "Banking/Credit Cards"
        except:
            impactedContainer = "failed"

        array.append(impactedContainer)

        tempStartTime = between('Start Time : ','\\\\', o[1])
        tempTentativeETA =  between('Tentative ETA : ',' \.\\\\', o[1])

        try:
            startTime = fixDate(re.split('/',tempStartTime))
        except:
            startTime = "Invalid Date Format"

        try:
            tentativeETA = fixDate(re.split('/',tempTentativeETA))
        except:
            tentativeETA = "Invalid Date Format"
        array.append(startTime)
        array.append(tentativeETA)

        errorCode = ""
        try:
            errorCode = between('Error Codes  :  ','Impacted Container',n)
        except:
            errorCode = ""
        array.append(errorCode)

        tempimpact = between('Impact : ', '\\\\', o[1])

        arrimpact = re.split('%', tempimpact)
        percentageImpact = arrimpact[0]

        try:
            if (int(percentageImpact) < 34):
                impact = "Low"
            elif (int(percentageImpact) < 67):
                impact = "Medium"
            else:
                impact = "High"
            print (impact)
        except:
            impact = percentageImpact
        array.append(impact)

        #gets the issue type either UAR, technical or site issue
        if bankBroken == True:
            parsedIssueType = subject[2].translate({ord(c): None for c in ' ='})
        else:
            parsedIssueType = subject[1].translate({ord(c): None for c in ' ='})


        #status, either in progress or resolved
        globMes = re.split('Global Message', n)
        tempstatus = re.split('-',globMes[0])
        length = len(tempstatus)
        status = re.split('\[',tempstatus[length-1])

        statusProc = status[0].translate({ord(c): None for c in ' ='})

        #processing for issue type and status, adds spaces and verbatum

        issueType = "#n/a"
        statusOut = "#n/a"
        if("Resolved" in statusProc):
            statusOut =  "Resolved"
            if "TechnicalError" in parsedIssueType:
                issueType = "Technical Error"
            if "UserActionRequired" in parsedIssueType:
                issueType = "UAR Error"
            if "SiteTemporarilyUnavailable" in parsedIssueType or "SiteLayoutChange" in parsedIssueType:
                issueType = "Site Error"
            if "LoginFormChange" in parsedIssueType:
                issueType = "Login Form Change"
        else:
            if "TechnicalError" in parsedIssueType:
                issueType = "Technical Error"
                statusOut = "Users are failing because of a technical issue"
            if "UserActionRequired" in parsedIssueType:
                issueType = "UAR Error"
                statusOut = "Site requires users to take action to continue refresh"
            if "SiteTemporarilyUnavailable" in parsedIssueType or "SiteLayoutChange" in parsedIssueType:
                issueType = "Site Error"
                statusOut = "Site temporarily unavailable"
            if "LoginFormChange" in parsedIssueType:
                issueType = "Login Form Change"
                statusOut = "Site temporarily unavailable"

        array.append(issueType)
        array.append(statusOut)

        tempsiteId = between('Site Id  : ','Impacted Container  :  ',n)

        siteId = re.split('Error Codes',tempsiteId)
        CountryRegion = 'blank'
        AltBankName = 'blank'
        try:
            CountryRegion = BankDict[int(siteId[0])]
        except:
            CountryRegion ='#n/a'

        try:
            AltBankName = NameDict[int(siteId[0])]
        except:
            AltBankName = '#n/a'

        array.append(CountryRegion)
        array.append(siteId[0])
        array.append(tempimpactedContainer)
        array.append(AltBankName)
        array.append(parsedIssueType)

    except AttributeError:
        m = ''
    finally:
        if array[0]!="":
            output(array)

def main():
    output(["Sent","Bank","Container", "StartTime","EndTime","Error Code","Impact","Issue","Status", "CountryRegion","SiteID", "Full Container", "AltBankName", "temp"])

    try:
        readmail()
    except:
        print ("failed")

if __name__ == '__main__':
    main()

