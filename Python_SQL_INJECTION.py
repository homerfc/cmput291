import  cx_Oracle	
con = cx_Oracle.connect("ORACLEUSERNAME","ORACLEPASSWORD","gwynne.cs.ualberta.ca:1521/CRS")
print("CONNECTED!")
curs = con.cursor()
#SQL INJECTION EXAMPLE

USERNAME="usr1"
PASSWORD="WrongPass"

#WHEN HACKER CHANGES THE PASSWORD INPUT PARAM
PASSWORD="a' or '1'='1"

QUERY="select * from LOGIN  where username='"+USERNAME+"' and password='"+PASSWORD+"'"
print(QUERY)
curs.execute(QUERY)
CNT =len(curs.fetchall())
print("curs.count= "+str(CNT))
if (CNT>0):
        print("LOGGED IN")
else:
        print("INCORRECT USER PASS")

curs.close()
con.close()
print("CONNECTION CLOSED.")
