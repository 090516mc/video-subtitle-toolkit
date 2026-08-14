"""
步骤3：翻译转录结果并生成 SRT 字幕文件
用法：
    python step3_translate_srt.py <转录JSON文件> [源语言] [目标语言] [输出SRT路径]
    
源语言默认 en，目标语言默认 zh-CN
"""

import json
import sys
import os
from deep_translator import GoogleTranslator


def format_timestamp(seconds):
    """将秒数转换为 SRT 时间戳格式 HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def translate_and_create_srt(json_path, source="en", target="zh-CN", output_path=None):
    if output_path is None:
        base = os.path.splitext(json_path)[0]
        output_path = base + f"_{target}.srt"

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data["segments"]
    print(f"共 {len(segments)} 个片段，正在翻译 {source} -> {target}...")

    translator = GoogleTranslator(source=source, target=target)

    srt_lines = []
    for i, seg in enumerate(segments):
        text = seg["text"].strip()
        if not text:
            continue

        try:
            translated = translator.translate(text)
        except Exception as e:
            print(f"  翻译第 {i+1} 段失败: {e}，使用原文")
            translated = text

        idx = len(srt_lines) // 4 + 1
        srt_lines.append(str(idx))
        srt_lines.append(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}")
        srt_lines.append(translated)
        srt_lines.append("")

        if (i + 1) % 10 == 0:
            print(f"  已翻译 {i+1}/{len(segments)}...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    print(f"字幕已保存到: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python step3_translate_srt.py <转录JSON> [源语言] [目标语言] [输出SRT]")
        print("示例: python step3_translate_srt.py audio_transcription.json en zh-CN")
        sys.exit(1)

    json_file = sys.argv[1]
    src = sys.argv[2] if len(sys.argv) > 2 else "en"
    tgt = sys.argv[3] if len(sys.argv) > 3 else "zh-CN"
    out = sys.argv[4] if len(sys.argv) > 4 else None
    translate_and_create_srt(json_file, src, tgt, out)