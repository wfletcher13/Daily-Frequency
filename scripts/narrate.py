#!/usr/bin/env python3
"""Turn an edited episode script into local, free Piper audio. No paid API."""
import json, pathlib, subprocess, sys, tempfile
root=pathlib.Path(__file__).resolve().parents[1]
source=root/"episodes/latest.json"
if not source.exists(): sys.exit("No editorial script: skip narration")
ep=json.loads(source.read_text(encoding="utf-8"))
parts=ep.get("segments",[])
if not ep.get("date") or not parts: sys.exit("Incomplete episode")
word_count=sum(len(" ".join(p.get("paragraphs",[])).split()) for p in parts)
if word_count<450: sys.exit("Refusing to publish incomplete short episode")
out=root/"daily";out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory() as td:
 t=pathlib.Path(td)
 voices=t/"voices";voices.mkdir()
 model_names={"host":"en_US-lessac-medium","guest":"en_GB-alan-medium"}
 for v in sorted({model_names.get(p.get("voice","host"),model_names["host"]) for p in parts}):
  subprocess.run([sys.executable,"-m","piper.download_voices","--download-dir",str(voices),v],check=True)
 files=[]
 for n,p in enumerate(parts):
  model=model_names.get(p.get("voice","host"),model_names["host"])
  transcript=p.get("title","")+". "+" ".join(p.get("paragraphs",[]))
  txt=t/f"{n:02}.txt";txt.write_text(transcript,encoding="utf-8")
  wav=t/f"{n:02}.wav"
  subprocess.run([sys.executable,"-m","piper","-m",model,"--data-dir",str(voices),"-f",str(wav),"--input-file",str(txt)],check=True)
  files.append(wav)
 # Normalize formats before concatenation to support models with different sample rates
 converted=[]
 for i,wav in enumerate(files):
  standardized=t/f"std{i:02}.wav"
  subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(wav),"-ar","22050","-ac","1",str(standardized)],check=True)
  converted.append(standardized)
 manifest=t/"concat.txt";manifest.write_text("".join("file '"+str(p)+"'\n" for p in converted))
 subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(manifest),"-codec:a","libmp3lame","-b:a","64k",str(out/"latest.mp3")],check=True)
(out/"latest.json").write_text(json.dumps(ep,indent=2,ensure_ascii=False),encoding="utf-8")
print("Rendered full episode:",ep["date"],word_count,"words")
