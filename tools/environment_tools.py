from langchain_core.tools import tool

# TODO: 以MCP的格式导入工具
@tool
def get_current_weather(location: str) -> str:
    """
    获取指定地点的当前气象信息。
    """
    return f"地点 {location} 的当前天气为：晴，温度 25°C，湿度 40%。"

@tool
def get_soil_moisture(field_id: str) -> str:
    """
    获取指定农田区域的土壤湿度。
    """
    return f"区域 {field_id} 的土壤湿度为 32%。"
  
