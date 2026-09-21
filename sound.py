"""
sound.py —— 程序化合成音效 + 胜利旋律
不加载任何外部音频文件，全部用 Python math 生成 sine 波 PCM 数据。
"""
import math
import struct
import pygame

SAMPLE_RATE = 44100

_mixer_ok = False


def init():
    global _mixer_ok
    try:
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        _mixer_ok = True
    except pygame.error:
        _mixer_ok = False


def _make_tone(freq, duration, volume=0.3, decimate=8):
    """单个 sine 音符，快速衰减"""
    n = int(SAMPLE_RATE * duration)
    buf = bytearray()
    for i in range(n):
        t = i / SAMPLE_RATE
        sample = math.sin(2 * math.pi * freq * t)
        env = math.exp(-t * decimate)
        val = int(sample * env * volume * 32767)
        buf += struct.pack('<h', max(-32767, min(32767, val)))
    return bytes(buf)


def _make_sequence(notes, gap_ms=30):
    """把一串 (freq, duration, volume) 拼成一段连续的旋律"""
    buf = bytearray()
    for freq, dur, vol in notes:
        buf += _make_tone(freq, dur, vol)
        # 音符间短停顿（静音）
        n_gap = int(SAMPLE_RATE * gap_ms / 1000)
        buf += b'\x00\x00' * n_gap
    return bytes(buf)


# ── 频率表（Hz） ──
C5, D5, E5, F5, G5, A5, B5 = 523, 587, 659, 698, 784, 880, 988
C6, E6, G6 = 1047, 1319, 1568

# 预生成
def _build():
    global _sounds
    if not _mixer_ok:
        return
    try:
        _sounds = {
            # 飞出：短高音
            'fly':     pygame.mixer.Sound(buffer=_make_tone(A5, 0.10, 0.35)),
            # 碰撞：柔和低频"嗡"声（不是刺耳撞击）
            'blocked': pygame.mixer.Sound(buffer=_make_tone(220, 0.22, 0.28, decimate=5)),
            # 胜利：欢快的上行旋律 C E G C（约 1.2 秒）
            'win':     pygame.mixer.Sound(buffer=_make_sequence([
                (C5, 0.18, 0.35),
                (E5, 0.18, 0.35),
                (G5, 0.18, 0.35),
                (C6, 0.30, 0.40),
            ])),
            # 失败：下行的阴郁旋律
            'lose':    pygame.mixer.Sound(buffer=_make_sequence([
                (G5, 0.18, 0.30),
                (E5, 0.18, 0.30),
                (D5, 0.28, 0.30),
            ])),
        }
    except Exception:
        _sounds = {}


_sounds = {}


def play(name):
    if not _mixer_ok:
        return
    if not _sounds:
        _build()
    s = _sounds.get(name)
    if s:
        s.play()
