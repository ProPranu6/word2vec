# -*- coding: utf-8 -*-
"""myword2vec

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vFKudErQ0tLqjkVrZO0YoSJKE9WLVqNR
"""



# Commented out IPython magic to ensure Python compatibility.
#!pip install wikipedia
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Activation, Input, Dot, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
from tensorflow.keras.datasets import imdb
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.manifold import TSNE
import wikipedia
import matplotlib.pyplot as plt
import pandas as pd
import copy
from math import *
from scipy.special import softmax
#%matplotlib inline
def prerequisites():
  print("Pre Requisites To Run 'myword2vec.py':\n Install :\n 1.wikipedia")
prerequisites()

def exampleWorkFlow():
  flow = """vecM = vecK("MineVectorizer")

  MineVectorizer Corpus Creation : 
  corpus1, corpus2 = vecM.makeCorpus(title= "guitar")


  MineVectorizer Model Description :
  modelalt, inputDict = vecM.makeModelAndInput(40, corpus2, window=25, negativeSampling=5)


  MineVectorizer Model Training : 
  modelalt = vecM.train(epochs=5, learning_rate=0.009)

  MineVectorizer Suggestions :
  choices = vecM.autoFillList(word1="guitar", topN=20, printList=True)

  MineVectorizer Visualisations :
  vecM.visualiseWordVec(targetDimensions=2, vecCount=100)

  MineVectorizer Summarizations :
  summary = vecM.summarizeCorpus(summaryTagChoices=3, summarizeEvery=2030)

  MineVectorizer Text Calculations :
  matchingWordsAndScores,  calculatedVector = vecM.textCalc(word1="sound", op1="+", word2="vibrates", op2="+", word3="instrument")
  """

  print("\n\nExample Work Flow Of Methods In 'myword2vec.py' : \n\t" + flow)
