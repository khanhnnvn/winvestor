"""Open an facebook public post, click to show the comments section
continue click until there is no more comment to show.

Take all the email address from all the comments in comment section.
"""


from selenium import webdriver
from bs4      import BeautifulSoup as BS
from time     import sleep
import re


url = "https://www.facebook.com/thang.levan.37/posts/1654600631279006"


print("[*] Openning PhantomJS as web browers...")
br  = webdriver.PhantomJS()
print("[!] Done!")
sleep(0.2)
print("[*] Getting Facebook post...")
br.get(url)
print("[!] Done!")
sleep(0.2)
print("[*] Start loading comments...")
br.find_element_by_xpath("//span[@class='_2u_j']").click()
sleep(1)


while True:
    try:
        print("> Checking comments...")
        br.find_element_by_xpath("//a[@class='UFIPagerLink']").click()
        sleep(1)
    except:
        ###until there is no more xpath to click###
        print("[!] Done!")
        break


resp    = BS(br.page_source, "html.parser")
matches = resp.findAll("span", attrs = {"class": "UFICommentBody"})


f       = open("email.txt", "w")


for match in matches:
    email     = re.findall("<span>.*?([A-Za-z0-9.]+@[A-Za-z.]+).+?</span>", str(match))
    if email != []:
        f.write(email[0].lower() + "\n")


f.close()
