import requests
import pandas as pd
from const import *
import urllib


class Post:
    def __init__(self,post_json =None,link=None):
        if post_json:
            self.extract_json(post_json)
        if link:
            self.json = requests.get(link+'.json', headers=headers).json()
            self.post_json = self.json[0]['data']['children'][0]
            self.extract_json(self.post_json)
            
    def extract_json(self,post_json):
            self.title= post_json['data']['title']        
            self.ups = post_json['data']['ups']
            self.downs = post_json['data']['downs']
            self.author = post_json['data']['author']
            self.id = post_json['data']['subreddit_id']
            self.subreddit = post_json['data']['subreddit']
            self.content = post_json['data']['selftext']
            self.url = post_json['data']['permalink']
            self.post_json = post_json
            self.is_video = post_json['data']['is_video']        
            try:
                self.pic_url = post_json['data']['url_overridden_by_dest']
            except:
                self.pic_url = None
    
    def download_media(self,gif = False,video = False):
        print(self.short_post())
        try:
            if video:
                self.download_video()
            if self.pic_url:
                file_name = self.pic_url.split("/")[-1]
                if not "." in file_name:
                    return
                if not gif and file_name.split('.')[1]=='gif':
                    return
                self.download_image()
        except:
            print("Error in :",self.title)
            pass


    def download_image(self):
        file_name = self.pic_url.split('/')[-1]
        with open('media/'+file_name, "wb") as f_out:
        #    print("Downloading {}".format(self.pic_url))
            c = requests.get(self.pic_url, headers=headers).content
            f_out.write(c)

    def short_post(self):
        return '\n'+self.title+'\n'+self.content+'\nAuthor: '+self.author+'\nups: '+str(self.ups)+' downs: '+str(self.downs)+'\n'

    def download_video(self):
        if self.is_video:
            vid = self.post_json['data']['secure_media']['reddit_video']['fallback_url']
            urllib.request.urlretrieve(vid, "videos/"+self.title+'.mp4')

    def get_comment(self):
        text = ""
        for comm in self.json[1]['data']['children']:
            text = text+comm['data']['body']
        return text


    def __str__(self):
        return self.short_post()

    def __repr__(self):
        return self.short_post()


class Scraper:
    def __init__(self,subreddit,sort='top',time = 'all',limit=POST_LIMIT):
        if subreddit:
            self.scrape(subreddit,sort,time,limit)
            self.subreddit = subreddit
            self.url = 'www.reddit.com/r/'+subreddit

    def scrape(self,subreddit,sort = 'top',time = 'all',limit=POST_LIMIT):
        url = "https://old.reddit.com/r/"+subreddit+"/"+sort+"/.json?t="+time+"&limit="
        self.posts = []
        if limit<=100:
            url = url+str(limit)
            self.sub_json = requests.get(url, headers=headers).json()
            for post in self.sub_json["data"]["children"]:
                p = Post(post)
                self.posts.append(p) 
        else:
            self.scrape_more(url,limit=limit)
        return self.posts

    def scrape_more(self,url,limit):
        res = limit%100
        rounds = int(limit/100 +1) if limit%100 else limit/100
        count = 0
        lim = 100

        for i in range(int(rounds)):
            url = url+str(lim)+'&count='+str(count)

            count = count+100
            lim = res if i==rounds-2 else 100
            data = requests.get(url, headers=headers).json()
            for post in data["data"]["children"]:
                p = Post(post)
                self.posts.append(p)

        return self.posts

    def download_media(self,gif = False,video=False):
        p = 1
        for post in self.posts:
            print("="*10,'\nPost ',p,'\n')
            post.download_media(gif=gif,video=video)
            p = p+1
    
    def download_video(self):
        for post in  self.posts:
            post.download_video()

    def save_text(self):
        with open('output.txt','w',encoding="utf-8") as f:
            i = 0
            for post in self.posts:
                f.writelines("Story: "+str(i))
                f.writelines(post.short_post())
                f.writelines("="*10)
                i = i+1

    def len(self):
        return len(self.posts)

    def dataframe(self):
        posts = []
        for post in self.posts:
            p = [
                post.id,
                post.title,
                post.content,
                post.author,
                post.subreddit,
                post.url,
                post.ups
            ]
            posts.append(p)
        self.df = pd.DataFrame(posts,columns=dfcolumns)
        return self.df

    def save_df(self):
        self.dataframe()
        self.df.to_csv('out.csv',index=None)
    