import re
from pathlib import Path


def preview_organize_images(dir: str, organize_mode: str):
    """预览图片整理结果"""

    pass


def organize_images(dir: str, organize_mode: str):
    """确认整理图片"""

    pass


def plan_organization(source_dir: str, renumber: bool = False) -> list[tuple[str, str]]:
    """生成整理计划，返回原路径和新路径的对应关系

    Args:
        source_dir (str): 图片源目录
        renumber (bool): 是否重新编号文件名，从1开始
    """
    plan = []
    date_counter = {}

    for file_path in Path(source_dir).iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp"}:
            # 提取时间信息和前缀
            match = re.search(r"^(.*?)(\d{4})(\d{2})(\d{2})(\d{2})?(\d{2})?(\d{2})?", file_path.stem)
            if match:
                # 分组匹配结果
                groups = match.groups()
                prefix = groups[0].rstrip("-")  # 前缀，去除末尾的连字符
                year, month, day = groups[1], groups[2], groups[3]
                time_str = "".join(groups[i] for i in range(4, 7) if groups[i] is not None)

                # 构建新路径
                dir_name = f"{year}-{month}"

                if renumber:
                    dir_key = dir_name
                    count = date_counter.get(dir_key, 1)
                    new_name = f"{count}{file_path.suffix}"
                    date_counter[dir_key] = count + 1
                else:
                    # 保留前缀，构建新文件名
                    if prefix:  # 如果有前缀
                        if time_str:
                            new_name = f"{prefix}-{day}{time_str}{file_path.suffix}"
                        else:
                            new_name = f"{prefix}-{day}{file_path.suffix}"
                    else:  # 如果没有前缀，使用原来的逻辑
                        new_name = f"{day}{time_str}{file_path.suffix}" if time_str else file_path.name

                new_path = Path(source_dir) / dir_name / new_name
                plan.append((file_path.as_posix(), new_path.as_posix()))

    return plan


def execute_organization(plan: list[tuple[str, str]]) -> None:
    """执行整理计划，实际移动文件"""
    for old_path, new_path in plan:
        Path(new_path).parent.mkdir(parents=True, exist_ok=True)
        Path(old_path).rename(new_path)


if __name__ == "__main__":
    # 第一步：生成整理计划
    plan = plan_organization("../../img", renumber=False)

    # 查看计划
    if len(plan) == 0:
        print("未发现可整理的图片。")
    else:
        for old_path, new_path in plan:
            print(f"{old_path} -> {new_path}")

    # 第二步：确认执行整理
    execute_organization(plan)
