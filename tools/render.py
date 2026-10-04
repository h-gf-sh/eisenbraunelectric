import json, asyncio, sys
from playwright.async_api import async_playwright
PAGES={"home":"https://www.eisenbraunelectric.co/","about":"https://www.eisenbraunelectric.co/about"}
JS=r"""
() => {
  const out={iframes:[],texts:[],links:[],fonts:new Set(),bg:getComputedStyle(document.body).backgroundColor};
  document.querySelectorAll('iframe').forEach(f=>out.iframes.push({src:f.src,title:f.title,w:f.width,h:f.height,rect:f.getBoundingClientRect().toJSON()}));
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_ELEMENT);
  const seen=new Set();
  while(walker.nextNode()){
    const el=walker.currentNode;
    if(!['H1','H2','H3','H4','H5','H6','P','A','LI','SPAN'].includes(el.tagName)) continue;
    const t=(el.innerText||'').trim(); if(!t) continue;
    if(el.tagName==='SPAN' && el.children.length) continue;
    const cs=getComputedStyle(el); const r=el.getBoundingClientRect();
    if(r.width===0) continue;
    const key=el.tagName+t.slice(0,80)+Math.round(r.top);
    if(seen.has(key)) continue; seen.add(key);
    out.fonts.add(cs.fontFamily);
    out.texts.push({tag:el.tagName,text:t.slice(0,4000),font:cs.fontFamily,size:cs.fontSize,weight:cs.fontWeight,lh:cs.lineHeight,ls:cs.letterSpacing,color:cs.color,align:cs.textAlign,tt:cs.textTransform,style:cs.fontStyle,top:Math.round(r.top+scrollY),left:Math.round(r.left),width:Math.round(r.width),href:el.href||null});
  }
  document.querySelectorAll('a').forEach(a=>out.links.push({text:(a.innerText||'').trim(),href:a.href,ariaLabel:a.getAttribute('aria-label')}));
  out.fonts=[...out.fonts];
  out.docH=document.documentElement.scrollHeight;
  out.ffaces=[...document.fonts].map(f=>({family:f.family,weight:f.weight,style:f.style,status:f.status}));
  return out;
}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for vp,(w,h) in {"desktop":(1440,900),"mobile":(390,844)}.items():
      ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=1 if vp=="desktop" else 2)
      for name,url in PAGES.items():
        pg=await ctx.new_page(); reqs=[]
        pg.on("request",lambda r: reqs.append(r.url))
        await pg.goto(url,wait_until="networkidle",timeout=60000)
        # scroll to trigger lazy loads
        H=await pg.evaluate("document.documentElement.scrollHeight")
        y=0
        while y<H:
          y+=600; await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(250)
          H=await pg.evaluate("document.documentElement.scrollHeight")
        await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"ref/{name}-{vp}-full.png",full_page=True)
        await pg.screenshot(path=f"ref/{name}-{vp}-fold.png")
        data=await pg.evaluate(JS)
        data["requests"]=sorted(set(reqs))
        if vp=="desktop":
          html=await pg.content(); open(f"ref/{name}-rendered.html","w").write(html)
        json.dump(data,open(f"ref/{name}-{vp}.json","w"),indent=1)
        print(vp,name,"docH",data["docH"],"iframes",len(data["iframes"]),"reqs",len(data["requests"]))
      await ctx.close()
    await b.close()
asyncio.run(main())
