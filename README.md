# Vlog Shot Breakdown / Vlog 视频逆向拆解方法

一套从成片反推拍摄脚本的工作流：**拉片 → 切镜 → 抽帧 → 逐镜分析 → 输出可执行的拍摄脚本表**。  
用于学习优秀 Vlog 的机位、景别、运镜、光线与剪辑节奏，不用于搬运或复制他人作品。

A reverse-engineering workflow for Vlog cinematography: break a finished video into shots, analyze camera position, framing, movement, lighting and sound, then turn it into a reproducible shooting script.

---

## 1. 这套方法解决什么问题

看完一支喜欢的 Vlog，常见的问题是：

- 觉得“好看”，但说不清每个镜头怎么拍；
- 想复刻，却只有观后感，没有可执行的机位、景别、光线信息；
- 剪辑节奏靠感觉，不知道镜头长度如何分布；
- 团队沟通时，文字描述无法对齐画面。

这套方法把“感觉”拆成可检查的字段：

| 维度 | 要回答的问题 |
|---|---|
| 时间码 / 时长 | 这个镜头从几秒到几秒？平均镜长多少？ |
| 场景 | 客厅、餐厅、卧室、窗边、户外？ |
| 画面内容 | 谁、在哪、做什么？ |
| 机位 / 距离 | 相机多高、离主体多远？ |
| 景别 | 大特写 / 特写 / 近景 / 中景 / 全景？ |
| 运镜 | 固定、推、拉、摇、移、跟、升降？ |
| 构图 / 前景 | 主体在画面哪里？有没有前景遮挡？ |
| 光线 | 窗光、逆光、侧逆光、实用光源？ |
| 声音 / 字幕 | 同期声、旁白、音乐、环境声？ |
| 分析 / 复刻要点 | 这一镜的核心手法是什么？怎么复现？ |
| 确定性 | A 可见 / B 推断 / C 信息不足 |

---

## 2. 工作流总览

```text
片源
  │
  ├─ 1. 读元数据：时长、分辨率、帧率、音轨
  │
  ├─ 2. 场景检测：找出硬切点，得到镜头边界
  │
  ├─ 3. 抽帧：每个镜头取代表性画面 / 接触表
  │
  ├─ 4. 逐镜分析：机位、景别、运镜、构图、光线、声音
  │
  ├─ 5. 输出脚本表：Excel / PDF / Markdown
  │
  └─ 6. 复刻执行：按场景重排拍摄顺序，列机位与道具清单
```

### 2.1 读元数据

```bash
ffprobe -v error -show_format -show_streams input.mp4
```

记录：总时长、分辨率、帧率、视频编码、音频编码。  
这些信息决定时间码精度与抽帧方式。

### 2.2 场景检测切镜

```bash
ffmpeg -i input.mp4 \
  -vf "select='gt(scene,0.30)',showinfo" \
  -an -f null -
```

从输出中提取 `pts_time`，得到候选切点。  
阈值建议先用 `0.30`，再用 `0.12` 复核：低阈值会抓到快摇、快速下摇造成的误报，需要人工合并。

### 2.3 抽帧

每个镜头至少取三类帧：

- 起幅（镜头开始后 0.1–0.3 秒）
- 中段（动作或构图最完整的一刻）
- 落幅（切点前 0.1–0.3 秒）

静态镜头起落幅差别不大，保留一张代表性画面即可；运动镜头建议保留起幅 / 落幅对照。

```bash
ffmpeg -ss 12.30 -i input.mp4 -frames:v 1 frame_0012.jpg
```

### 2.4 逐镜分析

按 `docs/field-guide.md` 的字段逐项填写。  
先写“看得见的事实”（人物、动作、景别、剪辑点），再写“拍摄方法推断”（机位高度、焦段、补光），最后写“复刻要点”。

### 2.5 输出脚本表

用 `tools/build_shot_table.py` 把 CSV 与截图合成 Excel：

```bash
pip install -r requirements.txt
python tools/build_shot_table.py \
  --video input.mp4 \
  --shots examples/example-shots.csv \
  --out out/breakdown.xlsx
```

生成的表包含：镜号、截图、时间码、时长、场景、画面、机位/景别/运镜、光线/声音/字幕、分析/复刻要点、确定性。

### 2.6 复刻执行

把成片顺序打散，按“少移动孩子、少换光”重排：

1. 静物 / 空镜（无人物，光线稳定）
2. 同一场景的连续动作
3. 需要引导的互动镜头
4. 固定大景（三脚架）
5. 补拍特写

---

## 3. 仓库结构

```text
.
├─ README.md
├─ docs/
│  ├─ method.md                  # 完整方法说明
│  ├─ field-guide.md             # 字段定义与示例
│  └─ privacy-copyright.md       # 隐私与版权边界
├─ templates/
│  └─ vlog-shot-breakdown-template.xlsx
├─ tools/
│  ├─ build_shot_table.py        # CSV + 视频 → 带截图的 Excel 脚本表
│  └─ scene_detect.py            # 场景检测，输出候选切点
├─ examples/
│  └─ example-shots.csv          # 示例数据（合成场景，非真实视频）
├─ requirements.txt
├─ LICENSE                       # 代码：MIT
└─ LICENSE-docs                  # 文档：CC BY 4.0
```

---

## 4. CSV 字段

`tools/build_shot_table.py` 读取的 CSV：

| 字段 | 说明 | 示例 |
|---|---|---|
| `shot` | 镜号 | `01` |
| `group` | 段落名，可选；变化时插入分组行 | `A 静物开场` |
| `start` | 镜头开始时间（秒或 mm:ss.s） | `0.0` |
| `end` | 镜头结束时间 | `1.7` |
| `capture` | 截图时间；留空取 start/end 中点 | `1.0` |
| `scene` | 场景 | `客厅窗边` |
| `picture` | 画面内容 | `孩子举杯，逆光` |
| `camera` | 机位 / 景别 / 运镜 | `0.8m｜中近｜固定` |
| `light` | 光线 / 声音 / 字幕 | `强逆光｜环境｜N4` |
| `analysis` | 分析 / 复刻要点 | `对脸测光，保留窗高光` |
| `certainty` | A / B / C | `A/B` |

示例见 `examples/example-shots.csv`。

---

## 5. 确定性分级

| 级别 | 含义 | 写法建议 |
|---|---|---|
| **A** | 画面可直接确认 | 景别、人物动作、剪辑点、固定/运动状态 |
| **B** | 根据画面合理推断 | 机位高度、距离、运镜方式、光线方向 |
| **C** | 信息不足 | 实际焦段、光圈/ISO、补光设备、镜头外引导、拍摄顺序 |

> 不要把推断写成事实。每个镜头的“确定性”列必须填写。

---

## 6. 隐私与版权

这套方法只用于**学习拍摄手法**。发布或分享拆解结果前，请阅读 `docs/privacy-copyright.md`，重点：

- 不发布原片、不搬运他人视频；
- 不暴露儿童正脸、学校、住址、小区、门牌、车牌、行程、全名；
- 截图中的窗外楼盘、镜面反射、照片墙都可能泄露隐私，发布前虚化或裁切；
- 引用旁白只做短句转述，不整段复述；
- 商业使用需获得原片创作者与监护人授权。

本仓库不包含任何第三方视频、截图或儿童影像。示例数据为合成场景。

---

## 7. License

- 代码（`tools/`）：MIT，见 `LICENSE`
- 文档与方法（`docs/`、`README.md`）：CC BY 4.0，见 `LICENSE-docs`

欢迎 Issue / PR 补充字段、脚本与案例（请先脱敏）。
