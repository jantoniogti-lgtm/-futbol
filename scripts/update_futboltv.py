import re,json,html,urllib.request,datetime
URL="https://www.futboltv.info/"
req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0"})
raw=urllib.request.urlopen(req,timeout=45).read().decode("utf-8","ignore")
s=html.unescape(raw)
s=re.sub(r"<(script|style)\b.*?</\1>"," ",s,flags=re.I|re.S)
s=re.sub(r"<[^>]+>"," ",s)
s=re.sub(r"\s+"," ",s)
months={"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,"julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
date_re=re.compile(r"(?:hoy|mañana\s+)?(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)?\s*,?\s*(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})",re.I)
game_re=re.compile(r"(?P<time>\d{1,2}:\d{2})\s+(?P<comp>.*?)\s+(?P<home>.*?)\s+Image\s+vs\s+Image\s+(?P<away>.*?)\s+(?P<channels>(?:\[Button:\s*.*?\]\s*)*)(?=(?:\d{1,2}:\d{2})\s|$)",re.I)
marks=list(date_re.finditer(s)); today=datetime.date.today(); events=[]
for i,m in enumerate(marks):
    mon=months.get(m.group(2).lower())
    if not mon: continue
    d=datetime.date(int(m.group(3)),mon,int(m.group(1)))
    if not today<=d<=today+datetime.timedelta(days=6): continue
    block=s[m.end():marks[i+1].start() if i+1<len(marks) else len(s)]
    for g in game_re.finditer(block):
        ch=re.findall(r"\[Button:\s*(.*?)\]",g.group("channels"))
        home=re.sub(r"\s+"," ",g.group("home")).strip()
        away=re.sub(r"\s+"," ",g.group("away")).strip()
        comp=re.sub(r"\s+"," ",g.group("comp")).strip()
        if len(home)>80 or len(away)>80: continue
        events.append({"id":f"{d}_{g.group('time')}_{home}_{away}","date":d.isoformat(),"time":g.group("time"),"competition":comp,"home":home,"away":away,"channels":ch,"status":"scheduled","score":None,"minute":"","homeLogo":"","awayLogo":""})
uniq={x["id"]:x for x in events}
events=sorted(uniq.values(),key=lambda x:(x["date"],x["time"],x["home"]))
if not events: raise SystemExit("Fútbol TV no se pudo analizar; no se modifica matches.json")
open("matches.json","w",encoding="utf-8").write(json.dumps(events,ensure_ascii=False,indent=2))
print("Partidos extraídos:",len(events))
