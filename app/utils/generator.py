import os
import time
from pathlib import Path

from loguru import logger
from PIL import Image

from app.core.config import config
from app.core.schemas import ImageInfo, ImageJsonObject


def get_all_image_files(image_dir: str, allowed_extensions: list[str]) -> dict[str, list[ImageInfo]]:
    """获取所有图片文件"""
    images_info = ImageJsonObject()
    base_path = Path(image_dir)
    allowed_extensions_set = set(allowed_extensions)

    for file_path in base_path.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in allowed_extensions_set:
            continue

        folder = file_path.parent.relative_to(base_path).as_posix()
        if folder == ".":
            pass  # 根目录的图片不分组
        if folder not in images_info.images:
            images_info.images[folder] = []

        # 获取图片尺寸
        width, height = 0, 0
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except Exception as e:
            logger.warning(f"无法读取图片尺寸: {file_path} - {e}")

        images_info.images[folder].append(
            ImageInfo(name=file_path.name, width=width, height=height, size=file_path.stat().st_size)
        )

    return images_info.images


def save_images_to_json(images: dict[str, list[ImageInfo]], json_file: str) -> None:
    """保存图片列表到JSON文件"""
    try:
        data = ImageJsonObject(
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S"),
            count=sum(len(v) for v in images.values()),
            base_url=config.web.base_url,
            images=images,
            urls=[
                f"/img/{folder}/{image_info.name}" if folder != "." else f"/img/{image_info.name}"
                for folder, files in images.items()
                for image_info in files
            ],
        )

        # 格式化 JSON
        indent = 2
        json_str = data.model_dump_json(indent=indent, ensure_ascii=False)
        # 压缩部分结构使输出更紧凑
        json_str = json_str.replace("\n" + " " * indent * 4, " ").replace(
            "\n" + " " * indent * 3 + "}", " }"
        )

        # 保存文件
        project_root = Path(os.environ.get("PROJECT_ROOT", Path.cwd()))
        json_file_path = project_root / json_file.lstrip("/")
        with open(json_file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        logger.info(f"💾 已保存到 {json_file}")
    except Exception as e:
        logger.error(f"❌ 保存JSON文件失败: {e}")
