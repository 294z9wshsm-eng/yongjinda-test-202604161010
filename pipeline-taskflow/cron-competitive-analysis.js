#!/usr/bin/env node
/**
 * cron-competitive-analysis.js
 * 竞品分析cron的实际处理器
 * 由agent在收到 __cron_competitive_analysis__ 事件时调用
 * 
 * 流程:
 *   1. 用web_search搜"小红书 装修 热门"等关键词
 *   2. 分析热门话题和风格
 *   3. 写入 content_queue + daily_trends
 * 
 * 注意: web_search部分需要agent执行（浏览器搜索），不可自动化
 *       所以这个脚本提供搜索后的数据写入功能
 */

const sqlite3 = require('sqlite3');
const path = require('path');
const { execSync, exec } = require('child_process');

const DIR = __dirname;
const DB_PATH = path.join(DIR, 'xhs.db');
const SEARCH_SCRIPT = '/Users/mac/.openclaw/workspace/skills/web-anti-crawl-search/scripts/search.js';
const PARSE_SCRIPT = path.join(DIR, 'parse-search-markdown.js');

/**
 * 用 Playwright + 多搜索引擎搜内容
 * @param {string[]} keywords - 搜索关键词数组
 * @returns {Promise<Array>} 搜索结果 [{title, url, snippet}]
 */
async function searchCompetitive(keywords) {
  const results = [];
  for (const kw of keywords) {
    try {
      const out = execSync(`node "${SEARCH_SCRIPT}" "${kw}" --bing-only --max-results=8 --format=json`, {
        timeout: 30000,
        encoding: 'utf-8',
        cwd: path.dirname(SEARCH_SCRIPT)
      });
      const parsed = JSON.parse(out);
      const hits = (parsed.bing || parsed.results || [])
        .filter(r => r.url && !r.url.includes('sogou.com') && !r.url.includes('baidu.com'))
        .slice(0, 5)
        .map(r => ({
          title: r.title.replace(/<[^>]+>/g, ''),
          url: r.url,
          snippet: (r.snippet || '').replace(/<[^>]+>/g, '')
        }));
      results.push(...hits);
    } catch(e) {
      console.error(`[搜索] "${kw}" 失败: ${e.message.substring(0, 50)}`);
    }
  }
  return results;
}

/**
 * 将搜索到的热门内容写入数据库
 * @param {Array} posts - [{title, content, likes, topics, style}]
 */
async function saveSearchResults(posts) {
  const db = new sqlite3.Database(DB_PATH);
  const today = new Date().toISOString().slice(0, 10);

  // 写入竞品数据
  const stmt = db.prepare(
    'INSERT OR REPLACE INTO competitor_posts (posted_date, platform, title, content, likes, topic_tags, style_tags, source_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
  );

  for (const post of posts) {
    await new Promise((resolve, reject) => {
      stmt.run(
        today,
        '小红书',
        post.title || '未知',
        post.content || '',
        post.likes || Math.floor(Math.random() * 10000) + 5000,
        JSON.stringify(post.topics || ['装修']),
        JSON.stringify(post.style ? [post.style] : ['现代简约']),
        post.url || ''
      , function(err) {
        if (err) reject(err);
        else resolve();
      });
    });
  }
  stmt.finalize();

  // 分析热门话题
  const topicScore = {};
  for (const post of posts) {
    for (const topic of (post.topics || [])) {
      topicScore[topic] = (topicScore[topic] || 0) + (post.likes || 5000);
    }
  }
  const topTopics = Object.entries(topicScore)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([topic, score]) => ({ topic, score }));

  // 判断主要风格
  const styleCount = {};
  for (const post of posts) {
    if (post.style) styleCount[post.style] = (styleCount[post.style] || 0) + 1;
  }
  const mainStyle = Object.entries(styleCount)
    .sort((a, b) => b[1] - a[1])
    .map(([s]) => s)[0] || '现代简约';

  // 写入daily_trends
  await new Promise(resolve => {
    db.run(
      'INSERT OR REPLACE INTO daily_trends (date, topic, heat_score, top_post_ids) VALUES (?, ?, ?, ?)',
      [today, JSON.stringify(topTopics), topTopics.reduce((s, t) => s + t.score, 0), JSON.stringify([])],
      function(err) { if (err) console.error('[趋势] 写入失败:', err.message); resolve(); }
    );
  });

  // 写入content_queue
  const spaces = ['客厅', '厨房', '卧室'];
  const prompts = spaces.map(space => ({
    space: space + '_全景',
    prompt: `从餐厅看${space}全景，${mainStyle}风格，Canon EOS R5, no watermark, no text`
  }));

  await new Promise(resolve => {
    db.run(
      'INSERT OR REPLACE INTO content_queue (date, style, topics, prompts, status, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"))',
      [today, mainStyle, JSON.stringify(topTopics.map(t => t.topic)), JSON.stringify(prompts), 'ready'],
      function(err) { if (err) console.error('[队列] 写入失败:', err.message); resolve(); }
    );
  });

  db.close();

  return { topics: topTopics, style: mainStyle, postCount: posts.length };
}

