import os
from datetime import datetime

from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

# from graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, ToHotelBookingAssistant, \
    # ToBookExcursion
from graph_chat.base_data_model import ToEnvironmentMonitorAssistant, ToDiseaseAndPestAssistant
from graph_chat.llm_tavily import tavily_tool, llm
from graph_chat.state import State

# 自定义一个类，表示流程图的一个节点（适用与更复杂的，需要进行更多定制的场景）
class AgriAssistant:
    def __init__(self, runnable: Runnable):
        """
        初始化助手的实例。
        :param runnable: 可以运行对象，通常是一个Runnable类型的
        """
        self.runnable = runnable

    def __call__(self, state: State):
        """
        调用节点，执行助手任务
        :param state: 当前工作流的状态
        :param config: 配置: 里面有用户的信息
        :return:
        """
        while True:
            # 创建了一个无限循环，它将一直执行直到：从 self.runnable 获取的结果是有效的。
            # 如果结果无效（例如，没有工具调用且内容为空或内容不符合预期格式），循环将继续执行，
            # state = {**state, 'config': xxxxxx}  # 从配置中得到用户的信息，也追加到state，这里还没有接入，故先缺省
            result = self.runnable.invoke(state)
            # 如果，runnable执行完后，没有得到一个实际的输出
            if not result.tool_calls and (  # 如果结果中没有工具调用，并且内容为空或内容列表的第一个元素没有"text"，则需要重新提示用户输入。
                    not result.content
                    or isinstance(result.content, list)
                    and not result.content[0].get("text")
            ):
                messages = state["messages"] + [("user", "请提供一个真实的输出作为回应。")] # 给出一个隐式的用户输入
                state = {**state, "messages": messages}
            else:  # 如果： runnable执行后已经得到，想要的输出，则退出循环
                break
        return {'messages': result}

# 中央控制节点提示模板
from datetime import datetime
from langchain.prompts import ChatPromptTemplate

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "您是农事助理，主要职责是帮助用户解决农业生产中的问题，"
            "包括环境监测、作物管理、水肥管理、病害防治和农机调度。"
            "当用户请求涉及环境监测、作物管理、水肥管理、病害防治或农机调度相关的具体操作时，"
            "请通过调用相应的专门助理工具来完成这些任务。"
            "您自身无法直接执行这些专门的操作，必须委派给相应的助理。"
            "用户并不知道有不同的专门助理存在，因此请不要提及他们；只需通过函数调用静默委派任务。"
            "请始终为用户提供详细的农业技术信息，并在确定信息不可用之前，反复核查相关数据库。"
            "如果初次查询没有结果，请尝试扩大查询范围再搜索。"
            "如果多次扩大范围后仍无结果，方可告知用户。"
            # "\n\n当前农田环境信息:\n<EnvData>\n{user_info}\n</EnvData>" 
            "\n当前时间: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

# 创建可运行对象，绑定主助理提示模板和工具集，包括委派给专门助理的工具
assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    [
        ToEnvironmentMonitorAssistant, # 用于环境监测的专门助理
        ToDiseaseAndPestAssistant, # 用于病虫害管理的专门助理
    ]
)


