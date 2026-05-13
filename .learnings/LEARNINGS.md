# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## Node.js 模块相对路径解析 bug（from 2026-05-13）
**Error**: `cron-competitive-analysis.js` 里 `path.join(DIR, '../../skills/...')` 找不到文件

**Root Cause**: `__dirname` 指向被加载文件所在目录，而非调用方目录。当 workspace/pipeline-taskflow/ 下的模块用 `../../skills/` 向上回退时，实际指向的是 `/Users/mac/.openclaw/skills/`，而真正的 skills 在 `/Users/mac/.openclaw/workspace/skills/`

**Fix**: 用硬编码绝对路径替代相对路径
```js
// ❌ 错误
const SEARCH_SCRIPT = path.join(DIR, '../../skills/web-anti-crawl-search/scripts/search.js');
// ✅ 正确
const SEARCH_SCRIPT = '/Users/mac/.openclaw/workspace/skills/web-anti-crawl-search/scripts/search.js';
```

**Best Practice**:
1. **Node.js 模块内不推荐用 `__dirname` + 相对路径** — 模块被多处 `require()` 时路径基准不一致
2. **推荐做法**：
   - 硬编码绝对路径（简单粗暴，最稳）
   - 或通过参数传入路径（更灵活）
   - 或在模块顶部声明 `ROOT_DIR = path.resolve(__dirname, '..')` 然后基于此计算
3. **CI/工程防护**：配置 ESLint `import/no-unresolved` 可以在跑 lint 时发现这类路径错误
4. **调试方法**：`node -e "console.log(require.resolve('模块路径'))"` 可以快速验证模块是否能找到

---

## Error Handling Principle (from 老大)
**每次错误都被立刻标记、显式纠正、并让纠正结果在下一轮生效**

When an error occurs:
1. **立刻标记** - Explicitly identify what went wrong
2. **显式纠正** - State the correct approach clearly
3. **下一轮生效** - Verify the fix works before continuing

**Example (from today)**:
- ❌ Error: osascript long JS returns empty → 改用无分号单行写法
- ❌ Error: workflow切换双击不生效 → 改用 app.loadGraphData()
- ❌ Error: VHS_VideoCombine 缺 format 参数 → 添加 "format": "video/h264-mp4"
---

## Node.js 嵌套 exec 回调 SIGKILL bug（from 2026-05-13）
**Error**: 并发优化后 Promise.all 里跑 searchKeyword()，内层 exec() 的回调永远不被触发，最终进程被 SIGKILL

**Root Cause**: libuv 的线程池默认 4 个线程（VIRT THREAD POOL）。外层 `exec()` 占用了所有线程，内层 `exec()` 要么排队等、要么直接失败。搜索（spawn 浏览器 Playwright）是 heavy I/O，等线程释放时主进程已超时被 kill

**Debug Method**:
```js
// 验证 libuv 线程池大小
console.log('threads:', process.env.UV_THREADPOOL_SIZE); // default: 4
```

**Fix**:
```js
// ❌ 错误：外层 exec 里直接调内层 exec（2层 I/O，共用线程池）
exec('outer 2>&1', callback(exec('inner', callback)));

// ✅ 正确：外层 exec 完成后，用 execSync 同步解析（不占线程池）
exec('outer 2>&1', callback(err, raw) => {
  const parsed = execSync('node parse.js', { input: raw });
});
```

**Engineering Principle**:
1. **libuv 线程池 = 4（默认）**，所有 async I/O（dns/fs/spawn）都从这里来
2. 两层 `exec()` 嵌套 = 2+ 层线程池占用。如果外层 I/O 阻塞内层，会死锁
3. **用 exec() 做进程启动，用 execSync() 做子进程内部解析** — 不额外占线程池
4. **并发 ≠ 并行**：`Promise.all + exec()` 能并发，但每个任务内的子 I/O 如果也用异步 exec 会产生竞争

**Next**: 研究 UV_THREADPOOL_SIZE=8 或改用 `child_process.spawn()` + 流式处理，绕过线程池限制

---

## Playwright page.evaluate() 浏览器上下文 vs Node.js 全局（from 2026-05-13）
**Error**: `page.evaluate: ReferenceError: random is not defined`

**Root Cause**: 
- `page.evaluate()` 的代码跑在**浏览器 JavaScript 上下文**里，不是 Node.js
- `Math.random()` 在浏览器里是内置的，不会报错
- 但 `process`、`require`、`node 里的全局 random()` 在浏览器里不存在

**日志里的真实场景**: `xhs-auto-publish.js` 里有 `function random(min,max)` 全局函数 → 传到 `page.evaluate()` → 浏览器里没定义 → ReferenceError

**Best Practice**:
```js
// ❌ 错误：在 page.evaluate 里用 Node.js API
await page.evaluate(() => process.env.SOME_VAR);

// ❌ 错误：在 page.evaluate 里用模块里的全局函数
await page.evaluate(() => random(100, 200));

// ✅ 正确：用 page.evaluate 的第二个参数传入
await page.evaluate(({ min, max }) => Math.floor(Math.random() * (max - min)) + min, { min: 100, max: 200 });

// ✅ 正确：把需要的数据序列化后传入
const data = readFromNode();
await page.evaluate((d) => useDataInBrowser(d), JSON.stringify(data));
```

**调试方法**:
```js
await page.evaluate(() => typeof someVariable); // 返回 'undefined' 或 'function'
```
