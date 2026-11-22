const assert=require('node:assert/strict');
const {chromium}=require('/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.BASE_URL||'http://127.0.0.1:4174/');
 await page.locator('#reject-analytics').tap();await page.locator('#monkey-banana').tap();await page.locator('#monkey-toggle').tap();
 assert.equal(await page.locator('.resident').count(),19);assert.equal(await page.locator('.follower').count(),1);
 const client=await context.newCDPSession(page);
 await page.evaluate(()=>{window.touchMoves=0;window.pointerCancels=0;addEventListener('touchmove',()=>window.touchMoves++);addEventListener('pointercancel',()=>window.pointerCancels++)});
 const position=()=>page.locator('.follower').evaluate(e=>{const m=new DOMMatrix(getComputedStyle(e).transform);return{x:m.m41,y:m.m42}});
 const initial=await position();
 await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:330,y:650}]});
 for(const y of [600,550,500,450,400,350]){await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:330,y}]});await page.waitForTimeout(90)}
 await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 const scrolled=await page.evaluate(()=>({y:scrollY,moves:window.touchMoves,cancels:window.pointerCancels}));
 assert.ok(scrolled.y>50,JSON.stringify(scrolled));assert.ok(scrolled.moves>2,JSON.stringify(scrolled));assert.ok(scrolled.cancels>0,JSON.stringify(scrolled));
 assert.notDeepEqual(await position(),initial);
 // After native scrolling, a real tap sets a new destination, then the monkey settles there.
 await page.touchscreen.tap(310,430);
 await page.waitForFunction(()=>document.querySelector('.follower')?.dataset.motion==='running');
 await page.waitForFunction(()=>document.querySelector('.follower')?.dataset.motion==='idle',{},{timeout:10000});
 const arrived=await position();assert.ok(Math.abs(arrived.x-236)<3&&Math.abs(arrived.y-448)<3,JSON.stringify(arrived));
 await page.waitForTimeout(300);assert.deepEqual(await position(),arrived);
 assert.equal(await page.locator('.follower').evaluate(e=>getComputedStyle(e).pointerEvents),'none');
 await page.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';scrollTo(0,0)});
 await page.locator('[data-lang=en]').tap();assert.equal(await page.locator('html').getAttribute('lang'),'en');
 await page.screenshot({path:'review/mobile-finger-follower.png'});
 await page.locator('#monkey-toggle').tap();assert.equal(await page.locator('.macaque').count(),0);assert.deepEqual(errors,[]);
 const quiet=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,reducedMotion:'reduce'}),quietPage=await quiet.newPage();
 await quietPage.goto(process.env.BASE_URL||'http://127.0.0.1:4174/');await quietPage.locator('#reject-analytics').tap();await quietPage.locator('#monkey-banana').tap();await quietPage.locator('#monkey-toggle').tap();
 assert.equal(await quietPage.locator('.follower').count(),0);assert.ok((await quietPage.locator('[data-monkey=F1]').getAttribute('src')).endsWith('-still.png'));
 await quietPage.touchscreen.tap(250,450);assert.equal(await quietPage.locator('.follower').count(),0);await quiet.close();
 console.log(JSON.stringify({status:'PASS',checks:['touch starts and moves follower','native scrolling continues after pointercancel','follower reaches last touch and stops','links remain tappable','reduced motion stays static','reset removes troupe'],scroll:scrolled}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
