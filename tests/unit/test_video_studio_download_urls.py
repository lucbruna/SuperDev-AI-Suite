import pytest

from modules.ai_video_studio.api.urls import DOWNLOAD_PREFIX, to_download_url


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (
            "/app/modules/downloads/videos/final.mp4",
            f"{DOWNLOAD_PREFIX}/videos/final.mp4",
        ),
        (
            r"C:\\DarkStudio\\modules\\downloads\\videos\\final cut.mp4",
            f"{DOWNLOAD_PREFIX}/videos/final%20cut.mp4",
        ),
        (
            "/app/modules/downloads/subtitles/legenda-á.srt",
            f"{DOWNLOAD_PREFIX}/subtitles/legenda-%C3%A1.srt",
        ),
    ],
)
def test_to_download_url_maps_download_tree_and_encodes_segments(path, expected):
    assert to_download_url(path) == expected


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/app/modules/downloads",
        "/app/modules/downloads/videos",
        "/app/modules/downloads/../secrets.txt",
        "/app/modules/downloads/videos/../../secrets.txt",
        "/app/modules/not-downloads/videos/final.mp4",
        "/tmp/downloads/videos/final.mp4",
        "/app/modules/cache/downloads/videos/final.mp4",
        "/app/modules/downloads//final.mp4",
    ],
)
def test_to_download_url_rejects_missing_or_unsafe_paths(path):
    assert to_download_url(path) is None
