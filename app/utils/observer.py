import sys
import threading
import time
from pathlib import Path

from loguru import logger
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.core.config import config
from app.utils.generator import get_all_image_files, save_images_to_json

# 配置
ALLOWED_EXTENSIONS = config.allowed_extensions
IMAGE_DIR = config.watchdog.monitor_dir
JSON_FILE = config.watchdog.json_file
MONITOR_DELAY = config.watchdog.monitor_delay
DEBOUNCE_INTERVAL = config.watchdog.debounce_interval

# 日志设置
logger.remove()
logger.add(sys.stdout, level="INFO", format="<blue>[{time:HH:mm:ss}]</blue> {message}")


class ImageFolderHandler(FileSystemEventHandler):
    def __init__(self):
        self.timer = None
        self.lock = threading.Lock()

    def is_image(self, path: str):
        return Path(path).suffix.lower() in ALLOWED_EXTENSIONS

    def handle_event(self, path: str, action: str, emoji: str):
        if not Path(path).is_dir() and self.is_image(path):
            rel_path = Path(path).relative_to(IMAGE_DIR).as_posix()
            logger.info(f"{emoji} {action}: {rel_path}")
            self.schedule_update()

    def on_created(self, event):
        self.handle_event(str(event.src_path), "新增图片", "📸")

    def on_deleted(self, event):
        self.handle_event(str(event.src_path), "删除图片", "🗑️ ")

    def on_moved(self, event):
        if not Path(str(event.src_path)).is_dir() and self.is_image(str(event.src_path)):
            src_rel = Path(str(event.src_path)).relative_to(IMAGE_DIR).as_posix()
            dest_rel = Path(str(event.dest_path)).relative_to(IMAGE_DIR).as_posix()
            logger.info(f"📁 移动（重命名）图片: {src_rel} -> {dest_rel}")
            self.schedule_update()

    def schedule_update(self):
        with self.lock:
            if self.timer and self.timer.is_alive():
                self.timer.cancel()
            self.timer = threading.Timer(DEBOUNCE_INTERVAL, self.update_list)
            self.timer.start()

    def update_list(self):
        try:
            time.sleep(MONITOR_DELAY)
            images = get_all_image_files(IMAGE_DIR, ALLOWED_EXTENSIONS)
            save_images_to_json(images, JSON_FILE)
            count = sum(len(v) for v in images.values())
            logger.info(f"✅ 已更新 {count} 张图片")
        except Exception as e:
            logger.error(f"❌ 更新失败: {e}")
        finally:
            with self.lock:
                self.timer = None


def start_file_monitor():
    """启动文件监控"""
    Path(IMAGE_DIR).mkdir(exist_ok=True)

    images = get_all_image_files(IMAGE_DIR, ALLOWED_EXTENSIONS)
    save_images_to_json(images, JSON_FILE)
    count = sum(len(v) for v in images.values())
    logger.info(f"🎯 初始加载 {count} 张图片")

    observer = Observer()
    observer.schedule(ImageFolderHandler(), IMAGE_DIR, recursive=True)
    observer.start()

    logger.info(f"👀 监控中: {IMAGE_DIR}")
    return observer
