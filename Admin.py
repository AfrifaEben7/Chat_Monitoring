import time
from collections import Counter
from string import punctuation
from tkinter import messagebox
from typing import List, Any

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
var_decision = False
stemmer = SnowballStemmer("english")

with open('flagegedwords', 'r') as file:
    file = file.read().split()

nlist = [stemmer.stem(word.lower()) for word in file]

new = ['u', 'ok', 'hahaha', 'haha', 'please', 'k', 'n', 'kk','pls','cn','gm']


def monitor(list, users):

    stoplist = stopwords.words('english')

    newlist = [word for word in list if word.strip(punctuation) not in stoplist and word not in new]

    rippedwords = [stemmer.stem(word) for word in newlist]  # type: List[Any]

    counter = Counter(rippedwords)
    top_three = counter.most_common(3)

    try:
        suspicion =[]
        if ((top_three[0][1] / len(rippedwords))*100)>= 10:
            for x in top_three:
                if x[0] in nlist:
                    suspicion.append(x[0])
        if suspicion:
                    print((time.ctime(time.time())))
                    print('###################################################')
                    print("|---- Chat Room -->",users)
                    print('Suspicion Raised --->',suspicion)
                    var_decision = True
                    print(len(rippedwords),'words in chat room')
    except Exception as e:
        print()
