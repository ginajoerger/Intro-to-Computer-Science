# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 11:38:58 2014

@author: zzhang
"""
import pickle

class Index:
    def __init__(self, name):
        self.name = name
        self.msgs = [];
        self.index = {}
        self.total_msgs = 0
        self.total_words = 0
        
    def get_total_words(self):
        return self.total_words
        
    def get_msg_size(self):
        return self.total_msgs
        
    def get_msg(self, n):
        return self.msgs[n]
        
    def add_msg(self, m):
        self.msgs.append(m)
        self.total_msgs = self.total_msgs + 1
        
    def add_msg_and_index(self, m):
        self.add_msg(m)
        line_at = self.total_msgs - 1
        self.indexing(m, line_at)

    def indexing(self, m, l):
        strung = m.split()
        for i in range(len(strung)):
            if strung[i] not in self.index:
                self.index[strung[i]] = []
                self.index[strung[i]].append(l)
            else:
                self.index[strung[i]].append(l)
                     
    def search(self, term):
        msgs = []
        for i in self.index:
            if term.lower() == i.lower():
                for x in self.index[i]:  
                    msgs.append((x, self.msgs[x].rstrip().lstrip()))
        return msgs

class PIndex(Index):
    def __init__(self, name):
        super().__init__(name)
        roman_int_f = open('roman.txt.pk', 'rb')
        self.int2roman = pickle.load(roman_int_f)
        roman_int_f.close()
        self.load_poems()
        
    def load_poems(self):
        a = open(self.name, 'r')
        for i in a:
            self.add_msg_and_index(i)
    
    def get_poem(self, p):
        poem = []
        poemnumber = self.int2roman[p]+'.'
        z = self.search(poemnumber)
        a = int(z[0][0])
        linenumber = 0
        while self.msgs[linenumber+5].rstrip() != '':
            poem.append(self.msgs[a + linenumber].rstrip())
            linenumber += 1
        return poem
    
if __name__ == "__main__":
    sonnets = PIndex("AllSonnets.txt")
    # the next two lines are just for testing
    p3 = sonnets.get_poem(3)
    s_love = sonnets.search("love")