# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### Ollama

- 安装在 `~/bin/ollama`（没有 root 权限，装在用户目录）
- 启动：`~/bin/ollama serve &`（后台运行）
- 当前模型：qwen2.5:1.5b（已下载）
- 路径未加入系统 PATH，每次调用需用完整路径或 `export PATH="$HOME/bin:$PATH"`
- API 端口：http://localhost:11434

---

Add whatever helps you do your job. This is your cheat sheet.
