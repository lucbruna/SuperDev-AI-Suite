"""Core constants and enumerations for the video studio.

All enums use str enum for JSON serialization compatibility.
"""
from enum import Enum, IntEnum


class Resolution(str, Enum):
    SD_480P = "640x480"
    HD_720P = "1280x720"
    FULL_HD_1080P = "1920x1080"
    QHD_1440P = "2560x1440"
    UHD_4K = "3840x2160"
    DCI_4K = "4096x2160"
    UHD_8K = "7680x4320"

    @property
    def width(self) -> int:
        return int(self.value.split("x")[0])

    @property
    def height(self) -> int:
        return int(self.value.split("x")[1])


class VideoCodec(str, Enum):
    H264 = "libx264"
    H265 = "libx265"
    VP8 = "libvpx"
    VP9 = "libvpx-vp9"
    AV1 = "libaom-av1"
    MPEG4 = "mpeg4"
    PRORES = "prores_ks"
    DNxHR = "dnxhd"


class AudioCodec(str, Enum):
    AAC = "aac"
    MP3 = "libmp3lame"
    OPUS = "libopus"
    VORBIS = "libvorbis"
    FLAC = "flac"
    PCM_S16LE = "pcm_s16le"
    PCM_S24LE = "pcm_s24le"


class ContainerFormat(str, Enum):
    MP4 = "mp4"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    AVI = "avi"
    GIF = "gif"
    HLS = "hls"


class PixelFormat(str, Enum):
    YUV420P = "yuv420p"
    YUV444P = "yuv444p"
    RGB24 = "rgb24"
    RGBA = "rgba"
    NV12 = "nv12"
    GRAY8 = "gray"


class ColorSpace(str, Enum):
    SRGB = "srgb"
    BT709 = "bt709"
    BT2020 = "bt2020"
    DCI_P3 = "dci-p3"
    ADOBE_RGB = "adobe-rgb"


class AspectRatio(str, Enum):
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    SQUARE_1_1 = "1:1"
    CINEMA_21_9 = "21:9"
    STANDARD_4_3 = "4:3"
    ULTRAWIDE_32_9 = "32:9"


class FrameRate(str, Enum):
    FPS_24 = "24"
    FPS_25 = "25"
    FPS_30 = "30"
    FPS_48 = "48"
    FPS_50 = "50"
    FPS_60 = "60"
    FPS_120 = "120"

    @property
    def value_int(self) -> int:
        return int(self.value)


class SceneType(str, Enum):
    INTRO = "intro"
    CONTENT = "content"
    TRANSITION = "transition"
    OUTRO = "outro"
    TITLE_CARD = "title_card"
    B_ROLL = "b_roll"
    HIGHLIGHT = "highlight"
    CREDITS = "credits"


class TransitionType(str, Enum):
    CUT = "cut"
    FADE = "fade"
    DISSOLVE = "dissolve"
    WIPE_LEFT = "wipe_left"
    WIPE_RIGHT = "wipe_right"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    SPIN = "spin"
    BLUR = "blur"


class AssetType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SUBTITLE = "subtitle"
    FONT = "font"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    VOICE_OVER = "voice_over"
    AVATAR = "avatar"
    TEMPLATE = "template"


class ExportStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    ENCODING = "encoding"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RenderPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


class QualityLevel(str, Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    ULTRA = "ultra"
    LOSSLESS = "lossless"


class AvatarStyle(str, Enum):
    REALISTIC = "realistic"
    ANIME = "anime"
    CARTOON = "cartoon"
    PIXEL_ART = "pixel_art"
    THREE_D = "3d"
    MINIMALIST = "minimalist"


class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class SubtitleFormat(str, Enum):
    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    TTML = "ttml"
    JSON = "json"


class AudioChannel(str, Enum):
    MONO = "mono"
    STEREO = "stereo"
    SURROUND_5_1 = "5.1"
    SURROUND_7_1 = "7.1"
    ATMOS = "atmos"


# ── Resolution Presets ────────────────────────────────────────────
RESOLUTION_PRESETS = {
    "youtube_1080p": {
        "resolution": Resolution.FULL_HD_1080P,
        "aspect_ratio": AspectRatio.LANDSCAPE_16_9,
        "frame_rate": FrameRate.FPS_30,
        "video_codec": VideoCodec.H264,
        "audio_codec": AudioCodec.AAC,
        "container": ContainerFormat.MP4,
    },
    "youtube_4k": {
        "resolution": Resolution.UHD_4K,
        "aspect_ratio": AspectRatio.LANDSCAPE_16_9,
        "frame_rate": FrameRate.FPS_30,
        "video_codec": VideoCodec.H265,
        "audio_codec": AudioCodec.AAC,
        "container": ContainerFormat.MP4,
    },
    "tiktok_vertical": {
        "resolution": Resolution.FULL_HD_1080P,
        "aspect_ratio": AspectRatio.PORTRAIT_9_16,
        "frame_rate": FrameRate.FPS_30,
        "video_codec": VideoCodec.H264,
        "audio_codec": AudioCodec.AAC,
        "container": ContainerFormat.MP4,
    },
    "instagram_reel": {
        "resolution": Resolution.FULL_HD_1080P,
        "aspect_ratio": AspectRatio.PORTRAIT_9_16,
        "frame_rate": FrameRate.FPS_30,
        "video_codec": VideoCodec.H264,
        "audio_codec": AudioCodec.AAC,
        "container": ContainerFormat.MP4,
    },
    "cinema_4k": {
        "resolution": Resolution.DCI_4K,
        "aspect_ratio": AspectRatio.CINEMA_21_9,
        "frame_rate": FrameRate.FPS_24,
        "video_codec": VideoCodec.PRORES,
        "audio_codec": AudioCodec.PCM_S24LE,
        "container": ContainerFormat.MOV,
    },
}