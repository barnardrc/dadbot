# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 15:31:40 2024

@author: barna
"""
import regex as re
def test1():
    mystring = '© 6d 23h 45m © 17,899 ©'
    x = mystring.replace(',', '')
    numExpression =r'(.*\D)(\d+)'
    timeExpression = r'( )(6d )(.*m)'
    
    m = re.search(timeExpression, x)
    
    #x = m
    #x = x.strip()
    print(m.group(3))
    
def test2():
    hourMinExpression = r'\d+'
    mystring = '23h 45m'
    timeListedList = []
    
    m = re.findall(hourMinExpression, mystring)
    for item in m:
        m[m.index(item)] = int(item)
        
    timeListed = (60 - m[1]) + (24 - m[0] - 1) * 60
    timeListedList.append(timeListed)

def test3():
    myint = '117800'
    if myint[-2:] == '00' and len(myint) > 5:
        myint = myint[1:]
    print(myint)
        

test3()