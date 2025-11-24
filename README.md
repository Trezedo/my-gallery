# 🖼️ 本地图库管理系统

## 🎯 项目初衷

本项目旨在利用 Python 开发一个功能完整的本地图库管理系统，主要解决以下需求：

- 📁 智能文件监控 - 自动监听指定文件夹的图片变化
- 🗂️ 自动分类整理 - 按照用户设定规则（如日期）自动整理图片
- 🌐 便捷浏览分享 - 通过浏览器查看图片并获取 Markdown 链接
- ⚡ 在线管理 - 支持移动、重命名、删除、回收站等操作
- ☁️ 静态部署 - 可部署到 Netlify 等静态托管服务

一个基于 Python FastAPI + Watchdog 的本地图库解决方案，自动监控图片文件夹并通过 Web 界面展示。

## ✨ 特性

- 👁️ **自动监控** - 使用 Watchdog 实时监控`img`目录的变化
- 🌐 **Web 展示** - FastAPI 提供优雅的图片浏览界面
- 📁 **自动索引** - 实时生成`images.json`索引文件
- 🎯 **零配置** - 开箱即用，无需复杂设置
- 📱 **响应式设计** - 适配各种设备屏幕

## 🏗️ 项目结构

```text
my-gallery/
├── app/
│   ├── core/
│   │   ├── config.py     # 配置读取和管理
│   │   ├── schemas.py    # 定义通用类型
│   ├── utils/
│   │   ├── generator.py  # 图片生成 json
│   │   └── observer.py   # Watchdog 文件监控
│   └── main.py           # FastAPI 应用主入口
├── img/                  # 📸 图片存储目录（被监控目录）
├── static/
│   ├── images.json       # 📋 自动生成的图片索引
│   └── index.js          # JavaScript 脚本
├── config.toml           # ⚙️ 配置文件
├── index.html            # 🎨 主页面模板
├── pyproject.toml        # 📦 项目配置和依赖
└── requirements.txt      # 📋 Python 依赖列表
```

## 🚀 快速开始

### 安装依赖

```bash
python -m venv .venv                   # 创建虚拟环境
.venv/Scripts/activate
pip install -r requirements.txt     # 添加依赖
```

### 启动服务

```bash
python -m app.main
```

### 访问界面

打开浏览器访问: `http://localhost:8000`

## ⚙️ 配置说明

编辑 `config.toml` 文件来自定义设置：

```toml
allowed_extensions = [".png", ".jpg", ".jpeg", ".gif", ".svg"] # 图片文件扩展名

[web]
title = "我的图库"
base_url = ""      # 基础 URL，用于生成图片链接，不填则使用 location.href
logo_url = ""      # 网站左上角 Logo URL，不填则使用默认图标

[fastapi]
host = "0.0.0.0"                            # 监听所有可用接口
port = 8000                                 # 监听端口
title = "图片监控服务"
description = "基于 FastAPI 和 Watchdog 的图库服务"

[watchdog]
monitor_dir = "img"                # 监控的图片目录，相对于项目根目录
json_file = "./static/images.json" # 保存 JSON 文件的路径，相对于项目根目录
monitor_delay = 0.2                # 监控延迟，单位秒
debounce_interval = 0.8            # 防抖间隔，单位秒
```

## 📖 使用指南

### 添加图片

1. 直接将图片文件放入 `img/` 目录
2. 系统会自动检测并更新索引
3. 刷新网页即可看到新图片

### 文件夹管理

- 在 `img/` 下创建子文件夹来分类图片
- 系统会自动识别文件夹结构
- Web 界面会按文件夹展示图片

### 访问图片

- 主页: `http://localhost:8000` - 完整图库浏览
- 直链: `http://localhost:8000/img/图片路径.jpg`

## 🔧 核心功能

### 文件监控 (app/utils/observer.py)

- 实时监控 `img` 目录的文件变化
- 支持新增、删除、移动操作
- 自动更新 `images.json` 索引

### Web 服务 (app/main.py)

- 提供静态文件服务
- 渲染图片浏览界面
- API 接口支持

### 配置管理 (app/utils/config.py)

- 统一配置读取
- 支持热重载
- 类型安全的配置项

## 🎯 API 接口

### 获取图片索引

```http
GET /api/images
```

响应示例:

```json
{
  "last_updated": "2024-01-01T12:00:00",
  "total_images": 42,
  "images": [
    {
      "name": "photo.jpg",
      "path": "img/photo.jpg",
      "size": 1024000,
      "modified": "2024-01-01T10:30:00"
    }
  ]
}
```

## 📦 依赖说明

主要依赖包 (详见 `requirements.txt`):

- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `watchdog` - 文件监控
- `toml` - 配置文件解析

## 🛠️ 开发指南

### 运行开发模式

```bash
python app/main.py
```

### 项目结构说明

- `app/main.py` - 应用入口点
- `app/utils/` - 工具模块
- `img/` - 用户图片存储
- `config.toml` - 应用配置

### 添加新功能

1. 在 `app/utils/` 中添加新模块
2. 在 `app/main.py` 中注册路由或服务
3. 更新 `config.toml` 添加配置项

## 🔄 工作流程

```text
本地图片文件
     ↓
Watchdog监控 (observer.py)
     ↓
生成/更新 images.json
     ↓
FastAPI服务 (main.py)
     ↓
Web界面展示 (index.html)
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

这个 README 完全基于你的实际项目结构编写。需要我为你生成对应的 `config.toml` 模板或补充任何其他文件吗？😊
