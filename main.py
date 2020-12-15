# -*- coding: utf-8 -*-
"""
Created on Wed Dec  15 20:23:01 2020

@author: Uwe
"""

from heise_preisvgl.crawler import Crawler

c = Crawler("https://www.heise.de/preisvergleich/?cat=gra16_512&xf=9810_16+0020314+-+RTX+3070", 810)

c.crawl()
