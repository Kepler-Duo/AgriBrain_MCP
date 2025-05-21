# agent_assistant.py

from datetime import datetime
from typing import List, Union

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from graph_chat.base_data_model import CompleteOrEscalate
from graph_chat.llm_tavily import llm
from tools.environment_tools import get_current_weather, get_soil_moisture
from langchain_mcp_adapters.client import MultiServerMCPClient


# 初始化客户端
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            "args": ["MCP_Servers/math_server.py"],
            "transport": "stdio",
        },
        "environment": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
    }
)

# 环境监测 Prompt
environment_monitor_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "您是专门处理农田环境数据采集与分析的环境监测助理。"
            "当用户需要获取当前或历史的气象信息、土壤湿度、温度、PH值等环境指标时，主助理会将任务委派给您。"
            "请根据传感器数据或历史记录，为用户提供准确、详细的信息。"
            "在查询数据时，请坚持不懈。如果第一次查询无结果，请扩大范围（例如时间区间或空间范围）。"
            "如果您需要更多信息，或者用户的请求超出环境监测范围，请将任务升级回主助理处理。"
            "请记住，只有通过成功调用工具获得的环境数据才是有效的。不要猜测或编造不存在的数据。"
            "\n当前时间: {time}。"
            "\n\n如果用户需要帮助，并且您的工具都不适用，则"
            '请调用“CompleteOrEscalate”将任务返回主助理。不要浪费用户时间，也不要虚构工具或功能。',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())


disease_pest_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "您是专门处理图片分析的作物病虫害管理助理。"
            "当用户需要询问病虫害信息以及作物防治建议等问题时，主助理会将任务委派给您。"
            "请根据病虫害检测模型结果、病虫害防治手册和防治历史记录，为用户提供准确、详细的建议。"
            "在查询数据时，请坚持不懈。如果第一次查询无结果，请扩大范围（例如时间区间或空间范围）。"
            "如果您需要更多信息，或者用户的请求超出弄租屋病虫害管理范围，请将任务升级回主助理处理。"
            "请记住，只有通过成功调用工具获得的环境数据才是有效的。不要猜测或编造不存在的数据。"
            "\n当前时间: {time}。"
            "\n\n如果用户需要帮助，并且您的工具都不适用，则"
            '请调用“CompleteOrEscalate”将任务返回主助理。不要浪费用户时间，也不要虚构工具或功能。',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# TODO(wwc, 2025-05-21): 增添子助理的prompt

# 私有变量用于缓存
_initialized = False
_cached_tools = []
_cached_environment_runnable = None
_cached_disease_runnable  = None


async def _initialize_once():
    global _initialized, _cached_tools, _cached_environment_runnable, _cached_disease_runnable

    if _initialized:
        return

    # 实际异步加载工具
    tools = await client.get_tools()
    # print(tools)
    _cached_tools = tools + [CompleteOrEscalate]

    # 构建 runnable
    _cached_environment_runnable = environment_monitor_prompt | llm.bind_tools(_cached_tools)
    _cached_disease_runnable = disease_pest_prompt | llm.bind_tools(_cached_tools)

    _initialized = True


async def get_tools() -> List[Union[str, object]]:
    """获取已初始化的工具列表"""
    await _initialize_once()
    return _cached_tools


async def get_environment_monitor_runnable() -> Runnable:
    """获取已初始化的环境监测 Runnable 对象"""
    await _initialize_once()
    return _cached_environment_runnable

async def get_disease_pest_runnable() -> Runnable:
    """获取已初始化的病虫害管理 Runnable 对象"""
    await _initialize_once()
    return _cached_disease_runnable

# TODO(wwc, 2025-05-21): 增添子助理的runnable

async def get_crop_growth_runnable() -> Runnable:
    """获取已初始化的作物生长监测 Runnable 对象"""
    pass