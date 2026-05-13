# 2026-05-13 下午学习

## 自主深入学习：Node.js 事件循环与并发模型

### 切入点：竞品采集的性能瓶颈
今天的竞品采集每个关键词串行搜索，5个关键词 × ~5秒 = 25秒。如果并发，理论上3-5秒搞定。
这是一个真实的高并发优化场景。

### 学习目标（本周）
1. 搞懂 Node.js 事件循环阶段（libuv）
2. 理解 Promise.then / setTimeout / process.nextTick / I/O async 的执行顺序
3. 能分析竞品采集流程，写出并发优化版本
4. 理解并发≠并行（单线程事件循环）

### 具体问题
```js
// 当前串行（慢）
for (const kw of keywords) {
  const hits = searchKeyword(kw);
  results.push(...hits);
  await new Promise(r => setTimeout(r, 500));
}

// 目标：并发（快）
const allResults = await Promise.all(keywords.map(kw => searchKeyword(kw)));
```

### 待验证的问题
- `Promise.all` 在 Node.js 事件循环里哪个阶段执行回调？
- `execSync` 是同步阻塞，会卡住事件循环吗？
- 如果搜索是 I/O 密集型，改成 `exec`（异步）后能并发吗？
- 并发数过大的话会怎样？（文件描述符耗尽/资源抢占）

### 下一步
找到 Node.js 事件循环文档，验证上述问题的答案，
然后改写 `cron-competitive-analysis.js` 的搜索部分为并发版本。

---

## 16:00-17:00 自主深入学习：Node.js 并发模型 + libuv 线程池

### 成果
并发版竞品采集打通 ✅

**性能对比：**
- 串行（execSync + for...of await）: ~25秒（5关键词 × 5秒/个）
- 并发（exec 异步 + Promise.all 批次）: ~7秒（3并发批次 + 解析）

**根因分析（libuv 线程池）：**
- Node.js 所有 I/O（spawn/dns/fs）走 libuv 线程池，默认 **4 线程**
- 两层嵌套 exec() 造成线程池耗尽 → 内层回调饿死 → SIGKILL
- fix: 外层 exec() 异步启动搜索，内层 execSync() 同步解析（不占线程池）

**学到的工程原则：**
- 进程启动用 exec()（异步非阻塞），进程内部解析用 execSync()（同步，不占线程池）
- 两层异步 I/O 嵌套要警惕线程池竞争
- 并发 ≠ 并行：Node.js 单线程事件循环里 exec() 是非阻塞的，但子进程 spawn 操作受线程池限制

### 新增文件
- `parse-search-markdown.js`（搜索结果解析器）
- `cron-competitive-analysis.js` 自动版（并发 + 修复路径 bug）

---

## 16:14-16:30 自主深入学习：XHS 反爬机制 + TLS/HTTPS 协议

### 真实问题
小红书 `formula-runtime` 反爬：node 原生 http 请求返回登录页，但 Playwright 浏览器请求正常。

### 学到的知识点

**TLS/HTTPS 协议基础：**
- TLS 握手流程：ClientHello → ServerHello → 证书验证 → 密钥交换 → 加密通信
- XHS 使用 **TLS 1.3** + `TLS_AES_256_GCM_SHA384`（现代最强密码套件之一）
- 证书：*.xiaohongshu.com，签发者 DNSPod（国内 CA）
- TLS 1.3 相比 1.2：1-RTT（一次往返）完成握手，更安全更快速

**小红书反爬分析：**
- XHS 首页返回 302 重定向到 /explore（有初始 Cookie: acw_tc + abRequestId）
- API 端点返回 500 + `create invoker failed, service: jarvis-gateway-default`（内部服务错误）
- `formula-runtime`：在浏览器里执行的 JS 会设置额外的 cookie（服务端检查这些 cookie 是否存在）
- 核心问题：**某些 cookie 由 JavaScript 计算生成**，而非服务器直接 Set-Cookie
- 没有执行 JS → 缺少关键 cookie → 服务端判定非真实浏览器 → 返回登录页或拦截

**Playwright 绕过原理：**
1. 真实浏览器建立 TLS 连接（完整 TLS 1.3 握手）✅
2. 执行页面 JS（formula-runtime 计算并设置 cookie）✅
3. 带着真实 cookie 发起后续请求 ✅
4. 服务端验证通过 → 正常数据响应 ✅

