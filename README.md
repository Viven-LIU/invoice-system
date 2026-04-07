# 发票信息提取系统

一个简单的网页应用，用于从发票图片中自动提取关键信息。

## 功能

- 上传发票图片
- 自动识别发票信息
- 保存记录到 Excel

## 技术栈

- 前端：HTML + CSS + JavaScript
- 后端：Flask + Python
- OCR：智谱 AI (glm-4.6v-flash)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在 `app.py` 中修改智谱 AI API Key：
```python
ZHIPU_API_KEY = "your-api-key"
```

### 3. 运行

```bash
python app.py
```

### 4. 访问

打开浏览器访问 http://127.0.0.1:5000

## 项目结构

```
├── app.py          # Flask 后端
├── index.html     # 前端页面
├── images/         # 图片存储目录
└── invoices.xlsx   # 发票记录 Excel 文件
```

## 使用方法

1. 点击 "Sale Invoice" 按钮上传发票图片
2. 系统自动识别发票信息
3. 识别结果会显示在页面上
4. 同时自动保存到 `invoices.xlsx`
