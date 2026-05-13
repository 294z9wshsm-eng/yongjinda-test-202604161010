/**
 * 小红书自动发布脚本 v4（防检测版）
 * - 操作间隔随机化
 * - 添加人类行为特征
 * - 发布时间随机浮动
 */

const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');

const TIMEOUT={
  login:120000,
  upload:30000,
  form:30000,
  publish:30000
};

const LOG_DIR=path.join(__dirname,'logs');
const LOG_FILE=path.join(LOG_DIR,`${new Date().toISOString().slice(0,10)}.log`);
const CONFIG_FILE=path.join(__dirname,'xhs-config.json');

// ========== 随机工具 ==========
function random(min,max){
  return Math.floor(Math.random()*(max-min+1))+min;
}

function randomDelay(){
  const ms=random(800,2500);
  return new Promise(resolve=>setTimeout(resolve,ms));
}

function randomMouseMove(page){
  return page.mouse.move(random(100,800),random(200,600));
}

// ========== 日志 ==========
function log(msg){
  const ts=new Date().toISOString().slice(11,19);
  const line=`[${ts}] ${msg}`;
  console.log(line);
  fs.mkdirSync(LOG_DIR,{recursive:true});
  fs.appendFileSync(LOG_FILE,line+'\n');
}

function withTimeout(promise,ms,desc){
  return Promise.race([
    promise,
    new Promise((_,reject)=>setTimeout(()=>reject(new Error(`${desc}超时(${ms/1000}s)`)),ms))
  ]);
}

// ========== 加载配置 ==========
function loadConfig(){
  if(fs.existsSync(CONFIG_FILE)){
    return JSON.parse(fs.readFileSync(CONFIG_FILE,'utf8'));
  }
  throw new Error('没有找到配置文件，请先运行 write-config.js');
}

// ========== 主流程 ==========
(async()=>{
  // 加载配置
  const CONFIG = loadConfig();
  log('已加载配置: ' + CONFIG.title);
  
  // 计算随机发布延迟
  const now=new Date();
  const targetHour=random(17,18);
  const targetMin=random(30,59);
  const delayMs=((targetHour*60+targetMin)-(now.getHours()*60+now.getMinutes()))*60*1000;
  
  if(delayMs>0 && delayMs<5*60*1000){
    log(`随机发布等待: ${targetHour}:${targetMin} (还有${Math.round(delayMs/60000)}分钟)`);
    await new Promise(resolve=>setTimeout(resolve,delayMs));
  }
  
  log('========== 开始发布流程 ==========');
  let browser;
  
  try{
    log('启动浏览器...');
    browser=await chromium.launch({
      headless:false,
      args:['--no-sandbox','--disable-blink-features=AutomationControlled']
    });
    
    const ctx=await browser.newContext({
      viewport:{width:1280,height:800},
      userAgent:'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });
    const page=await ctx.newPage();
    
    // 注入反检测脚本
    await page.addInitScript(() => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
      Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN','zh','en'] });
      window.chrome = { runtime: {} };
    });
    
    // 随机鼠标移动
    await randomMouseMove(page);
    await randomDelay();
    
    if(fs.existsSync(CONFIG.cookiesPath || path.join(__dirname,'cookies.json'))){
      const cookies=JSON.parse(fs.readFileSync(CONFIG.cookiesPath || path.join(__dirname,'cookies.json'),'utf8'));
      await ctx.addCookies(cookies);
      log('已加载cookies');
    }
    
    log('访问创作者首页...');
    await randomMouseMove(page);
    await randomDelay();
    await withTimeout(page.goto('https://creator.xiaohongshu.com/new/home',{timeout:60000}),TIMEOUT.login,'访问首页');
    
    await page.evaluate(()=>window.scrollTo(0,Math.floor(Math.random()*201)+100));
    await randomDelay();
    
    if(page.url().includes('login')){
      log('需要登录，等待扫码...');
      await randomDelay();
      await withTimeout(page.waitForFunction(()=>!window.location.href.includes('login'),{timeout:TIMEOUT.login}),TIMEOUT.login,'登录');
      const newCookies=await ctx.cookies();
      fs.writeFileSync(CONFIG.cookiesPath || path.join(__dirname,'cookies.json'),JSON.stringify(newCookies));
      log('cookies已保存');
    } else {
      log('已登录');
    }
    
    log('点击发布图文笔记...');
    await randomMouseMove(page);
    await randomDelay();
    await page.locator('text=发布笔记').last().click();
    await randomDelay();
    
    log('切换到上传图文...');
    await page.evaluate(() => window.scrollTo(0, 0));
    await randomDelay();
    await page.evaluate(() => {
      const spans = document.querySelectorAll('span');
      for(const s of spans) {
        if(s.textContent.includes('上传图文')) {
          s.click();
          return;
        }
      }
    });
    await randomDelay();
    
    log('上传图片...');
    const validPaths=CONFIG.imagePaths.filter(p=>fs.existsSync(p));
    if(validPaths.length>0){
      await randomMouseMove(page);
      await randomDelay();
      await withTimeout(
        page.locator('input[type=file]').first().setInputFiles(validPaths),
        TIMEOUT.upload
      ,'上传图片');
      log(`图片已上传: ${validPaths.length}张`);
    } else {
      log('警告：没有找到有效图片');
    }
    
    log('等待图片上传...');
    await randomDelay();
    await new Promise(r => setTimeout(r, random(8000,15000)));
    
    log('填写标题...');
    await randomMouseMove(page);
    await randomDelay();
    await withTimeout(
      page.locator('input[placeholder="填写标题会有更多赞哦"]').fill(CONFIG.title),
      TIMEOUT.form
    ,'填写标题');
    log('标题已填');
    
    await randomDelay();
    
    log('填写正文...');
    await randomMouseMove(page);
    await randomDelay();
    await withTimeout(
      (async()=>{
        await page.locator('.tiptap.ProseMirror').click();
        await randomDelay();
        await page.locator('.tiptap.ProseMirror').fill(CONFIG.content);
      })(),
      TIMEOUT.form
    ,'填写正文');
    log('正文已填');
    
    await page.evaluate(()=>window.scrollTo(0,Math.floor(Math.random()*101)+50));
    await randomDelay();
    
    log('点击发布...');
    await randomMouseMove(page);
    await randomDelay();
    await withTimeout(
      page.locator('text=发布').last().click(),
      TIMEOUT.publish
    ,'点击发布');
    log('已点击发布');
    
    await randomDelay();
    await page.waitForTimeout(random(3000,6000));
    
    log('========== 发布完成 ==========');
    
  } catch(e){
    log(`错误: ${e.message}`);
    if(browser){
      try{
        const pages=await browser.pages();
        if(pages.length>0){
          await pages[0].screenshot({path:path.join(LOG_DIR,'error-screenshot.png')});
          log('错误截图已保存');
        }
      } catch{}
    }
    process.exit(1);
  } finally{
    if(browser){
      await browser.close();
    }
  }
})();