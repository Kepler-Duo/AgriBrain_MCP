from pydantic import BaseModel, Field

class CompleteOrEscalate(BaseModel):  # 定义数据模型类 —— 只要继承了BaseModel，就可以被当做工具使用（信号型）
    """
    一个工具，用于标记当前任务为已完成和/或将对话的控制权升级到主助理，
    主助理可以根据用户的需求重新路由对话。
    """

    cancel: bool = True  # 默认取消任务
    reason: str  # 取消或升级的原因说明

    # 示例：分别展示了可能会调用类的三种情况 —— 任务完成，用户意图变更与权限不足、需要调用其它工具
    class Config:  # 内部类 Config: json_schema_extra: 这个字段包含了一些示例数据
        json_schema_extra = {
            "example": {
                "cancel": True,
                "reason": "用户改变了对当前任务的想法。",
            },
            "example2": {
                "cancel": True,
                "reason": "我已经完成了任务。",
            },
            "example3": {
                "cancel": False,
                "reason": "我需要搜索用户的电子邮件或日历以获取更多信息。",
            },
        }


class ToEnvironmentMonitorAssistant(BaseModel):
    """
    将工作转交给专门处理环境数据采集与分析的环境监测助理。
    """

    request: str = Field(
        description="用户想要了解的环境的地点"
    )
    
class ToDiseaseAndPestAssistant(BaseModel):
    """
    将工作转交给专门处理病虫害管理的助理。
    """
    img_path: str = Field(
        description="图像存储的地址"
    )
    
    request: str = Field(
        description="用户想要了解的病害或虫害的种类以及防治办法"
    )
    
    class Config:
        json_schema_extra = {
            "示例": {
                "img_path": "agent/wwc/graph2.png",
                "request": "我想知道这个作物发生什么了,怎么防治?。",
            }
        }

# TODO(wwc, 2025-05-21): 定义其他子助理的数据模型类