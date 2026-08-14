"""
步骤5：烧录字幕到视频画面（硬字幕 - 永久嵌入）
用法：
    python step5_burn_hardsub.py <视频文件> <字幕SRT文件> [输出视频路径] [CRF质量]

硬字幕会重新编码视频，字幕永久嵌入画面，任何播放器都能看到。
CRF 值越小质量越高（默认 20，推荐 18-23）。
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


def burn_hardsub(video_path, srt_path, output_path=None, crf=20):
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = base + "_hardsub" + ext

    # ffmpeg subtitles 滤镜需要正斜杠路径
    srt_path_fixed = srt_path.replace("\\", "/").replace(":", "\\:")

    ffmpeg = find_ffmpeg()
    print(f"输入视频: {video_path}")
    print(f"字幕文件: {srt_path}")
    print(f"输出视频: {output_path}")
    print(f"CRF 质量: {crf} (越小越清晰)")
    print("正在重新编码视频（需要一些时间）...")

    cmd = [
        ffmpeg,
        "-i", video_path,
        "-vf", f"subtitles='{srt_path_fixed}'",
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "fast",
        "-c:a", "copy",
        output_path,
        "-y"
    ]

    subprocess.run(cmd, check=True)
    print("硬字幕烧录完成！")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python step5_burn_hardsub.py <视频文件> <字幕SRT> [输出视频] [CRF]")
        print("CRF: 18-23, 默认 20（越小质量越高，文件越大）")
        sys.exit(1)

    video = sys.argv[1]
    srt = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    burn_hardsub(video, srt, out, quality)