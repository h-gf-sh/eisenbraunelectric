import asyncio, json, sys
from playwright.async_api import async_playwright
JS=r"""(sel)=>{
 const res=[];
 document.querySelectorAll(sel).forEach(el=>{
   const tops=[]; const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
   while(w.nextNode()){const n=w.currentNode; if(!n.textContent.trim())continue; const r=document.createRange(); r.selectNodeContents(n);
     for(const rc of r.getClientRects()){ if(rc.width<2)continue; tops.push([Math.round(rc.top+scrollY), Math.round(rc.height), Math.round(rc.left), Math.round(rc.right)]);}}
   const uniq={}; tops.forEach(t=>{uniq[t[0]]=uniq[t[0]]||t;});
   const ys=Object.keys(uniq).map(Number).sort((a,b)=>a-b);
   res.push({id:el.id||el.parentElement.id, n:ys.length, ys, first:(el.innerText||'').trim().slice(0,30)});
 });
 return res;}"""
async def main(url,sel,out):
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1440,"height":900})
    await pg.goto(url,wait_until="networkidle",timeout=60000); await pg.wait_for_timeout(1500)
    r=await pg.evaluate(JS,sel); json.dump(r,open(out,'w'),indent=1)
    for x in r: print(x['id'],x['n'],x['first'],'| gaps',[b-a for a,b in zip(x['ys'],x['ys'][1:])][:14])
    await b.close()
asyncio.run(main(sys.argv[1],sys.argv[2],sys.argv[3]))
