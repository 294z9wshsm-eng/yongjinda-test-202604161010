#!/usr/bin/env node
/**
 * parse-search-markdown.js
 * 把 search.js 的 markdown 输出解析成结构化 JSON
 * 支持单行格式 "1. 标题 🔗 url"
 * 也支持多行格式（标题和🔗在不同行）
 */
const fs = require('fs');
const input = fs.readFileSync('/dev/stdin', 'utf-8');

const results = [];
// 单行格式: 序号. 标题 🔗 url
const singleLineRegex = /^(\d+)\.\s+(.+?)\s+🔗\s*(https?:\/\/\S+)/gm;
// 多行格式: 提取所有 🔗 行，然后关联到前一个非🔗行
const lines = input.split('\n');

let pendingTitle = '';
for (const line of lines) {
  const trimmed = line.trim();
  const titleMatch = trimmed.match(/^(\d+)\.\s+(.+)/);
  if (titleMatch) {
    pendingTitle = titleMatch[2].replace(/<[^>]+>/g, '').trim();
  }
  const urlMatch = trimmed.match(/🔗\s*(https?:\/\/\S+)/);
  if (urlMatch && pendingTitle) {
    results.push({ title: pendingTitle, url: urlMatch[1] });
    pendingTitle = '';
  }
}

console.log(JSON.stringify(results, null, 2));