### 待深入
- HTTP/2 vs HTTP/1.1（多路复用，头部压缩）对反爬的影响
- Cookie 计算的原理（formula-runtime 混淆的具体算法）
- 不用 Playwright 的替代方案：JSelenium/Puppeteer remote/浏览器自动化框架
- 小红书 App API 能否绕过（APP 层校验 vs Web 层）

### 工程教训
1. **HTTPS 只是传输层安全**，TLS 握手成功 ≠ 业务层允许请求
2. **反爬在应用层**：检查 header/cookie/JS 执行痕迹，不只是 IP/频率
3. **Playwright 是万能解**，因为它真正跑了一个浏览器，什么反爬都能过
4. 遇到反爬先搞清楚在哪层拦截（DNS/TLS/HTTP header/JS/行为检测），再决定方案

---

## 16:25-16:30 数据库 + HTTP/2 学习

### 数据库分析：竞品库索引优化

**发现：**
- 现有索引：`idx_posts_date` (posted_date)，ORDER BY 时用了 TEMP B-TREE（内存排序，大数据量会慢）
- 修复：创建复合索引 `idx_posts_date_likes` (posted_date, likes DESC)
- 结果：排序从 TEMP B-TREE 变为索引扫描，查询时间 ~1.6ms

**SQL 执行计划解读（SQLite）：**
```
SEARCH ... USING INDEX idx_posts_date (posted_date=?)
`--USE TEMP B-TREE FOR ORDER BY  ← 文件排序（慢）
```

加了复合索引后：
```
SEARCH ... USING INDEX idx_posts_date_likes (posted_date=?)  ← 直接用索引排序（快）
```

**工程原则：**
- ORDER BY + WHERE 条件的列，可以组复合索引避免排序
- LIMIT 配合索引可以实现「最前 N 条」的高效检索
- 用 `EXPLAIN QUERY PLAN` 看执行计划，是性能分析的第一步

### HTTP/2 协议分析

**发现：**
- 小红书 web 层使用 **HTTP/1.1** over TLS 1.3（不支持 h2）
- ALPN 协商结果为 false（没协商出协议，服务端只接受 HTTP/1.1）
- 没有 HTTP/2 多路复用、header 压缩、server push 等优化

**HTTP/2 vs HTTP/1.1 关键区别：**
- 多路复用：一个 TCP 连接上并行多个请求（HTTP/1.1 需 pipeline 或多连接）
- Header 压缩（HPACK）：减少重复 header 传输
- Server Push：服务端主动推送资源
- 流控制：每个流独立控制，避免一个流拖慢其他流

**对反爬的影响：**
- 没有 HTTP/2 不影响反爬判断，反爬主要看 header/cookie/JS 执行
- 小红书的反爬是应用层（cookie 计算），不是协议层

### 工程教训汇总
1. **数据库**：`EXPLAIN QUERY PLAN` 是分析性能的第一工具
2. **复合索引**：WHERE + ORDER BY 的列可以组索引覆盖，避免排序
3. **HTTP/2**：TLS 1.3 和 HTTP/2 是两层协议，TLS 1.3 ≠ HTTP/2
4. **反爬分析层次**：DNS → TLS → HTTP header → 应用层(JS) → 行为层

---

## 16:32-16:45 代码审计 + Git 现状

### 发现的问题
**Playwright page.evaluate() 上下文错误（历史 bug）**
- `xhs-auto-publish.js` 里有 `function random(min,max)` → 传入 `page.evaluate()` → 浏览器里无定义 → ReferenceError
- 根因：浏览器 Node.js 上下文隔离，模块函数不自动注入浏览器

**今天日志分析**：
- `xhs-publish-playwright.js` 最近一次成功跑在 2026-05-10
- 有 3 个文件：`xhs-publish-playwright.js`（最新版）/ `xhs-publish.js` / `xhs-auto-publish.js`

### Git 现状
- 只有一个 branch `main`，无 CI/CD
- 今天改了 `.learnings/LEARNINGS.md` + `HEARTBEAT.md` + `MEMORY.md`
- `CloudFlare-AI-Insight-Daily` 以 embedded repo 存在，需要 `git rm --cached`

### 数据库现状（竞品库）
- 今天入库 61 条（新纪录），昨天 27 条
- 热词：卧室、小户型、爆改、收纳、客厅
- 今日热度：568,879（昨天 237,034）

### 待做
- [ ] Git 建分支策略（main/dev/feature）
- [ ] CI/CD 流程（GitHub Actions）
- [ ] XHS publish 的 page.evaluate random bug 需要修复
