import uuid
import os

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

# from graph_chat.assistant import CtripAssistant, assistant_runnable, primary_assistant_tools
# from graph_chat.base_data_model import ToFlightBookingAssistant, ToBookCarRental, ToHotelBookingAssistant, \
#     ToBookExcursion
# from graph_chat.build_child_graph import build_flight_graph, builder_hotel_graph, build_car_graph, \
#     builder_excursion_graph
# from tools.flights_tools import fetch_user_flight_information
# from graph_chat.draw_png import draw_graph
from graph_chat.state import State
from tools.init_db import update_dates
from tools.tools_handler import create_tool_node_with_fallback, _print_event






from graph_chat.build_child_graph import build_environment_monitor_graph
from graph_chat.assistant import AgriAssistant, assistant_runnable
from graph_chat.base_data_model import ToEnvironmentMonitorAssistant



# 定义了一个流程图的构建对象
builder = StateGraph(State)
# 添加主助理
builder.add_node('primary_assistant', AgriAssistant(assistant_runnable))
builder.add_edge(START, "primary_assistant")

# 添加 助理的子工作流
builder = build_environment_monitor_graph(builder)


def route_primary_assistant(state: dict):
    """
    根据当前状态判断路由到子助手节点。
    :param state: 当前对话状态字典
    :return: 下一步应跳转到的节点名
    """
    route = tools_condition(state)  # 判断下一步的方向
    if route == END:
        return END  # 如果结束条件满足，则返回END
    tool_calls = state["messages"][-1].tool_calls  # 获取最后一条消息中的工具调用
    if tool_calls:
        if tool_calls[0]["name"] == ToEnvironmentMonitorAssistant.__name__:
            return "enter_environment_monitor"  # 跳转至技能节点
    raise ValueError("无效的路由")  # 如果没有找到合适的工具调用，抛出异常

# 条件边：符合谁的条件就跳转到谁（取决于之前对话对state的更新）
builder.add_conditional_edges(
    'primary_assistant',
    route_primary_assistant,
    # path_map的作用是，限定返回的值必须在以下值之中，否则报错
    [
        "enter_environment_monitor",
        END,
    ]
)


# 实例化一个用于保存/恢复内存状态的对象
memory = MemorySaver()

graph = builder.compile(
    # 检查点：如果工作流中发生中断或失败，memory 将用于恢复工作流的状态。
    checkpointer=memory,
)

from graph_chat.draw_png import draw_graph
draw_graph(graph, 'graph4.png')

# 生成随机的唯一会话id
session_id = str(uuid.uuid4())
update_dates()  # 每次测试的时候：保证数据库是全新的，保证，时间也是最近的时间

# 配置参数，包含乘客ID和线程ID
config = {
    "configurable": {
        # passenger_id用于我们的航班工具，以获取用户的航班信息
        "passenger_id": "3442 587242",
        # 检查点由session_id访问
        "thread_id": session_id,
    }
}

_printed = set()  # set集合，避免重复打印

# # 执行工作流
# while True:
#     question = input('用户：')
#     # 退出逻辑，目前只是样本，当用户输入的单词包括 q/exit/quit 时退出，也没有进行中译英
#     if question.lower() in ['q', 'exit', 'quit']:
#         print('对话结束，拜拜！')
#         break
#     else:
#         # 参数：input——对state的初始化更新，config——之前动态定义的配置字典，stream_mode——返回值（events）的格式，具体如下：
#         # "values"只返回最终状态值（最常用）
#         # "messages"返回 LangGraph 中间所有消息
#         # "all"	返回执行 trace，包括每个节点的日志记录等
#         events = graph.stream({'messages': ('user', question)}, config, stream_mode='values')
#         # 打印消息，直到中断发生（或者用户退出退出）——builder.compile中定义了，当涉及到敏感工具时就会中断
#         for event in events:
#             _print_event(event, _printed)

        