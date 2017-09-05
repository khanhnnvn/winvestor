"""Open an facebook public post, click to show the comments section
continue click until there is no more comment to show.

Take all the email address from all the comments in comment section.

Adding argument parser.
"""


from selenium import webdriver
from bs4      import BeautifulSoup as BS
from time     import sleep
import re
import argparse
import os


emails  = []
path    = os.getcwd()


def getemail(url):
    print("[*] Openning PhantomJS as web browers...")
    br  = webdriver.PhantomJS()
    print("[!] Done!")
    sleep(0.2)
    print("[*] Getting Facebook post...")
    try:
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
        resp          = BS(br.page_source, "html.parser")
        comments      = resp.findAll("div", attrs = {"class": "UFICommentContent"})
        for comment in comments:
            ###print(comment)###
            user      = re.findall('<span class=" UFICommentActorName".+?>(.+?)</span>', str(comment))
            email     = re.findall("<span>.*?([A-Za-z0-9._+-]+@[A-Za-z.]+).*?</span>", str(comment))
            if email != []: emails.append((user[0], email[0]))
    except:
        print("[!] Can\'t get Facebook post address.")
###for match in matches: print(match)### <--- checking other Facebook post, getting comments only --->


def Main():
    parser   = argparse.ArgumentParser(description = "Crawling Facebook post, getting email address in comment section.")
    parser.add_argument("URL", help = "Adding URL to the facebook public post <PC version> I haven\'t check if this also works with mobile version of facebook post yet. But you\'re welcome.")
    parser.add_argument("-s", "--save", help = "Save all the email address getting from URL into <%s/emails.txt>." %path, action = "store_true")
    args     = parser.parse_args()
    result   = getemail(args.URL)
    if args.save:
        f = open("emails.txt", "w")
        for (u,e) in emails: f.write("%s: %s\n" %(u,e.lower()))
        f.close()
    else:
        for (u,e) in emails: print(u + ":" + e)


if __name__ == "__main__":
    Main()
