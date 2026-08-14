#!/bin/bash
# ============================================================
# 视频字幕一键处理 (云服务器版)
# 
# 用法（一条命令）：
#   curl -fsSL https://raw.githubusercontent.com/090516mc/video-subtitle-toolkit/main/cloud_run.sh | bash -s -- video.mkv
#
# 选项：
#   bash cloud_run.sh video.mkv                     # 默认：英文->中文软字幕
#   bash cloud_run.sh video.mkv --hardsub           # 硬字幕
#   bash cloud_run.sh video.mkv --model medium      # 更精准
#   bash cloud_run.sh video.mkv --lang ja --target zh-CN  # 日文->中文
# ============================================================

set -e

REPO="https://raw.githubusercontent.com/090516mc/video-subtitle-toolkit/main"
SCRIPT="run.py"

# ── 1. 安装系统依赖 ──
echo ">>> 检查系统依赖..."
if ! command -v ffmpeg &>/dev/null; then
    echo "安装 ffmpeg..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq ffmpeg
    elif command -v yum &>/dev/null; then
        sudo yum install -y ffmpeg
    else
        echo "请手动安装 ffmpeg: https://ffmpeg.org/download.html"
        exit 1
    fi
fi
echo "  ffmpeg: $(ffmpeg -version 2>&1 | head -1)"

# ── 2. 安装 Python 依赖 ──
echo ">>> 检查 Python 依赖..."
pip install -q openai-whisper deep-translator 2>/dev/null || pip3 install -q openai-whisper deep-translator

# ── 3. 下载最新 run.py ──
echo ">>> 下载处理脚本..."
curl -fsSL "$REPO/$SCRIPT" -o "$SCRIPT"

# ── 4. 运行 ──
echo ">>> 开始处理..."
python "$SCRIPT" "$@" || python3 "$SCRIPT" "$@"

# ── 5. 清理脚本自身 ──
rm -f "$SCRIPT"