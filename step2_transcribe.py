"""
步骤2：使用 OpenAI Whisper 进行语音识别
用法：
    python step2_transcribe.py <音频文件> [模型大小] [语言]
    
模型大小: tiny / small / medium / large（默认 small）
语言: en / ja / zh / auto（默认 en）
"""

import whisper
import json
import sys
import os


def find_ffmpeg():
    """确保 ffmpeg 在 PATH 中"""
    try:
        import imageio_ffmpeg
        ffmpeg_dir = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
    except ImportError:
        pass


def transcribe(audio_path, model_size="small", language="en"):
    find_ffmpeg()

    print(f"加载 Whisper 模型 ({model_size})...", flush=True)
    model = whisper.load_model(model_size)

    print("正在转录...", flush=True)
    result = model.transcribe(audio_path, language=language, word_timestamps=True)

    print(f"转录完成！共 {len(result['segments'])} 个片段", flush=True)

    # 保存结果
    json_path = os.path.splitext(audio_path)[0] + "_transcription.json"
    save_data = {
        "segments": [
            {
                "start": s["start"],
                "end": s["end"],
                "text": s["text"].strip()
            }
            for s in result["segments"]
        ],
        "full_text": result["text"]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"已保存到: {json_path}")
    return json_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python step2_transcribe.py <音频文件> [模型大小] [语言]")
        print("模型: tiny/small/medium/large (默认 small)")
        print("语言: en/ja/zh/auto (默认 en)")
        sys.exit(1)

    audio = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "small"
    lang = sys.argv[3] if len(sys.argv) > 3 else "en"
    transcribe(audio, model, lang)