"""
步骤1：从视频中提取音频 (16kHz 单声道 WAV，适合 Whisper)
用法：
    python step1_extract_audio.py <视频文件路径> [输出音频路径]
"""

import subprocess
import sys
import os

# 自动查找 ffmpeg（优先使用 imageio-ffmpeg 自带的）
def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    return "ffmpeg"


def extract_audio(video_path, audio_path=None):
    if audio_path is None:
        base = os.path.splitext(video_path)[0]
        audio_path = base + "_audio.wav"

    ffmpeg = find_ffmpeg()
    print(f"使用 ffmpeg: {ffmpeg}")
    print(f"输入视频: {video_path}")
    print(f"输出音频: {audio_path}")

    cmd = [
        ffmpeg,
        "-i", video_path,
        "-vn",                # 不要视频
        "-acodec", "pcm_s16le",  # 16-bit PCM
        "-ar", "16000",       # 16kHz 采样率
        "-ac", "1",           # 单声道
        audio_path,
        "-y"                  # 覆盖已有文件
    ]

    subprocess.run(cmd, check=True)
    print("音频提取完成！")
    return audio_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python step1_extract_audio.py <视频文件> [输出音频.wav]")
        sys.exit(1)

    video = sys.argv[1]
    audio = sys.argv[2] if len(sys.argv) > 2 else None
    extract_audio(video, audio)