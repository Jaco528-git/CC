---
name: chart-generator
description: 按照用户自定义的matplotlib规范生成各类可视化图表。使用当用户提到生成图表、柱状图、折线图、饼图、散点图、雷达图、可视化数据时触发。
scope: global
license: MIT
---


# 图表生成Skill

## 适用场景

用户需要生成数据可视化图表时自动触发，支持两种生成方式：

1. 轻量快速图表：调用antv MCP工具直接生成
2. 定制化PNG图表：严格按照用户指定的matplotlib规范生成，输出到Downloads目录

## 执行流程

### Step 1: 确认需求

自动收集必要参数，缺失时询问用户：

- 图表类型（柱状图/折线图/饼图/散点图/雷达图/面积图等）
- 具体数据（包含维度和数值）
- 可选参数：标题、x轴标签、y轴标签、是否堆叠、颜色主题等

### Step 2: 按规范生成

使用 matplotlib 生成图表（仅此一种方式）：

#### Matplotlib生成规范（严格执行用户配置）

1. 必须使用Agg后端，无GUI模式
2. 全局字体设置：

   ```python
   plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
   plt.rcParams['axes.unicode_minus'] = False
   ```

3. 输出路径固定为用户Downloads目录（Windows: `%USERPROFILE%/Downloads/`，macOS/Linux: `~/Downloads/`），文件名按图表内容命名，dpi=150
4. 自动添加紧凑布局：`plt.tight_layout()`

### Step 3: 结果反馈

- Matplotlib生成：告知用户文件保存路径，确认生成成功

## 触发关键词

生成图表、画个图、柱状图、折线图、饼图、散点图、雷达图、面积图、数据可视化、matplotlib画图

## 禁止场景

- 非图表生成类请求
- 要求生成Excel/Word等非可视化格式的请求
