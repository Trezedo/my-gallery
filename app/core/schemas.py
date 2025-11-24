from pydantic import BaseModel, Field


class ImageInfo(BaseModel):
    """单个图片信息模型"""

    name: str = Field(default="", description="图片文件名")
    width: int = Field(default=0, description="图片宽度")
    height: int = Field(default=0, description="图片高度")
    size: int = Field(default=0, description="图片文件大小（字节）")


class ImageJsonObject(BaseModel):
    """图片响应模型"""

    last_updated: str = Field(default="", description="最后更新时间")
    count: int = Field(default=0, description="图片总数")
    base_url: str = Field(default="", description="基础 URL，用于生成图片链接")
    images: dict[str, list[ImageInfo]] = Field(default_factory=dict, description="图片文件名列表")
    urls: list[str] = Field(default_factory=list, description="图片URL列表")
