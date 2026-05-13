/**
 * 小红书每日Pipeline - 完整9步版
 * 
 * 基于daily-pipeline.js（成功版），出图改为真实MiniMax API
 * 
 * 执行流程：
 * Step1: 资料收集（从内容队列读取今日选题）
 * Step2: 提示词生成（生成3组不同房间的prompt）
 * Step4: 图片生成（分别生成3张图，同一空间3角度）
 * Step5: 质量检查（简单验证）
 * Step6: 自动修图（防AI处理）
 * Step7: 文案撰写
 * Step8: 发布
 */

const sqlite3 = require('sqlite3');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const DIR = __dirname;
const DB_PATH = path.join(DIR, 'xhs.db');
const LOG_DIR = path.join(DIR, 'logs');
const OUTPUT_DIR = path.join(DIR, 'output');

function log(msg) {
  const ts = new Date().toISOString().slice(11, 19);
  const line = '[' + ts + '] ' + msg;
  console.log(line);
  fs.mkdirSync(LOG_DIR, { recursive: true });
  fs.appendFileSync(path.join(LOG_DIR, 'pipeline-' + new Date().toISOString().slice(0,10) + '.log'), line + '\n');
}

// 从数据库读取今日内容队列
async function getTodayContent() {
  const db = new sqlite3.Database(DB_PATH);
  db.exec('PRAGMA journal_mode=WAL');
  db.exec('PRAGMA synchronous=NORMAL');
  const today = new Date().toISOString().slice(0, 10);
  
  const row = await new Promise((resolve) => {
    db.get('SELECT * FROM content_queue WHERE date = ?', [today], (err, row) => {
      if (err) resolve(null);
      else resolve(row);
    });
  });
  db.close();
  
  if (!row) {
    log('[内容队列] 今日无数据，使用默认风格');
    return {
      style: '现代简约',
      topics: JSON.stringify(['现代简约', '客厅设计', '家居装修']),
      prompts: JSON.stringify([
        { space: '客厅_全景', prompt: '从餐厅看客厅全景，现代简约风格...' },
        { space: '客厅_沙发区', prompt: '客厅沙发区特写...' },
        { space: '客厅_电视墙', prompt: '客厅电视墙方向...' }
      ])
    };
  }
  return row;
}

// 生成图片（真实MiniMax出图）
async function generateImages(prompts) {
  log('[生成] 开始生成' + prompts.length + '张图片...');
  const imagePaths = [];
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  
  for (let i = 0; i < prompts.length; i++) {
    const p = prompts[i];
    log('[生成] ' + p.space + ': ' + (p.prompt || '').slice(0, 50) + '...');
    
    const result = await generateSingleImage(p.space, p.prompt);
    if (result && result.path) {
      imagePaths.push(result.path);
    }
  }
  
  log('[生成] 完成，共' + imagePaths.length + '张');
  return imagePaths;
}

// 真实出图（调minimax-image.js API）
async function generateSingleImage(space, prompt) {
  const scriptPath = path.join(DIR, 'minimax-image.js');
  if (!fs.existsSync(scriptPath)) {
    log('[生成] minimax-image.js 不存在');
    return null;
  }

  const filename = space.replace(/[\/\s]/g, '_') + '_' + Date.now() + '.png';
  const outFile = path.join(OUTPUT_DIR, filename);
  
  try {
    execSync(`node "${scriptPath}" "${(prompt || '').replace(/"/g,'\\"')}" "${outFile}" 3:4`, {
      timeout: 60000,
      stdio: 'pipe'
    });
    if (fs.existsSync(outFile) && fs.statSync(outFile).size > 1000) {
      log('[生成] ✅ 已保存: ' + filename);
      return { space, prompt, path: outFile, generated: true };
    }
  } catch(e) {
    log('[生成] ❌ ' + space + '失败: ' + (e.message || '').slice(0, 80));
  }
  return null;
}

