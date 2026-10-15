#!/usr/bin/env python3
"""Free, source-linked headline audio digest. No generative AI, no API keys."""
import datetime as dt, json, pathlib, re, subprocess, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/"daily";OUT.mkdir(exist_ok=True)
TODAY=dt.datetime.now(ZoneInfo("America/New_York")).strftime("%B %-d, %Y")
FEEDS=[
 ("Markets & investing","https://news.google.com/rss/search?q="+urllib.parse.quote("stocks investing economy inflation when:1d")+"&hl=en-US&gl=US&ceid=US:en",3),
 ("World & business","https://feeds.bbci.co.uk/news/world/rss.xml",3),
 ("Liverpool & football","https://news.google.com/rss/search?q="+urllib.parse.quote("Liverpool FC Premier League when:2d")+"&hl=en-US&gl=US&ceid=US:en",2),
 ("Science & discovery","https://news.google.com/rss/search?q="+urllib.parse.quote("physics archaeology scientific discovery when:7d")+"&hl=en-US&gl=US&ceid=US:en",2),
]
def items(url,limit):
 req=urllib.request.Request(url,headers={"User-Agent":"DailyFrequency/1.0 contact: public news digest"})
 try:
  with urllib.request.urlopen(req,timeout=20) as r:data=r.read()
  tree=ET.fromstring(data)
  result=[]
  for e in tree.findall(".//item")[:limit*3]:
   title=(e.findtext("title") or "").strip()
   link=(e.findtext("link") or "").strip()
   title=re.sub(r"\\s+"," ",title)
   if not title or not link:continue
   result.append({"title":title,"url":link})
   if len(result)>=limit:break
  return result
 except Exception as e:
  print("Feed unavailable:",str(e),file=sys.stderr);return []
segments=[]
for category,url,limit in FEEDS:
 found=items(url,limit)
 if found:segments.append({"category":category,"items":found})
if not segments:sys.exit("No sources were available: refusing to publish an empty update")
sentences=["Good morning. This is The Daily Frequency, your free headline edition for "+TODAY+".",
 "A quick note: this is a sourced headline roundup, not the full conversational show. Stories are chosen from public feeds and should be read at their original links for full context."]
for s in segments:
 sentences.append("Next, "+s["category"]+".")
 for it in s["items"]:
  # Headlines are attributed to their originating sources; no unverified assertions beyond headlines.
  sentences.append("One story making headlines: "+it["title"].replace(" - ",". Source: ")+".")
sentences.append("That's the headline round-up. Stay curious out there.")
text="\n".join(sentences)
(OUT/"script.txt").write_text(text,encoding="utf-8")
(OUT/"latest.json").write_text(json.dumps({"date":TODAY,"edition":"Automated headline digest","segments":segments,"notice":"Automated sourced headlines, not an AI-written analysis. Open original links to verify details.","audio":"daily/latest.mp3"},indent=2),encoding="utf-8")
subprocess.run([sys.executable,"-m","piper.download_voices","en_US-lessac-medium"],cwd=OUT,check=True)
subprocess.run([sys.executable,"-m","piper","-m","en_US-lessac-medium","-f","latest.wav","--input-file","script.txt"],cwd=OUT,check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","latest.wav","-codec:a","libmp3lame","-b:a","64k","latest.mp3"],cwd=OUT,check=True)
(OUT/"latest.wav").unlink(missing_ok=True)
print("Produced dated sourced audio digest for",TODAY)
