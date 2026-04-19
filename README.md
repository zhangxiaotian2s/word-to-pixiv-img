# Word to Pixiv Anime Background Generator

> 将用户输入文案 → 自动生成高质量二次元背景图 → 优雅添加文字 → 返回成品图

仅使用 **doubao-seed-2.0-pro** 模型。

## 功能流程

1. **提示词优化**: 将用户简单文案转换成专业的 AI 绘画提示词，包含风格、构图、光照、氛围等细节
2. **图片生成**: 根据优化后的提示词调用 Doubao 文生图 API 生成二次元背景
3. **文字叠加**: 使用 Pillow 优雅地将原文叠加到图片上，多层保证可读性：
   - 半透明渐变背景
   - 文字描边
   - 投影
   - 支持智能位置选择

## 项目结构

```
├── src/
│   ├── config/          # 配置管理
│   ├── api/             # API 客户端
│   ├── core/            # 核心业务逻辑
│   ├── text_rendering/  # 文字渲染
│   ├── models/          # 数据类型和异常
│   └── utils/           # 工具函数
├── frontend/            # Vue.js 前端界面
├── outputs/             # 生成图片输出
├── fonts/               # 自定义字体（可选）
├── tests/               # 测试
└── examples/            # 示例脚本
    ├── simple_cli.py    # 命令行版本
    └── web_demo.py      # FastAPI Web 版本
```

## 安装

### 依赖

```bash
# 克隆项目
git clone <your-repo>
cd word-to-pixiv-img

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 Doubao API Key：

```env
DOUBAO_API_KEY=你的APIKey
DOUBAO_BASE_URL=https://api.doubao.com/v1
DOUBAO_MODEL=doubao-seed-2.0-pro

# 可配置默认图片尺寸
DEFAULT_IMAGE_WIDTH=1024
DEFAULT_IMAGE_HEIGHT=1024

# 可配置文字渲染默认参数
DEFAULT_TEXT_POSITION=bottom  # bottom, top, center, auto
```

## 使用

### 命令行使用

```bash
# 完整生成
python examples/simple_cli.py "樱花飘落的公园小路 春天"

# 只查看提示词优化结果（不生成图片，省API）
python examples/simple_cli.py "樱花飘落" --prompt-only

# 指定尺寸
python examples/simple_cli.py "雨夜车站" --width 1280 --height 720

# 指定文字位置
python examples/simple_cli.py "星空山顶" --position auto
```

### Web 界面

**后端 API**:
```bash
uvicorn examples.web_demo:app --reload --port 8000
```

访问 http://localhost:8000/docs 可以在线测试 API。

**前端界面**:
```bash
cd frontend
npm install
npm run dev
```

打开浏览器访问 Vite 显示的本地地址（通常是 http://localhost:5173）即可使用完整的交互界面。

### 代码中使用

```python
from src.core.pipeline import AnimeBackgroundPipeline
from src.models.types import TextStyle

pipeline = AnimeBackgroundPipeline()
result = pipeline.generate(
    user_text="夕阳下的城市街道",
    text_style=TextStyle(position="bottom", font_size=48),
    width=1024,
    height=1024,
)

if result.success:
    print(f"图片保存到: {result.image_path}")
    print(f"优化后提示词: {result.enhanced_prompt}")
```

## 文字位置选项

| 选项 | 说明 |
|------|------|
| `bottom` | 底部居中（默认，符合动漫海报习惯） |
| `top` | 顶部 |
| `center` | 居中 |
| `auto` | 智能选择 - 分析图像选择最合适区域放置文字 |

## 字体说明

### 自动字体选择

**新增功能** - 可以根据文字意境自动选择最合适的字体：

| 字体风格 | 适用场景 |
|----------|----------|
| 粗黑有力 | 口号、标语、标题、力量感文字 |
| 文艺宋体 | 诗文、抒情、文艺、感悟 |
| 清新手写 | 心情、日记、寄语、祝福 |
| 可爱圆润 | 萌系、甜美、二次元 |
| 现代无衬线 | 通用场景（默认） |

开启"根据文字意境自动选择字体"后，系统会分析文字关键词匹配合适风格。

### 安装免费字体

项目支持五种免费可商用字体，请下载后放入 `fonts/` 目录。详见 [fonts/README.md](fonts/README.md)。

### 回退机制

字体加载回退链，保证总能找到可用字体：

1. 优先使用 `./fonts/` 目录下对应风格的字体（自动选择）
2. 然后尝试系统字体（Noto Sans CJK、微软雅黑等）
3. 最后回退到 PIL 默认字体

如果需要自定义字体，将 `.ttf`/`.otf` 文件放到 `fonts/` 目录即可自动识别。

## 测试

```bash
# 运行单元测试（不需要 API key）
pytest tests/ -v -m "not e2e"

# 运行单元测试加覆盖率
pytest tests/ -v -m "not e2e" --cov=src

# 运行端到端测试（需要配置 API key）
pytest tests/test_e2e.py -v
```

## 示例输出

| 输入 | 输出 |
|------|------|
| `樱花飘落的公园小路` | 生成樱花公园背景，底部添加文字 |
| `雨夜中的日本车站` | 生成雨夜车站背景，文字渐变叠加 |

## 功能特性

- [x] 提示词自动优化增强
- [x] Doubao 文生图 API 集成
- [x] 智能文字排版与美化（半透明渐变背景 + 描边 + 投影）
- [x] 多种文字位置选择（底部/顶部/居中/智能自动）
- [x] 根据文字意境自动选择字体风格
- [x] 支持自定义字体，多种回退机制
- [x] RESTful API + 现代化 Vue 前端界面
- [x] 完整单元测试覆盖

## 许可证

MIT
