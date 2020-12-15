# -*- coding: utf-8 -*-
"""
Created on Tue Dec  14 19:45:03 2020

@author: Uwe
"""

from bs4 import BeautifulSoup
import requests, time, getpass


class Crawler():
    
    def __init__(self, url=None, max_price=None, sleep_time = 40, alert_by_mail=False):
        """Constructor"""
        self.PREFIX_ = "https://www.heise.de/preisvergleich/"
        
        if max_price is None:
            max_price = int(input("Maximum price (as integer):"))
        if max_price <= 0:
            raise ValueError(f"Maximum price value ({max_price}) is set to zero or lower.")
        self.MAX_PRICE_ = max_price
        
        if url is None:
            url = input("URL to crawl:")
        if not url.startswith(self.PREFIX_):
            raise ValueError(f"Given URL ({url}) is not a URL from Heise Preisvergleich.")
        self.URL_ = url
        
        if sleep_time <= 0:
            raise ValueError("Sleep time between requests is set to zero or lower.")
        self.SLEEP_TIME_ = sleep_time
        
        self.ALERT_MAIL_ = alert_by_mail
        if self.ALERT_MAIL_:
            # only implemented for gmail
            self.USERNAME_ = input("Gmail Username:")
            self.PASSWORD_ = getpass.getpass("Password:")
            pass
        self.FOUND_MATCH_ = False
    
    def crawl(self):
        """Crawl given URL once and look whether an offer lower or equal to MIN_PRICE_ is found
        If such an offer is found, send email notification."""
        
        while not self.FOUND_MATCH_:
            
            # get page data
            session = requests.session()
            response = session.get(self.URL_)
            session.close()
            
            # check for server errors
            response.raise_for_status()
            
            #.gh_price
            
            soup = BeautifulSoup(response.text, "lxml")
            
            
            itemPriceClasses = soup.find_all("span", {"class": "gh_price"})
            itemPrices = [float(item.find_all("span", "notrans")[0]
                                .text[2:]
                                .replace(",", "."))
                          for item in itemPriceClasses]
            
            try:
                min(itemPrices)
            except: 
                time.sleep(self.SLEEP_TIME_)
                continue
            
            if min(itemPrices) < self.MAX_PRICE_:
                # match found -> alert with link
                self.FOUND_MATCH_ = True
                
                indexes = [idx for idx, price in enumerate(itemPrices) if price < self.MAX_PRICE_]
                prices = [round(itemPrices[i], 2) for i in indexes]
                itemClasses = soup.find_all('a', class_='productlist__link')
                # get names
                itemNames = [item.find_all("span", "notrans")[0]
                             .text[1:-1] 
                             for item in itemClasses]

                # get links as well
                itemLinks = [self.PREFIX_ + item["href"] for item in itemClasses]
                
                # filter for matches
                itemNames = [itemNames[idx] for idx in indexes]
                itemLinks = [itemLinks[idx] for idx in indexes]
    
                print(f"Found {len(indexes)} matches with prices lower than {self.MAX_PRICE_}:\n")
                for idx, (price, name, link) in enumerate(zip(prices, itemNames, itemLinks)):
                    print(f"\t{idx+1}:\t{name} with a price of {price}.")
                    print(f"\t\t{link}\n")
                    
                if self.ALERT_MAIL_:
                    import smtplib, email
                    
                    try:
                        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                        msg = email.message.EmailMessage()
                        
                        msg["Subject"] = "Heise Preisvergleich Match"
                        msg["From"] = self.USERNAME_
                        msg["To"] = self.USERNAME_
                        body = f"Found {len(indexes)} matches with prices lower than {self.MAX_PRICE_}€:\n"
                        for price, name, link in zip(prices, itemNames, itemLinks):
                            body = body + f"\t{name} with a price of {price}€.\n"
                            body = body + f"\t{link}\n\n"
                        msg.set_content(body)
                        server.login(self.USERNAME_, self.PASSWORD_)
                        server.send_message(msg)
                        server.quit()
                    except:
                        print("Failed to send mail.")
                    
                    pass
                
                
            else:
                # wait 15 seconds until next request
                time.sleep(self.SLEEP_TIME_)
