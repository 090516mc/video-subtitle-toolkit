"""
视频字幕一键处理工具
用法：python run.py <视频文件> [选项]

一条命令完成：提取音频 → 语音识别 → 翻译 → 生成字幕 → 嵌入视频

示例：
    python run.py video.mkv                          # 默认：英文→中文软字幕
    python run.py video.mkv --lang ja --target zh-CN # 日文→中文
    python run.py video.mkv --hardsub                # 烧录硬字幕
    python run.py video.mkv --model medium           # 使用更精准的模型
"""

import subprocess
import sys
import os
import argparse
import json


def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def ensure_ffmpeg_in_path():
    try:
        import imageio_ffmpeg
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
    except ImportError:
        pass


def extract_audio(video_path):
    audio_path = os.path.splitext(video_path)[0] + "_audio.wav"
    ffmpeg = find_ffmpeg()
    print(f"[1/5] 提取音频 -> {audio_path}")
    subprocess.run([
        ffmpeg, "-i", video_path, "-vn",
        "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        audio_path, "-y"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path


def transcribe(audio_path, model_size, language):
    import whisper
    json_path = os.path.splitext(audio_path)[0] + "_transcription.json"
    print(f"[2/5] Whisper 语音识别 (模型: {model_size}, 语言: {language})")

    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language=language, word_timestamps=True)

    save_data = {
        "segments": [
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in result["segments"]
        ],
        "full_text": result["text"],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
    print(f"  识别出 {len(save_data['segments'])} 个片段")
    return json_path


def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def translate_and_srt(json_path, source, target):
    from deep_translator import GoogleTranslator
    srt_path = os.path.splitext(json_path)[0] + f"_{target}.srt"
    print(f"[3/5] 翻译 {source} -> {target}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data["segments"]
    translator = GoogleTranslator(source=source, target=target)

    srt_lines = []
    for i, seg in enumerate(segments):
        text = seg["text"].strip()
        if not text:
            continue
        try:
            translated = translator.translate(text)
        except Exception:
            translated = text

        idx = len(srt_lines) // 4 + 1
        srt_lines.append(str(idx))
        srt_lines.append(f"{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}")
        srt_lines.append(translated)
        srt_lines.append("")

        if (i + 1) % 10 == 0:
            print(f"  已翻译 {i+1}/{len(segments)}")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    print(f"  字幕已保存: {srt_path}")
    return srt_path


def embed_softsub(video_path, srt_path):
    ffmpeg = find_ffmpeg()
    base, ext = os.path.splitext(video_path)
    out = base + "_softsub" + ext
    print(f"[4/5] 嵌入软字幕 -> {out}")

    subprocess.run([
        ffmpeg, "-i", video_path, "-i", srt_path,
        "-map", "0", "-map", "1",
        "-c", "copy", "-c:s", "srt",
        "-metadata:s:s:1", "language=chi",
        out, "-y"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


def burn_hardsub(video_path, srt_path, crf=20):
    ffmpeg = find_ffmpeg()
    base, ext = os.path.splitext(video_path)
    out = base + "_hardsub" + ext
    srt_fixed = srt_path.replace("\\", "/").replace(":", "\\:")
    print(f"[5/5] 烧录硬字幕 -> {out} (CRF={crf})")

    subprocess.run([
        ffmpeg, "-i", video_path,
        "-vf", f"subtitles='{srt_fixed}'",
        "-c:v", "libx264", "-crf", str(crf),
        "-preset", "fast", "-c:a", "copy",
        out, "-y"
    ], check=True)
    return out


def cleanup(video_path):
    base = os.path.splitext(video_path)[0]
    for f in [
        base + "_audio.wav",
        base + "_audio_transcription.json",
        base + "_audio_transcription_zh-CN.srt",
    ]:
        if os.path.exists(f):
            os.remove(f)


def main():
    parser = argparse.ArgumentParser(description="视频字幕一键处理工具")
    parser.add_argument("video", help="视频文件路径")
    parser.add_argument("--model", default="small",
                        choices=["tiny", "small", "medium", "large"],
                        help="Whisper 模型大小 (默认 small)")
    parser.add_argument("--lang", default="en", help="视频语言 (默认 en)")
    parser.add_argument("--target", default="zh-CN", help="字幕目标语言 (默认 zh-CN)")
    parser.add_argument("--hardsub", action="store_true", help="烧录硬字幕")
    parser.add_argument("--crf", type=int, default=20, help="硬字幕质量 18-23 (默认 20)")
    parser.add_argument("--keep", action="store_true", help="保留临时文件")

    args = parser.parse_args()
    video = args.video

    if not os.path.exists(video):
        print(f"错误：找不到文件 {video}")
        sys.exit(1)

    ensure_ffmpeg_in_path()

    print(f"视频: {video}")
    print(f"语言: {args.lang} -> {args.target}")
    print(f"模型: {args.model}")
    print(f"模式: {'硬字幕' if args.hardsub else '软字幕'}")
    print("-" * 50)

    audio = extract_audio(video)
    json_path = transcribe(audio, args.model, args.lang)
    srt = translate_and_srt(json_path, args.lang, args.target)

    if args.hardsub:
        output = burn_hardsub(video, srt, args.crf)
    else:
        output = embed_softsub(video, srt)

    if not args.keep:
        cleanup(video)
        print("  已清理临时文件")

    print("-" * 50)
    print(f"完成！输出文件: {output}")


if __name__ == "__main__":
    main()