import asyncio, sys
from playwright.async_api import async_playwright
async def main(url, prefix, ys, w=1440, h=900):
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":w,"height":h})
    await pg.goto(url,wait_until="load",timeout=60000); await pg.wait_for_timeout(3000)
    for y in ys:
      await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(1200)
      await pg.screenshot(path=f"{prefix}-{y}.png")
    await b.close()
url=sys.argv[1]; prefix=sys.argv[2]; ys=[int(x) for x in sys.argv[3].split(',')]
w=int(sys.argv[4]) if len(sys.argv)>4 else 1440; h=int(sys.argv[5]) if len(sys.argv)>5 else 900
asyncio.run(main(url,prefix,ys,w,h))
