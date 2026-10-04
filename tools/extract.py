import asyncio, json
from playwright.async_api import async_playwright
JS=r"""
() => {
  const rts=[...document.querySelectorAll('[data-testid="richTextElement"]')];
  const out=rts.map(el=>{const r=el.getBoundingClientRect();return {id:el.id||el.parentElement.id, top:Math.round(r.top+scrollY), left:Math.round(r.left), w:Math.round(r.width), html:el.innerHTML}});
  const bgs=[...document.querySelectorAll('*')].filter(e=>{const cs=getComputedStyle(e);return cs.backgroundImage&&cs.backgroundImage!=='none'}).map(e=>({tag:e.tagName,id:e.id,bg:getComputedStyle(e).backgroundImage.slice(0,200),att:getComputedStyle(e).backgroundAttachment,pos:getComputedStyle(e).position}));
  const imgs=[...document.querySelectorAll('img')].map(i=>({src:i.currentSrc.slice(0,250),w:i.naturalWidth,h:i.naturalHeight,fit:getComputedStyle(i).objectFit,pos:getComputedStyle(i).objectPosition, parentPos:getComputedStyle(i.closest('[data-testid]')||i.parentElement).position}));
  const vids=[...document.querySelectorAll('wix-bg-media, [data-testid="bgMedia"], [data-testid="colorUnderlay"]')].map(e=>({tag:e.tagName,id:e.id,bgc:getComputedStyle(e).backgroundColor,op:getComputedStyle(e).opacity}));
  return {rts:out,bgs,imgs,vids};
}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1440,"height":900})
    for name,url in {"home":"https://www.eisenbraunelectric.co/","about":"https://www.eisenbraunelectric.co/about"}.items():
      await pg.goto(url,wait_until="networkidle",timeout=60000); await pg.wait_for_timeout(1500)
      d=await pg.evaluate(JS); json.dump(d,open(f"ref/{name}-rich.json","w"),indent=1)
      print(name,len(d['rts']),'rich text blocks')
      for x in d['bgs']: print(' BG',x)
      for x in d['imgs']: print(' IMG',x)
      for x in d['vids']: print(' UL',x)
    await b.close()
asyncio.run(main())
