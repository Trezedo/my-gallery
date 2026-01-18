import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.core.config import config
from app.utils.observer import start_file_monitor
from app.utils.organizer import organize_images, preview_organize_images

# 设置项目根目录
root_path = Path(__file__).parent.parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    """生命周期管理器"""
    logger.info("🚀 FastAPI 服务启动中...")

    # 启动文件监控
    file_observer = start_file_monitor()
    logger.info("✅ 服务启动完成!")

    yield  # 应用运行期间

    # 关闭时停止监控
    if file_observer:
        file_observer.stop()
        file_observer.join()
        logger.info("🛑 文件监控已停止")


# 创建 FastAPI 应用
app = FastAPI(title=config.fastapi.title, description=config.fastapi.description, lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回首页"""
    html_path: Path = root_path / config.web.dir / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html 文件不存在")
    return FileResponse(html_path)


@app.get("/api/organize-preview")
async def preview_organize(mode: str):
    """预览图片整理结果"""
    try:
        preview = preview_organize_images(config.watchdog.monitor_dir, mode)
        return {"preview": preview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}") from e


@app.get("/api/organize-confirm")
async def confirm_organize(mode: str):
    """确认整理图片"""
    try:
        result = organize_images(config.watchdog.monitor_dir, mode)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"整理失败: {str(e)}") from e


if __name__ == "__main__":
    # 设置全局环境变量
    os.environ["PROJECT_ROOT"] = str(root_path)

    # 挂载静态文件
    app.mount("/img", StaticFiles(directory=root_path / config.watchdog.monitor_dir), name="images")
    app.mount("/static", StaticFiles(directory=root_path / config.web.dir / "static"), name="static_files")

    # 启动应用
    uvicorn.run(app, host=config.fastapi.host, port=config.fastapi.port, reload=False)
