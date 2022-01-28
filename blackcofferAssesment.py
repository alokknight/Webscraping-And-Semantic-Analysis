import sre_yield
import pandas as pd
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
import re
import nltk

nltk.download('punkt')
nltk.download("stopwords")
df = pd.read_excel('input.xlsx')
links = [x for x in df['URL']]




with open('StopWords_Generic.txt','r') as f:
    stop_words = f.read()

stop_words = stop_words.split('\n')
print(f'Total count of Stop Words are {len(stop_words)}')

# print(stop_words)

master_dic = pd.read_excel('LoughranMcDonald_MasterDictionary_2020.xlsx')
master_dic.head()

uncertainity = pd.read_excel('uncertainty_dictionary.xlsx')
uncertainity_words = list(uncertainity['Word'])

constraining = pd.read_excel('constraining_dictionary.xlsx')
constraining_words = list(constraining['Word'])

def sentiment(score):
    if(score < -0.5):
        return 'Most Negative'
    elif(score >= -0.5 and score < 0):
        return 'Negative'
    elif(score == 0):
        return 'Neutral'
    elif(score > 0 and score < 0.5):
        return 'Positive'
    else:
        return 'Very Positive'

def remove_stopwords(words, stop_words):
    return [x for x in words if x not in stop_words]


positive_dictionary = [x for x in master_dic[master_dic['Positive'] != 0]['Word']]

negative_dictionary = [x for x in master_dic[master_dic['Negative'] != 0]['Word']]

def countfunc(store, words):
    score = 0
    for x in words:
        if(x in store):
            score = score+1
    return score

def tokenize(text):
    text = re.sub(r'[^A-Za-z]',' ',text.upper())
    tokenized_words = word_tokenize(text)
    return tokenized_words

def positive_score(positive_dictionary,words):
    return countfunc(positive_dictionary, words)

def negative_score(negative_dictionary, words):
    return countfunc(negative_dictionary, words)


def polarity(positive_score, negative_score):
    return (positive_score - negative_score)/((positive_score + negative_score)+ 0.000001)

# SUBJECTIVITY_SCORE = subjectivity(POLARITY_SCORE, NEGATIVE_SCORE, WORD_COUNT)
def subjectivity(positive_score, negative_score, WORD_COUNT):
    return (positive_score+negative_score)/(WORD_COUNT+ 0.000001)

def fog_index_cal(average_sentence_length, percentage_complexwords):
    return 0.4*(average_sentence_length + percentage_complexwords)

def average_number_of_words_per_sentence(total_words,totalsentances):
    return total_words/totalsentances

def syllable_morethan2(word):
    if(len(word) < 2 and (word[-2:] == 'es' or word[-2:] == 'ed')):
        return False
    count =0
    vowels = ['a','e','i','o','u']
    for i in word:
        if(i.lower() in vowels):
            count = count +1
    # print(count)
    if(count > 2):
        return True
    else:
        return False

def word_count(content):
    tokenized_words = tokenize(content)
    #print(f'Total tokenized words are {len(tokenized_words)}')
    words = remove_stopwords(tokenized_words, stop_words)
    WORD_COUNT = len(words)
    return WORD_COUNT

def syllable_count_per_word(words):
    syllables_count =0
    vowels = ['a','e','i','o','u']
    for word in words:
        for i in word:
            if(i.lower() in vowels):
                syllables_count = syllables_count +1

        if(word[-2:] == 'es' or word[-2:] == 'ed'):
            syllables_count = syllables_count - 1

    return syllables_count/len(words)

def count_personal_pronoun(content):
    all_permuted_pronoun = []
    pattern=r'(W|w)(e|E) | (I|i) | (O|o)(U|u)(r|R)(s|S) | (M|m)(Y|y) | (U|u)(S|s)'
    for each in sre_yield.AllStrings(pattern):
        all_permuted_pronoun.append(each)
    # all_permuted_pronoun.remove('US')
    all_permuted_pronoun_copy = all_permuted_pronoun.copy
    all_permuted_pronoun_copy.remove('US')
    # print(all_permuted_pronoun)
    return countfunc(content, all_permuted_pronoun)

