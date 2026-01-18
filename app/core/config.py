import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings

try:
    import tomllib  # Python 3.11+
except ImportError:  # Python 3.10 及以下
    import tomli as tomllib  # type: ignore


class WebConfig(BaseSettings):
    dir: str
    title: str
    base_url: str
    logo_url: str


class FastAPIConfig(BaseSettings):
    title: str
    description: str
    host: str
    port: int


class WatchdogConfig(BaseSettings):
    monitor_dir: str
    json_file: str
    monitor_delay: float
    debounce_interval: float


class AppConfig(BaseModel):  # 使用 BaseModel 而不是 BaseSettings
    allowed_extensions: list[str]
    web: WebConfig
    fastapi: FastAPIConfig
    watchdog: WatchdogConfig

    # 前向引用，在类定义内部 AppConfig 类尚未完全创建完成，不能直接使用 AppConfig 作为类型注解
    @classmethod
    def load(cls, file_path: str = "config.toml") -> "AppConfig":
        """加载配置（工厂方法）"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"配置文件不存在: {file_path}")

        with open(file_path, "rb") as f:
            config_data = tomllib.load(f)
        return cls(**config_data)


# 全局配置实例
config: AppConfig = AppConfig.load()
