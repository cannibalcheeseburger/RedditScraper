from gtts import gTTS

o = 0
text = ""
for s in range(5):
    text = text+"\nStory "+str(s+1)+"\n" + scraper.posts[s+2].content
#text = scraper.posts[1].content
MAXLIM = 10000
rounds = int(len(text)/MAXLIM)+1 if len(text)>MAXLIM else 1
for i in range(rounds):
    mytext = text[i*MAXLIM:(i+1)*MAXLIM]
    language = 'en'  
    myobj = gTTS(text=mytext, lang=language, slow=False)
    myobj.save("stories/"+str(o)+".mp3")
    print(o)
    o = o+1

