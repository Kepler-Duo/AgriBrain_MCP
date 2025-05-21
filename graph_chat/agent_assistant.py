from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

from graph_chat.base_data_model import CompleteOrEscalate
from graph_chat.llm_tavily import llm
from tools.environment_tools import get_current_weather, get_soil_moisture

  

# 环境监测助理 Prompt
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
            # "\n\n当前农田环境信息:\n<EnvData>\n{user_info}\n</EnvData>"
            "\n当前时间: {time}。"
            "\n\n如果用户需要帮助，并且您的工具都不适用，则"
            '请调用“CompleteOrEscalate”将任务返回主助理。不要浪费用户时间，也不要虚构工具或功能。',
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

tools = [get_current_weather, get_soil_moisture]

# 创建可运行对象
environment_monitor_runnable = environment_monitor_prompt | llm.bind_tools(
    tools + [CompleteOrEscalate]
)


# from langchain_core.messages import HumanMessage

# test_input = {"messages": [HumanMessage(content="请告诉我3号田的天气和土壤湿度。")]}
# output = environment_monitor_runnable.invoke(test_input)
# print(output)