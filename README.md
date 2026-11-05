# Vlog Shot Breakdown

**从成片反推拍摄脚本：拉片 → 切镜 → 抽帧 → 逐镜分析 → 输出可执行的拍摄表。**

A reverse-engineering workflow for Vlog cinematography: break a finished video into shots, analyze camera position, framing, movement, lighting and sound, then turn it into a reproducible shooting script.

![License: MIT / CC BY 4.0](https://img.shields.io/badge/License-MIT%20%2F%20CC%20BY%204.0-lightgrey.svg)

## 简介

看完一支喜欢的 Vlog，往往只记得“好看”，说不清每个镜头怎么拍。这套方法把“感觉”拆成可检查的字段：时间码、场景、机位、景别、运镜、构图、光线、声音，以及每个判断的确定性等级。

它输出的不是观后感，而是一张能直接照着拍的脚本表。用于学习拍摄手法，不用于搬运或复制他人作品。

## 核心能力

- **镜头边界检测**：调用 ffmpeg 场景分数输出候选切点，再用低阈值复核软切。
- **逐镜字段体系**：11 个维度覆盖时间、画面、机位、光线与声音，区分“可见事实”和“方法推断”。
- **确定性分级**：A 可见 / B 推断 / C 信息不足，避免把猜测写成事实。
- **脚本表生成**：CSV + 视频 → 带截图的 Excel 逐镜表，支持分组、缩略图宽度与打印分页。
- **完整案例**：一支 55.2 秒、18 个镜头的父亲节 Vlog 文本拆解，含逐镜笔记与复刻建议。
- **隐私与版权边界**：明确不收录原片、截图与儿童影像，并提供发布前的脱敏清单。

## 工作流

```text
片源
  ├─ 1. 读元数据：时长、分辨率、帧率、音轨
  ├─ 2. 场景检测：找出硬切点，得到镜头边界
  ├─ 3. 抽帧：每个镜头取代表性画面
  ├─ 4. 逐镜分析：机位、景别、运镜、构图、光线、声音
  ├─ 5. 输出脚本表：Excel / PDF / Markdown
  └─ 6. 复刻执行：按场景重排拍摄顺序，列机位与道具清单
```

完整的阈值选择、抽帧时机与分析方法见 [`docs/method.md`](docs/method.md)。

## 快速开始

前置：[ffmpeg](https://ffmpeg.org/)（含 `ffprobe`）、Python 3。

```bash
pip install -r requirements.txt
```

**1. 找候选切点：**

```bash
python tools/scene_detect.py --video input.mp4 --threshold 0.30
```

每个候选切点输出一行时间戳（秒）。快速摇镜可能被误判，需抽帧人工复核；软切可再用 `0.12` 复核。

**2. 填写逐镜 CSV**：列为 `shot, group, start, end, capture, scene, picture, camera, light, analysis, certainty`。字段含义见 [`docs/field-guide.md`](docs/field-guide.md)，可直接参考 [`examples/example-shots.csv`](examples/example-shots.csv)。

**3. 生成带截图的 Excel：**

```bash
python tools/build_shot_table.py \
  --video input.mp4 \
  --shots examples/example-shots.csv \
  --out out/breakdown.xlsx
```

生成的表包含：镜号、截图、时间码、时长、场景、画面、机位/景别/运镜、光线/声音/字幕、分析与复刻要点、确定性。也可从 [`templates/vlog-shot-breakdown-template.xlsx`](templates/vlog-shot-breakdown-template.xlsx) 手动填写。

## 案例

[父亲节 Vlog 逆向拆解（纯文本）](cases/fathers-day-vlog-7380698968457645350/README.md)

- 55.2 秒、18 个镜头，逐镜给出机位、景别、运镜、光线与复刻要点。
- 不含原片与截图，附 CSV、Markdown 表与纯文本 Excel。
- 配套 [`notes.md`](cases/fathers-day-vlog-7380698968457645350/notes.md) 记录关键镜头的反推过程。

## 确定性分级

| 级别 | 含义 | 典型内容 |
|---|---|---|
| **A** | 画面可直接确认 | 景别、人物动作、剪辑点、固定/运动状态 |
| **B** | 根据画面合理推断 | 机位高度、距离、运镜方式、光线方向 |
| **C** | 信息不足 | 实际焦段、光圈/ISO、补光设备、镜头外引导、拍摄顺序 |

不要把推断写成事实。每个镜头的“确定性”列必须填写。

## 隐私与版权

这套方法只用于学习拍摄手法。发布拆解结果前请阅读 [`docs/privacy-copyright.md`](docs/privacy-copyright.md)：

- 不发布原片，不搬运他人视频。
- 不暴露儿童正脸、学校、住址、小区、门牌、车牌、行程与全名。
- 截图中的窗外楼盘、镜面反射、照片墙都可能泄露隐私，发布前虚化或裁切。
- 引用旁白只做短句转述；商业使用需获得原片创作者与监护人授权。

本仓库不包含任何第三方视频、截图或儿童影像；示例数据为合成场景。

## 目录结构

```text
├── docs/
│   ├── method.md                 # 完整方法
│   ├── field-guide.md            # 字段定义与示例
│   └── privacy-copyright.md      # 隐私与版权边界
├── tools/
│   ├── scene_detect.py           # 场景检测，输出候选切点
│   └── build_shot_table.py       # CSV + 视频 → 带截图的 Excel
├── templates/                    # 空白逐镜表模板
├── examples/                     # 合成场景示例 CSV
├── cases/                        # 父亲节 Vlog 文本拆解
├── requirements.txt
├── LICENSE                       # 代码：MIT
└── LICENSE-docs                  # 文档：CC BY 4.0
```

## 参与贡献

欢迎 Issue / PR 补充字段、脚本与案例。提交案例前请先脱敏，不要附带原片或可识别个人身份的截图。

## 许可证

- 代码（`tools/`）：MIT，见 [`LICENSE`](LICENSE)。
- 文档与方法（`docs/`、本 README、`templates/`）：CC BY 4.0，见 [`LICENSE-docs`](LICENSE-docs)。
