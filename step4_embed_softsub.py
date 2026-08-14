"""
步骤4：将字幕嵌入视频（软字幕 - 可开关）
用法：
    python step4_embed_softsub.py <视频文件> <字幕SRT文件> [输出视频路径]

软字幕保留原始视频画质，播放时可选择开启/关闭字幕。
"""

import subprocess
import sys
import os


def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def embed_softsub(video_path, srt_path, output_path=None):
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = base + "_softsub" + ext

    ffmpeg = find_ffmpeg()
    print(f"输入视频: {video_path}")
    print(f"字幕文件: {srt_path}")
    print(f"输出视频: {output_path}")

    cmd = [
        ffmpeg,
        "-i", video_path,
        "-i", srt_path,
        "-map", "0",           # 保留原始所有流
        "-map", "1",           # 添加字幕流
        "-c", "copy",          # 视频音频无损复制
        "-c:s", "srt",         # 字幕编码
        "-metadata:s:s:1", "language=chi",
        "-metadata:s:s:1", "title=Chinese",
        output_path,
        "-y"
    ]

    subprocess.run(cmd, check=True)
    print("软字幕嵌入完成！播放时选择 Chinese 字幕轨道即可。")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python step4_embed_softsub.py <视频文件> <字幕SRT> [输出视频]")
        sys.exit(1)

    video = sys.argv[1]
    srt = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    embed_softsub(video, srt, out)