# main.py
import uuid
import os
import asyncio  

from langchain_core.messages import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from graph_chat.state import State
from tools.init_db import update_dates
from tools.tools_handler import create_tool_node_with_fallback, _print_event

from graph_chat.build_child_graph import build_environment_monitor_graph, build_disease_pest_graph
from graph_chat.assistant import AgriAssistant, assistant_runnable
from graph_chat.base_data_model import ToEnvironmentMonitorAssistant, ToDiseaseAndPestAssistant


async def main():  # 将主逻辑包装成 async 函数
    # 定义了一个流程图的构建对象
    builder = StateGraph(State)
    # 添加主助理
    builder.add_node('primary_assistant', AgriAssistant(assistant_runnable))
    builder.add_edge(START, "primary_assistant")

    # await 异步函数,适配mcp工具
    builder = await build_environment_monitor_graph(builder)
    builder = await build_disease_pest_graph(builder)
    # TODO(wwc, 2025-05-21): 这里可以添加更多的子助手节点,确保是异步函数

    def route_primary_assistant(state: dict):
        """
        根据当前状态判断路由到子助手节点。
        :param state: 当前对话状态字典
        :return: 下一步应跳转到的节点名
        """
        route = tools_condition(state)  # 判断下一步的方向
        print("route:", route)
        if route == END:
            return END  # 如果结束条件满足，则返回END
        print("state:", state["messages"][-1])
        tool_calls = state["messages"][-1].tool_calls  # 获取最后一条消息中的工具调用
        if tool_calls:
            print(f"tool_calls_name: {tool_calls[0]["name"]}")
            if tool_calls[0]["name"] == ToEnvironmentMonitorAssistant.__name__:
                return "enter_environment_monitor"  # 跳转至环境监测技能节点
            if tool_calls[0]["name"] == ToDiseaseAndPestAssistant.__name__:
                return "enter_disease_pest"  # 跳转至病虫害管理技能节点
        raise ValueError("无效的路由")  # 如果没有找到合适的工具调用，抛出异常

    # 条件边：符合谁的条件就跳转到谁（取决于之前对话对state的更新）
    builder.add_conditional_edges(
        'primary_assistant',
        route_primary_assistant,
        [
            "enter_environment_monitor",
            "enter_disease_pest",
            # TODO(wwc, 2025-05-21): 这里可以添加更多的条件边,跳转自助理
            END,
        ]
    )

    # 实例化一个用于保存/恢复内存状态的对象
    memory = MemorySaver()

    graph = builder.compile(
        checkpointer=memory,
    )

    # 初始化状态，只初始化一次！
    state = {
        "messages": [],
        "user_info": "当前农田状态：\n- 温度：25℃\n- 湿度：60%\n- 土壤pH：6.8",
    }

    from graph_chat.draw_png import draw_graph
    draw_graph(graph, 'graph.png')

    # 生成随机的唯一会话id
    session_id = str(uuid.uuid4())
    # update_dates()  # 每次测试的时候：保证数据库是全新的，保证，时间也是最近的时间

    # 配置参数，包含用户ID和线程ID
    config = {
        "configurable": {
            # passenger_id用于我们的航班工具，以获取用户的航班信息
            "user_id": "3442 587242",
            # 检查点由session_id访问
            "thread_id": session_id,
        }
    }

    _printed = set()  # set集合，避免重复打印

    # 执行工作流
    while True:
        question = input('用户：')
        # 退出逻辑，目前只是样本，当用户输入的单词包括 q/exit/quit 时退出，也没有进行中译英
        if question.lower() in ['q', 'exit', 'quit']:
            print('对话结束，拜拜！')
            break
        else:
            # # 参数：input——对state的初始化更新，config——之前动态定义的配置字典，stream_mode——返回值（events）的格式
            # events = graph.stream({'messages': ('user', question)}, config, stream_mode='values')
            # # 打印消息，直到中断发生（或者用户退出退出）——builder.compile中定义了，当涉及到敏感工具时就会中断
            # for event in events:
            #     _print_event(event, _printed)
            # 使用 astream 异步流式处理事件
            async for event in graph.astream({'messages': ('user', question)}, config, stream_mode='values'):
                _print_event(event, _printed)


if __name__ == "__main__":
    asyncio.run(main())  # 使用 asyncio 运行异步主函数
    
# TODO(wwc, 2025-05-21): 更改为后端形式，而非目前的命令行形式