import asyncio, json, sys
from playwright.async_api import async_playwright
JS=r"""()=>{
 const lines=(el)=>{const ys=new Set();const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);while(w.nextNode()){const n=w.currentNode;if(!n.textContent.trim())continue;const r=document.createRange();r.selectNodeContents(n);for(const rc of r.getClientRects()){if(rc.width>2)ys.add(Math.round(rc.top+scrollY));}}return [...ys].sort((a,b)=>a-b);};
 const o={h2:[],iframes:[],blocks:[]};
 document.querySelectorAll('main h2').forEach(h=>{const ys=lines(h);o.h2.push([h.textContent.trim().slice(0,22),ys[0]])});
 document.querySelectorAll('main .embed').forEach(f=>{const r=f.getBoundingClientRect();o.iframes.push([Math.round(r.top+scrollY),Math.round(r.left),Math.round(r.width),Math.round(r.height)])});
 document.querySelectorAll('.essay,.blurb,.about-body').forEach(b=>{const ys=lines(b);o.blocks.push([ys.length,ys[0],ys[ys.length-1]])});
 const t=document.querySelector('.site-title a'), tl=document.querySelector('.site-tagline'), nav=[...document.querySelectorAll('nav a')];
 o.title=lines(t)[0]; o.tagline=lines(tl)[0]; o.nav=[lines(nav[0])[0], Math.round(nav[0].getBoundingClientRect().right), lines(nav[nav.length-1])[0]];
 o.docH=document.documentElement.scrollHeight;
 o.fontsOk=[...document.fonts].map(f=>f.family+':'+f.status);
 return o;}"""
async def main(url, shots):
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1440,"height":900})
    await pg.goto(url,wait_until="load",timeout=60000); await pg.wait_for_timeout(2500)
    r=await pg.evaluate(JS); print(json.dumps(r))
    for y in shots:
      await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(700); await pg.screenshot(path=f"cmp/rebuild-{y}.png")
    await b.close()
import os; os.makedirs('cmp',exist_ok=True)
asyncio.run(main(sys.argv[1], [int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else []))