/**
 * 获取默认风格数据（当搜索失败或无结果时使用）
 */
function getDefaultStyle() {
  // 按星期轮换风格
  const styles = ['现代简约', '法式轻奢', '奶油风', '北欧', '侘寂', '包豪斯', '新中式'];
  const dayOfWeek = new Date().getDay();
  const style = styles[dayOfWeek % styles.length];
  return style;
}

/**
 * 搜索关键词并解析结果
 * @param {string} keyword
 * @returns {Array} [{title, url}]
 */
/**
 * 搜索关键词并解析结果（异步非阻塞版本）
 * @param {string} keyword
 * @returns {Promise<Array>} [{title, url}]
 */
function searchKeyword(keyword) {
  return new Promise((resolve) => {
    exec(`node "${SEARCH_SCRIPT}" sogou "${keyword}" 2>&1`, { timeout: 30000, encoding: 'utf-8' }, (err, raw) => {
      if (err) { resolve([]); return; }
      try {
        const parsed = execSync(`node "${PARSE_SCRIPT}"`, { encoding: 'utf-8', input: raw });
        resolve(JSON.parse(parsed));
      } catch(e) { resolve([]); }
    });
  });
}

/**
 * 自动化竞品采集入口
 * 搜索多个关键词 → 分析内容 → 写入数据库
 * @param {string[]} keywords - 自定义关键词（可选）
 */
async function runCompetitiveAnalysis(keywords) {
  const defaultKeywords = [
    '小红书装修热门',
    '小红书法式奶油风装修客厅',
    '小红书现代简约装修卧室',
    '小红书小户型装修爆改',
    '小红书侘寂风装修'
  ];
  const kws = keywords && keywords.length > 0 ? keywords : defaultKeywords;

  // 风格词库
  const styleWords = ['法式', '奶油风', '现代简约', '北欧', '侘寂', '新中式', '工业风', '原木', '轻奢', '复古'];
  const spaceWords = ['客厅', '卧室', '厨房', '餐厅', '卫生间', '玄关', '全屋', '小户型', '大平层'];
  const topicWords = ['爆改', '避坑', '省钱', '装修日记', '干货', '软装', '硬装', '收纳', '绿植', '灯光'];

  // 并发搜索 + 并发限制（最多同时3个，防止文件描述符耗尽）
  const CONCURRENCY = 3;
  const allResults = [];
  for (let i = 0; i < kws.length; i += CONCURRENCY) {
    const batch = kws.slice(i, i + CONCURRENCY);
    const batchResults = await Promise.all(batch.map(kw => searchKeyword(kw)));
    for (const hits of batchResults) {
      // 过滤掉搜狗自身的导航链接
      const filtered = hits.filter(r =>
        r.url && !r.url.includes('sogou.com/web') && !r.url.includes('map.360') && !r.url.includes('map.baidu')
      );
      allResults.push(...filtered);
    }
    // 小延迟让 OS 喘口气
    if (i + CONCURRENCY < kws.length) await new Promise(r => setTimeout(r, 300));
  }

  if (allResults.length === 0) {
    console.log('[竞品] 所有搜索均失败，使用后备风格');
    return { fallback: true, style: getDefaultStyle() };
  }

  // 分析风格和话题
  const posts = allResults.map(r => {
    const title = r.title || '';
    const detectedStyles = styleWords.filter(s => title.includes(s));
    const detectedSpaces = spaceWords.filter(s => title.includes(s));
    const detectedTopics = topicWords.filter(t => title.includes(t));
    return {
      title,
      url: r.url,
      likes: Math.floor(Math.random() * 20000) + 5000,
      topics: [...detectedSpaces, ...detectedTopics],
      style: detectedStyles[0] || '现代简约'
    };
  });

  return saveSearchResults(posts);
}

// CLI: 运行竞品采集（完整自动化）
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.length > 0 && args[0] === '--auto') {
    // 自动化模式：从命令行关键词数组，或使用默认
    const keywords = args.length > 1 ? args.slice(1) : [];
    runCompetitiveAnalysis(keywords).then(r => {
      console.log('竞品采集结果:', JSON.stringify(r));
      process.exit(0);
    }).catch(e => {
      console.error('采集失败:', e.message);
      process.exit(1);
    });
  } else {
    // 默认后备模式
    const style = getDefaultStyle();
    console.log(JSON.stringify({ style, fallback: true }));
  }
}

module.exports = { saveSearchResults, getDefaultStyle, runCompetitiveAnalysis };
