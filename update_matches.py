import json,re,datetime as dt,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'matches.json'
LOGOS=ROOT/'logos.json'
BASE_LOGO='https://sportstv-img.b-cdn.net/pics/mini/teams/'
FTV='https://www.futboltv.info/'
HEAD={'User-Agent':'Mozilla/5.0 (compatible; IPTV-Futbol-GitHub/2.0)'}

# ESPN competition endpoints used only to guarantee complete fixture discovery.
LEAGUES={
 'esp.1':'Liga EA Sports','eng.1':'Premier League','ita.1':'Serie A Italia',
 'ger.1':'Bundesliga','fra.1':'Ligue 1','esp.2':'Liga Hypermotion',
 'esp.3':'Primera Federación','esp.w.1':'Liga F','uefa.europa':'Europa League',
 'uefa.champions':'Champions League','conmebol.libertadores':'Copa Libertadores',
 'ita.cup':'Coppa Italia'
}


def fetch(url):
    req=Request(url,headers=HEAD)
    with urlopen(req,timeout=25) as r: return r.read()

def norm(s):
    return re.sub(r'\s+',' ',(s or '').strip())

def espn_matches(start,end):
    rows=[]
    d=start
    while d<=end:
        ds=d.strftime('%Y%m%d')
        for league,comp in LEAGUES.items():
            url=f'https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard?dates={ds}'
            try:
                data=json.loads(fetch(url))
            except Exception as e:
                print('ESPN fail',league,ds,e); continue
            for ev in data.get('events',[]):
                try:
                    compname=ev.get('competitions',[{}])[0]
                    c=ev.get('competitions',[{}])[0]
                    home=next(x for x in c.get('competitors',[]) if x.get('homeAway')=='home')
                    away=next(x for x in c.get('competitors',[]) if x.get('homeAway')=='away')
                    date=ev.get('date','')[:10]
                    local=dt.datetime.fromisoformat(ev['date'].replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Madrid'))
                    status=c.get('status',{}).get('type',{}).get('name','')
                    rows.append({'id':'espn-'+str(ev.get('id')), 'date':date, 'time':local.strftime('%H:%M'),
                        'competition':comp, 'home':home.get('team',{}).get('displayName') or home.get('team',{}).get('name',''),
                        'away':away.get('team',{}).get('displayName') or away.get('team',{}).get('name',''),
                        'channels':[], 'status':status, 'score':'', 'minute':'', 'homeLogo':'','awayLogo':''})
                except Exception: continue
        d+=dt.timedelta(days=1)
    return rows

MONTHS={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'octubre':10,'noviembre':11,'diciembre':12}
def parse_date(txt,year):
    m=re.search(r'\b(\d{1,2})\s+de\s+([a-záéíóú]+)(?:\s+de\s+(\d{4}))?',txt.lower())
    if not m: return None
    mon=MONTHS.get(m.group(2));
    if not mon:return None
    return dt.date(int(m.group(3) or year),mon,int(m.group(1)))

def ftv_matches():
    try: html=fetch(FTV).decode('utf-8','ignore')
    except Exception as e:
        print('FTV fail',e); return []
    soup=BeautifulSoup(html,'html.parser')
    today=dt.date.today(); current_year=today.year; current_date=None; out=[]; seen=set()
    # Search time nodes and climb to the smallest ancestor containing two team links.
    for node in soup.find_all(string=re.compile(r'^\s*\d{1,2}:\d{2}\s*$')):
        time=norm(node)
        if not re.fullmatch(r'\d{1,2}:\d{2}',time): continue
        # Find latest preceding date heading.
        cur=node.parent
        for _ in range(20):
            if not cur: break
            txt=norm(cur.get_text(' ',strip=True))
            dd=parse_date(txt,current_year)
            if dd: current_date=dd; break
            cur=cur.parent
        # Look at ancestors for a card with exactly 2+ team links.
        anc=node.parent; card=None
        for _ in range(8):
            if not anc: break
            teams=[]
            for a in anc.find_all('a',href=True):
                if '/equipo/' in a.get('href',''):
                    name=norm(a.get_text(' ',strip=True)) or norm(a.get('title','')) or norm(a.find('img').get('alt','') if a.find('img') else '')
                    if name and name not in teams: teams.append(name)
            if len(teams)>=2:
                card=anc; break
            anc=anc.parent
        if not card or not current_date: continue
        teams=teams[:2]
        channels=[]
        for a in card.find_all('a',href=True):
            href=a.get('href',''); text=norm(a.get_text(' ',strip=True))
            if '/canal/' in href and text and text not in channels: channels.append(text)
        comp=''
        for a in card.find_all('a',href=True):
            if '/competicion/' in a.get('href',''):
                comp=norm(a.get_text(' ',strip=True)); break
        if not comp:
            text=norm(card.get_text(' ',strip=True))
            # Best-effort competition labels from known names.
            for c in set(LEAGUES.values())|{'Liga EA Sports','Liga Hypermotion','Primera Federación','Liga F'}:
                if c.lower() in text.lower(): comp=c; break
        key=(current_date.isoformat(),time,teams[0],teams[1])
        if key in seen: continue
        seen.add(key)
        out.append({'date':current_date.isoformat(),'time':time,'home':teams[0],'away':teams[1], 'competition':comp,'channels':channels})
    return out

def aliases(name):
    s=norm(name).lower()
    repl={'cf ':'',' cf':'','rc ':'','rcd ':'','real ':'','club ':'','deportivo de la coruña':'deportivo','deportivo la coruna':'deportivo','málaga cf':'málaga','malaga cf':'malaga','athletic club':'athletic','r. racing club':'racing de santander','racing club':'racing de santander','r. sociedad':'real sociedad','real sociedad san sebastian':'real sociedad','atletico madrid':'atlético de madrid','atlético madrid':'atlético de madrid','villarreal cf':'villarreal','getafe cf':'getafe','valencia cf':'valencia','levante ud':'levante','real betis seville':'betis'}
    for a,b in repl.items(): s=s.replace(a,b)
    return re.sub(r'[^a-z0-9áéíóúüñ ]','',s).strip()

def merge(espn,ftv):
    fmap={(x['date'],x['time'],aliases(x['home']),aliases(x['away'])):x for x in ftv}
    old=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else []
    # Keep old data only as a channel/logo fallback, not as the source of fixture completeness.
    omap={(x.get('date'),x.get('time'),aliases(x.get('home','')),aliases(x.get('away',''))):x for x in old}
    merged=[]
    for m in espn:
        key=(m['date'],m['time'],aliases(m['home']),aliases(m['away']))
        o=omap.get(key,{})
        f=fmap.get(key,{})
        m['channels']=f.get('channels') or o.get('channels',[])
        m['competition']=f.get('competition') or m['competition']
        m['homeLogo']=o.get('homeLogo','');m['awayLogo']=o.get('awayLogo','')
        merged.append(m)
    # Add FTV-only fixtures not returned by ESPN (cups/TV listings).
    ekeys={(x['date'],x['time'],aliases(x['home']),aliases(x['away'])) for x in merged}
    for f in ftv:
        key=(f['date'],f['time'],aliases(f['home']),aliases(f['away']))
        if key not in ekeys:
            o=omap.get(key,{})
            merged.append({'id':'ftv-'+re.sub(r'[^0-9a-z]+','-', '-'.join(key)),'date':f['date'],'time':f['time'],'competition':f.get('competition') or 'Fútbol','home':f['home'],'away':f['away'],'channels':f.get('channels',[]),'status':'scheduled','score':'','minute':'','homeLogo':o.get('homeLogo',''),'awayLogo':o.get('awayLogo','')})
    merged.sort(key=lambda x:(x['date'],x['time'],x['competition'],x['home']))
    return merged

def main():
    start=dt.date.today(); end=start+dt.timedelta(days=6)
    e=espn_matches(start,end); print('ESPN fixtures',len(e))
    f=ftv_matches(); print('FTV listings',len(f))
    data=merge(e,f); print('Merged fixtures',len(data))
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
