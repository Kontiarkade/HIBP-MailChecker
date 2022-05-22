# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Data processsing module
"""

import time
import re
import json

try:
    import requests
except ImportError:
    print ('Requests module required. Please visit https://docs.python-requests.org/en/latest/')

# 1.5 seconds is a minimum safe value
RATE = 1.8

# current HIBP active endpoint
HIBP_ULR = 'https://haveibeenpwned.com/api/v3/breachedaccount/'

# email regexp
REGEX = re.compile(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")


class MailChecker:
    """
    A class for working with emails and handling requests to HIBP
    """
    
    def __init__(self, stream=None, key=None):
        """
        file - file, single email per string, rest is ignored (?)
        string - single string with one or more emails
        """
        self.key = key
        
        self.l = self.parseString(stream, REGEX)
        self.lLen = len(self.l)
        
        self.sleep = RATE

        self.aproxTime = self.lLen * self.sleep
        self.estimatedTime = None

    def parsePayload(self, payload, *args):
        s = ''
        for i in payload:
            for j in args:
                s += str(j) + ': ' + i[j] + '; '
        return s.rstrip('; ')

    def checkAll(self):
        if self.l:
            res = {}
            c = 1
            t = self.lLen
            for i in self.l:
                t -= 1
                status, s, p = self.checkSingleAddress(i)
                res[c] = {'Email':i, 'Status':status, 'Domains':'-'}
                if p: res[c].update(Domains=self.parsePayload(p, 'Domain', 'BreachDate'))
                if s: self.sleep = s
                self.estimatedTime = t * self.sleep
                if i != self.l[-1]:
                    time.sleep(self.sleep) # sleep so that we don't trigger the rate limit
                    c += 1
            return res
        else:
            raise ValueError('No emails found')
        
    def checkSingleAddress(self, email):
        s = None
        p = None
        reqUrl = HIBP_ULR + email + '?truncateResponse=false'
        headers = {
            'hibp-api-key':self.key,
            'user-agent':'MailChecker_Python'
            }
        check = requests.get(
            reqUrl,
            verify=True,
            headers=headers
            )
        if str(check.status_code) == "404": # The address has not been breached.
            status = 'Not breached'
        elif str(check.status_code) == "200": # The address has been breached!
            status = 'Breached'
            p = json.loads(check.text)
        elif str(check.status_code) == "429": # Rate limit triggered
            #TODO
            '''
            logMsg = (
                "[!] Rate limit exceeded, server instructed us to retry after "
                + check.headers['Retry-After']
                + " seconds for email "
                + email
                )
            '''
            s = float(check.headers['Retry-After']) # Read rate limit from HTTP response headers and set local sleep rate
        elif str(check.status_code) == "401": # Wrong api-key
            raise AssertionError('Access denied due to invalid hibp-api-key.')
        else:
            status = 'Error'
            #TODO 
            #logMsg = 'Something went wrong'
        return(status, s, p)

    def parseString(self, s, regex):
        m = regex.finditer(s)
        l = [i.group() for i in m]
        return(l)
    
    #TODO
    #def logger(msg):
    #    pass