exampleWorkFlow()
class vecW2V():
    


  def __init__(self, modelName):
    self.model = None
    self.probLayer = None
    self.modelName = modelName
    self.modelInputDict = None
    self.modelVecSize = None
    self.modelCorpus = None
    self.modelVocab = None
    self.modelLinedVocab = None
    self.modelWordVectors = None
    self.freqDict = None

  def removeEle(self, li, ele):
    l = li
    try:
        while True:
            l.remove(ele)
    except ValueError:
        pass
    
    return l
    
  class helperFormat():
    
    def __init__(selfi):
      return
    
    def removeEle(selfi, li, ele):
      l = li
      try:
        while True:
            l.remove(ele)
      except ValueError:
        pass
    
      return l
    
    def removeStopWords(selfi, senList):
      
      noUseWords = stopwords.words('english')
      newSenList = []
    
      for lines in senList :
        
        words = copy.deepcopy(lines.split(" "))
        for nouse in noUseWords:
          if nouse in lines.split(" "):
           
            words = selfi.removeEle(words, nouse)
      
        newSenList.append(" ".join(words))
      
      return newSenList
  
  def uniquefy(self, seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
  


  def makeCorpus(self, title=None, fromText=None):
    
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''

    if fromText == None:
      titlePage = wikipedia.page(title)
      corpus = (titlePage.content).lower()
  
    else:
      corpus = fromText.lower()


    corpus = re.sub(r'==.*?==+', '', corpus)
    corpus = re.sub(r'[,;:\-\(\)\]\[\$%&\*_!<>@#"]','', corpus)
    corpus1 = re.sub(r'\n',' ', corpus)
    corpus2 = re.split(r'\.\s', corpus1)
    
    self.modelCorpus = corpus1

    return corpus1, corpus2


  def setFreqs(self):
    data = []
    freqDict = dict()
    for lis in self.modelLinedVocab.values():
      data += lis
    for vwds in self.modelVocab:
      freqDict[vwds] = data.count(vwds)
    
    self.freqDict = freqDict
    return "DONE"
    

    
  def generateSamplingDistribution(self, li, iterations=10):
    
    le = [self.modelVocab[x] for x in li]
    probDict = dict()
    totalFreqs = sum(list(self.freqDict.values()))
    for wds in le:
      probDict[wds] = (self.freqDict[wds])**0.75/(totalFreqs)**0.75
    
    pickUpList = []
    
    for wdi in li: 
      pickUpList += [wdi for x in range(ceil(probDict[self.modelVocab[wdi]]*iterations))]
    
    return pickUpList 


  def makeInputData(self, corpusSen, window, negativeSampling = 0.4, allowStopWords = False):
  
    global enc
    noUseWords = stopwords.words('english')
    togetherData = []

    vocab = []
    vocabLineWise = dict()
    lineCount = 0
    for lines in corpusSen :
      lines = re.sub("((\s+)\s)"," ", lines)
      lines = re.sub("^(\s+)|(\s+)$|","", lines)
      words = lines.split(" ")
      vocab += words
      vocabLineWise[lineCount] = words
      lineCount += 1
    
    vocab = self.uniquefy(vocab)
    if allowStopWords == False:
      for nouse in noUseWords:
        if nouse in vocab:
          vocab = self.removeEle(vocab, nouse)
    
    
    enc = OneHotEncoder(sparse=False)
    enc.fit(np.array(vocab).reshape(-1,1))

 
    for l in range(lineCount):
      temp = copy.deepcopy(vocabLineWise[l])
      for wds in vocabLineWise[l]:
      
        if wds not in vocab:
          
          temp = self.removeEle(temp, wds)
        
      vocabLineWise[l] = temp
      
    self.modelVocab = vocab
    self.modelLinedVocab = vocabLineWise
    _ = self.setFreqs()
  
    biggerOffSet = 0
    for sen in range(lineCount):
      xinputraw = vocabLineWise[sen]
    
      for c in range(len(xinputraw)):
        centreWord = xinputraw[c]

        contentIndices = range(max(0,c-window), min(len(xinputraw), c+window+1))
        negativecount = int(negativeSampling)
        candids = list(set(range(0, len(vocab))) - set(range(max(0+biggerOffSet,biggerOffSet + c-window), min(len(xinputraw)+biggerOffSet,biggerOffSet+c+window+1))))
        candids = self.generateSamplingDistribution(candids, iterations=window)

       
        if len(candids) == 0:
          noncontentIndices = [-1]
        else:
          noncontentIndices = random.choices(candids, k=negativecount)

        for pick1 in contentIndices :
          contextWord = xinputraw[pick1]
          togetherData.append((centreWord, contextWord, 1))
      
        for pick2 in noncontentIndices :
          if pick2 == -1 :
            continue
          noncontextWord = vocab[pick2]
          togetherData.append((centreWord, noncontextWord, 0))

        biggerOffSet += (len(xinputraw)-1)

    centreWordsAlone = []
    maybecontextWordsAlone = []
    similarity = []
    for dp in togetherData :
      centreWordsAlone.append(dp[0])
      maybecontextWordsAlone.append(dp[1])
      similarity.append(dp[2])
  
    xinput1 = enc.transform(np.array(centreWordsAlone).reshape(-1,1)).T
    xinput2 = enc.transform(np.array(maybecontextWordsAlone).reshape(-1,1)).T
    ylabel = np.array(similarity).reshape(1,-1)



    return xinput1, xinput2, ylabel, enc

  def makeModelAndInput(self, vecSize, corpus2, window=15, negativeSampling=5, allowStopWords=False, describeModel=True):
    
    corpusSen = corpus2
    xinput1, xinput2, ylabel, encoderObject= self.makeInputData(corpusSen, window=window, negativeSampling=negativeSampling, allowStopWords=allowStopWords)

    outputsize = ylabel.shape[0]
    xinput1 = xinput1.T
    xinput2 = xinput2.T
    ylabel = ylabel.T  #(None, 1)


    Xinp1 = Input(shape=(xinput1.shape[1],))
    Xinp2 = Input(shape=(xinput2.shape[1],))

    embed = Dense(vecSize, use_bias=False, name="embed")
    V1 = embed(Xinp1)
    V2 = embed(Xinp2)
    dot = Dot(axes=1)([V1, V2])
    prob = Dense(1, activation='sigmoid', name="prob")(dot)
  
    model = Model(inputs=[Xinp1, Xinp2], outputs=prob)
    self.model = model
    self.probLayer = self.model.get_layer('prob')
    if describeModel == True:
      model.summary()
    
    inputDict = {"Input1":xinput1, "Input2":xinput2, "ylabel":ylabel}
    
    self.modelInputDict = inputDict
    self.modelVecSize = vecSize

    return model, inputDict

  def train(self, learning_rate=0.0009, metrics=["accuracy"], batch_size =32, epochs=100):
    model = self.model
    model.compile(optimizer=Adam(learning_rate=learning_rate), loss="binary_crossentropy", metrics=metrics)
    model.fit(x=[self.modelInputDict["Input1"], self.modelInputDict["Input2"]], y=self.modelInputDict["ylabel"], batch_size=batch_size, epochs=epochs, verbose=2)

    self.model = model
    self.probLayer = self.model.get_layer('prob')
    _ = self.describeWordVecs()

    return model
    
  def Sort_Tuple(self, tup): 
      
    # getting length of list of tuples
    lst = len(tup) 
    for i in range(0, lst): 
        for j in range(0, lst-i-1): 
            if (tup[j][1] < tup[j + 1][1]): 
                temp = tup[j] 
                tup[j]= tup[j + 1] 
                tup[j + 1]= temp 
    return tup 

  def sig(self, x):
    z = 1/(1 + np.exp(-x))
    return z

  def describeWordVecs(self):
    
    vectorizedWords = []
    for vectors in range(self.modelInputDict["Input1"].shape[1]):
      vectorizedWords.append(self.model.weights[0][vectors,:])
    
    vectorizedWords = np.array(vectorizedWords)

    self.modelWordVectors = vectorizedWords
    return vectorizedWords

  def autoFillList(self, word1=None, word2=None, topN=None,  printList=False):
    
    vectorizedWords = self.modelWordVectors
    originWord1 = enc.transform(np.array([word1]).reshape(-1,1))
    if word2 != None:
      originWord2 = enc.transform(np.array([word2]).reshape(-1,1))
      embedWord1 = np.dot(originWord1, vectorizedWords) 
      embedWord2 = np.dot(originWord2, vectorizedWords)
      print(embedWord1.shape, embedWord2.shape)
      matches = np.dot(embedWord1, embedWord2.T)
      den = np.linalg.norm(embedWord1)*np.linalg.norm(embedWord2)
      matches = matches/den
    
      reqProbs = matches
      if printList == True:
        print(*reqProbs[0])


      return reqProbs
    else:
      embedWord = np.dot(originWord1, vectorizedWords)
  
      matches = np.dot(tf.keras.utils.normalize(embedWord), tf.keras.utils.normalize(vectorizedWords).T)
  
      reqMatches = np.flip(np.argsort(matches))[0,0:topN]

      reqProbs = np.flip(np.sort(matches))[0,0:topN]

      originWord2 = np.zeros((self.modelInputDict["Input1"].shape[1],1))
      count = 0
      result = []
      for vindex in reqMatches :
        originWord2[vindex,0] = 1
    
        result.append((enc.inverse_transform(np.array([originWord2]).reshape(1,-1))[0,:], reqProbs[count]))
        if printList == True:
          print(enc.inverse_transform(np.array([originWord2]).reshape(1,-1)), reqProbs[count])
        count += 1
        originWord2[vindex,0] = 0


      return result

  def textCalc(self, printList=True, topN=10, **kwargs):
    vectorizedWords = self.modelWordVectors
    resultantVec = 0
    opCache = "+"
    vectorCount = 0
    if vectorizedWords.all() == None:
      return "No Vector Lookup Given"
    else :
      for keys, vals in kwargs.items():
      
        if "word" in keys:
          currentWord = enc.transform(np.array([vals]).reshape(-1,1))
          currentWord = np.dot(currentWord, vectorizedWords) 
          vectorCount +=1

          resultantVec = eval("resultantVec " + opCache + " currentWord")
        else :
          opCache = vals
    
      matches = np.dot(tf.keras.utils.normalize(resultantVec), tf.keras.utils.normalize(vectorizedWords).T)
  
      reqMatches = np.flip(np.argsort(matches))[0,0:topN]

      reqProbs = np.flip(np.sort(matches))[0,0:topN]

      originWord2 = np.zeros((self.modelInputDict["Input1"].shape[1],1))
      count = 0
      result = []
      for vindex in reqMatches :
        originWord2[vindex,0] = 1
    
        result.append((enc.inverse_transform(np.array([originWord2]).reshape(1,-1))[0,:], reqProbs[count]))
        if printList == True:
          print(enc.inverse_transform(np.array([originWord2]).reshape(1,-1)), reqProbs[count])
        count += 1
        originWord2[vindex,0] = 0


      return result, resultantVec

  def summarizeCorpus(self, summaryTagChoices = 3, summarizeEvery = 10, printTags = True):

    vectorizedWords = self.modelWordVectors
    filteredWds = self.modelVocab
    resultantVec = 0
    taggedContent = []
    contentNum = 0
    preWd = 0
    if vectorizedWords.all() == None:
      return "No Vector Lookup Given"
    else :
      for wds in range(len(filteredWds)):
      
        if filteredWds[wds] != "*" or filteredWds[wds] != "":
          currentWord = enc.transform(np.array([filteredWds[wds]]).reshape(-1,1))
          currentWord = np.dot(currentWord, vectorizedWords) 

          resultantVec += eval("currentWord")
        
        
        else :
          continue
      
        if (wds+1)%summarizeEvery == 0:

        
          matches = np.dot(tf.keras.utils.normalize(resultantVec/summarizeEvery), tf.keras.utils.normalize(vectorizedWords).T)
          reqMatches = np.flip(np.argsort(matches))[0,0:summaryTagChoices]
          reqProbs = np.flip(np.sort(matches))[0,0:summaryTagChoices]

          originWord2 = np.zeros((self.modelInputDict["Input1"].shape[1],1))
          count = 0
          result = []

          if printTags == True:
            print("Content Number : ", contentNum, "; The Orginial Content : ", " ".join(filteredWds[preWd:wds+1]), "\n")
          for vindex in reqMatches :
            originWord2[vindex,0] = 1
    
            result.append((enc.inverse_transform(np.array([originWord2]).reshape(1,-1))[0,:], reqProbs[count]))
            if printTags == True:
              print(enc.inverse_transform(np.array([originWord2]).reshape(1,-1)), reqProbs[count])
            count += 1
            originWord2[vindex,0] = 0
        
          if printTags == True:
            print("\n")
          contentNum += 1
          taggedContent.append(result)
          resultantVec = 0
          preWd = (wds+1)
      
      return taggedContent
  
  def predictText(self, word1=None, topN=None, printList = True):

    vectorizedWords = self.modelWordVectors
    originWord1 = enc.transform(np.array([word1]).reshape(-1,1))


    embedWord = np.dot(originWord1, vectorizedWords)

    scores =[]
    dots = np.dot(embedWord, vectorizedWords.T)
    
    for d in dots[0,:]:
      d = d.reshape(-1,1)
     
      scores.append(np.array(self.probLayer(d))[0,0])

    scores = np.array(scores)
    
    reqMatches = np.flip(np.argsort(scores))[0:topN]

    reqProbs = np.flip(np.sort(scores))[0:topN]

    originWord2 = np.zeros((self.modelInputDict["Input1"].shape[1],1))
    count = 0
    result = []
    for vindex in reqMatches :
      originWord2[vindex,0] = 1
    
      result.append((enc.inverse_transform(np.array([originWord2]).reshape(1,-1))[0,:], reqProbs[count]))
      if printList == True:
        print(enc.inverse_transform(np.array([originWord2]).reshape(1,-1)), reqProbs[count])
      count += 1
      originWord2[vindex,0] = 0


    return result



  def visualiseWordVec(self, targetDimensions=2, vecCount = None, model = None):

    filteredWds = self.modelVocab
    vectorizedWords = self.modelWordVectors
    labels = []
    tokens = []

    if model == None:

      for wds in range(len(filteredWds)):
      
          if (filteredWds[wds] != "*" or filteredWds[wds] != "" )and (filteredWds[wds] not in labels):
            currentWord = enc.transform(np.array([filteredWds[wds]]).reshape(-1,1))
            labels.append(filteredWds[wds])
            tokens.append(np.dot(currentWord, vectorizedWords)[0]) 
    else:
      
      for word in model.wv.vocab:
        tokens.append(model[word])
        labels.append(word)

    
    #print(tokens[0:2])
    Vtsned = TSNE(n_components=targetDimensions).fit_transform(tokens)

    x = []
    y = []
    for value in Vtsned:
        x.append(value[0])
        y.append(value[1])
        
    plt.figure(figsize=(16, 16))
    if vecCount == None:
      num = len(x)
    else:
      num = vecCount 
    for i in range(num):
        plt.scatter(x[i],y[i])
        plt.annotate(labels[i],
                     xy=(x[i], y[i]),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')
    plt.show()

    return