// 质量检查 + 防AI处理
async function polishImages(imagePaths) {
  log('[修图] 防AI处理...');
  try {
    const polish = require('./anti-ai-polish.js');
    const result = await polish.polishAll({ imageDir: OUTPUT_DIR });
    log('[修图] 完成，处理' + result.imageCount + '张');
  } catch(e) {
    log('[修图] 失败: ' + (e.message || '').slice(0, 80));
  }
  return imagePaths;
}

// 撰写文案（子AI）
function generateCopy(style) {
  try {
    const cw = require('./copywriter.js');
    if (typeof cw.generate === 'function') {
      const result = cw.generate({ style, room: '客厅' });
      if (result && result.title && result.content) {
        log('[文案] 已生成: ' + result.title);
        const polish = require('./anti-ai-polish.js');
        const polished = polish.polishCopywrite(result.title, result.content);
        return { title: polished.title || result.title, content: polished.content || result.content };
      }
    }
  } catch(e) {
    log('[文案] 使用后备: ' + (e.message || '').slice(0, 60));
  }
  return { title: '新作|' + style + '风客厅设计', content: '分享一套' + style + '设计\n#装修 #室内设计' };
}

// 发布到小红书（Playwright）
async function publish(title, content, imagePaths) {
  const publishScript = path.join(DIR, 'xhs-publish-playwright.js');
  if (!fs.existsSync(publishScript)) {
    log('[发布] 脚本不存在');
    return { success: false, error: '脚本不存在' };
  }

  log('[发布] ' + title);
  
  try {
    execSync(`node "${publishScript}" "${title.replace(/"/g,'\\"')}" "${content.replace(/"/g,'\\"')}" "${imagePaths[0] || ''}"`, {
      timeout: 120000,
      stdio: 'pipe'
    });
    log('[发布] ✅ 成功');
    return { success: true };
  } catch(e) {
    log('[发布] ❌ 失败: ' + (e.message || '').slice(0, 80));
    return { success: false, error: e.message };
  }
}

// 主流程
async function runDailyPipeline(keywords) {
  log('========== 每日Pipeline ==========');
  
  try {
    // Step1: 确定任务
    let content;
    
    if (keywords) {
      content = {
        style: keywords,
        topics: JSON.stringify([keywords, '装修', '室内设计']),
        prompts: JSON.stringify([
          { space: '客厅_全景', prompt: '从餐厅看客厅全景。Modern minimalist客厅，浅灰沙发，大理石茶几，落地窗自然光。Canon EOS R5, no watermark' },
          { space: '客厅_沙发区', prompt: '客厅沙发区特写。Modern minimalist客厅沙发区，浅灰沙发，茶几，抱枕，绿植。Canon EOS R5' },
          { space: '客厅_电视墙', prompt: '客厅电视墙方向。Modern minimalist电视墙，悬空电视柜，电视，无装饰。Canon EOS R5' }
        ])
      };
      log('[Step1] 临时任务: ' + keywords);
    } else {
      content = await getTodayContent();
      log('[Step1] 今日队列: ' + content.style);
    }
    
    const prompts = JSON.parse(content.prompts);
    
    // Step4: 生成图片
    const imagePaths = await generateImages(prompts);
    
    if (imagePaths.length === 0) {
      throw new Error('无可用图片');
    }
    
    // Step5+6: 防AI处理
    const finalPaths = await polishImages(imagePaths);
    
    // Step7: 文案
    const copy = generateCopy(content.style);
    log('[文案] ' + copy.title);
    
    // Step8: 发布
    const pubResult = await publish(copy.title, copy.content, finalPaths);
    
    // 更新队列状态
    if (!keywords) {
      const db = new sqlite3.Database(DB_PATH);
      const today = new Date().toISOString().slice(0, 10);
      db.run('UPDATE content_queue SET status = ? WHERE date = ?', ['published', today]);
      db.close();
    }
    
    log('========== Pipeline完成 ==========');
    return { success: true, published: pubResult.success };
    
  } catch (e) {
    log('[错误] ' + e.message);
    return { success: false, error: e.message };
  }
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  const keywords = args.join(' ');
  runDailyPipeline(keywords || null)
    .then(r => process.exit(r.success ? 0 : 1))
    .catch(e => { console.error(e); process.exit(1); });
}

module.exports = { runDailyPipeline };
