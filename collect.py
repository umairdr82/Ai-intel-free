import json,re,hashlib,calendar,datetime
from pathlib import Path
import feedparser
FEEDS=[("OpenAI","https://openai.com/news/rss.xml","Official"),("Google AI","https://blog.google/technology/ai/rss/","Official"),("Google DeepMind","https://deepmind.google/blog/rss.xml","Official"),("Google Research","https://research.google/blog/rss/","Official"),("Microsoft Research","https://www.microsoft.com/en-us/research/feed/","Official"),("Hugging Face","https://huggingface.co/blog/feed.xml","Official"),("NVIDIA","https://blogs.nvidia.com/blog/category/deep-learning/feed/","Official"),("GitHub AI","https://github.blog/ai-and-ml/feed/","Official"),("OpenAI SDK","https://github.com/openai/openai-python/releases.atom","Release"),("Anthropic SDK","https://github.com/anthropics/anthropic-sdk-python/releases.atom","Release"),("Transformers","https://github.com/huggingface/transformers/releases.atom","Release"),("Ollama","https://github.com/ollama/ollama/releases.atom","Release"),("arXiv AI","https://rss.arxiv.org/rss/cs.AI","Preprint")]
p=Path(__file__).parent/'data/stories.json'
old=json.loads(p.read_text())
seen={s['id']:s for s in old.get('stories',[])}
now=datetime.datetime.now(datetime.timezone.utc)
ok=0
for name,url,kind in FEEDS:
 try:
  feed=feedparser.parse(url,agent="AIIntelFree/1.0")
  if not feed.entries:print("SKIP",name);continue
  ok+=1
  for e in feed.entries[:25]:
   link=e.get('link','')
   if not link.startswith('http'):continue
   parsed=e.get('published_parsed') or e.get('updated_parsed')
   date=datetime.datetime.fromtimestamp(calendar.timegm(parsed),datetime.timezone.utc) if parsed else now
   if date<now-datetime.timedelta(days=45):continue
   title=re.sub('<[^>]*>','',e.get('title','')).strip()
   if not title:continue
   key=hashlib.sha256(link.split('#')[0].encode()).hexdigest()[:20]
   desc=re.sub('<[^>]*>','',e.get('summary','')).strip()[:650]
   imp=min(4,(2 if kind=='Preprint' else 3)+int(any(w in title.lower() for w in ('launch','release','introduc','model','agent','gpt','claude','gemini','security'))))
   seen[key]=dict(id=key,title=title,url=link,source=name,source_type=kind,published_at=date.isoformat(),summary=desc,importance=imp,status='PREPRINT' if kind=='Preprint' else 'PRIMARY SOURCE')
 except Exception as ex:print('ERROR',name,str(ex)[:150])
stories=sorted(seen.values(),key=lambda s:s['published_at'],reverse=True)[:450]
p.write_text(json.dumps(dict(updated_at=now.isoformat(),stories=stories,sources_checked=ok),ensure_ascii=False,indent=2)+'\n')
print('Stored',len(stories),'stories from',ok,'sources')