def average_word_length(words):
    all_words_length =0
    for word in words:
        all_words_length = all_words_length +len(word)
    return all_words_length/len(words)

df=df.drop(df.loc[ : ,df.columns.difference(['URL_ID', 'URL'])], axis=1)
print(df.columns)


var = [
    'POSITIVE_SCORE',
    'NEGATIVE_SCORE',
    'POLARITY_SCORE',
    'SUBJECTIVITY_SCORE',
    'AVG_SENTENCE_LENGTH',
    'PERCENTAGE_OF_COMPLEX_WORDS',
    'FOG_INDEX',
    'AVG_NUMBER_OF_WORDS_PER_SENTENCE',#
    'COMPLEX_WORD_COUNT',
    'WORD_COUNT',
    'SYLLABLE_PER_WORD',#
    'PERSONAL_PRONOUNS',#
    'AVG_WORD_LENGTH'#
    ]

for v in var[:-1]:
    df[v] = 0.0


def files():
    n = 1
    while True:
        yield open('./allhtml/%d.part' % n, 'w',encoding="utf-8")
        n += 1

fs = files()
outfile = next(fs)
allhtml = []
articles = []
for url in df['URL']:
    session = requests.Session()
    session.headers = {
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.1.2222.33 Safari/537.36",
        "User-Agent": "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.307.11 Safari/532.9",
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }
    r = session.get(url)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    allhtml.append(soup)
    # encodedsoup = soup.encode("utf-8")
    Title = soup.title.get_text()
    Article = soup.find("div", class_= "td-post-content").text
    strr = str(Title) + str(Article)
    articles.append(strr)
    outfile = next(fs)
    outfile.write(str(Title) + str(Article))
    outfile.close()

    textfile = open("allhtml.txt", "w",encoding="utf-8")
    for html in allhtml:
        textfile.write(str(html) + "\n"+"-"*125+"\n" )
    textfile.close()

    articlefile = open("articles.txt", "w",encoding="utf-8")
    for article in articles:
        articlefile.write(str(article) + "\n"+"-"*125+"\n" )
    articlefile.close()

df.head()

for i in range(len(articles)):
    if articles[i]:
        tokenized_words = tokenize(articles[i])
        words = remove_stopwords(tokenized_words, stop_words)
        WORD_COUNT = len(words)
        sentences = sent_tokenize(articles[i])
        SENTANCE_COUNT = len(sentences)
        COMPLEX_WORD_COUNT =0
        SYLLABLE_PER_WORD = 0
        for word in words:
            if(syllable_morethan2(word)):
                COMPLEX_WORD_COUNT = COMPLEX_WORD_COUNT + 1

        df.at[i , 'POSITIVE_SCORE'] = countfunc(positive_dictionary, words)
        df.at[i , 'NEGATIVE_SCORE'] = countfunc(negative_dictionary, words)
        df.at[i , 'POLARITY_SCORE'] = polarity(POSITIVE_SCORE, NEGATIVE_SCORE)
        df.at[i , 'SUBJECTIVITY_SCORE']=subjectivity(POLARITY_SCORE, NEGATIVE_SCORE, WORD_COUNT)
        df.at[i , 'AVG_SENTENCE_LENGTH']=WORD_COUNT/SENTANCE_COUNT
        df.at[i , 'PERCENTAGE_OF_COMPLEX_WORDS']=COMPLEX_WORD_COUNT/WORD_COUNT
        df.at[i , 'FOG_INDEX']=fog_index_cal(AVG_SENTENCE_LENGTH, PERCENTAGE_OF_COMPLEX_WORDS)
        df.at[i , 'AVG_NUMBER_OF_WORDS_PER_SENTENCE']=WORD_COUNT/SENTANCE_COUNT
        df.at[i , 'COMPLEX_WORD_COUNT']=COMPLEX_WORD_COUNT
        df.at[i , 'WORD_COUNT']=WORD_COUNT
        df.at[i , 'SYLLABLE_PER_WORD']=syllable_count_per_word(words)
        df.at[i , 'PERSONAL_PRONOUNS']=count_personal_pronoun(articles[i])
        df.at[i , 'AVG_WORD_LENGTH']=average_word_length(words)

df.to_excel('output.xlsx')