import os
import pandas as pd
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Environment")

# 初始化城市adcode DataFrame
city_df = pd.read_excel(
    'https://modelscope.oss-cn-beijing.aliyuncs.com/resource/agent/AMap_adcode_citycode.xlsx'
)

# 高德天气 API URL 和 key
AMAP_API_KEY = os.environ.get('AMAP_API_KEY', '')
AMAP_API_URL = 'https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key={key}'

def get_city_adcode(city_name: str) -> str:
    filtered_df = city_df[city_df['中文名'] == city_name]
    if filtered_df.empty:
        raise ValueError(f'未找到城市：{city_name}')
    return filtered_df['adcode'].values[0]

@mcp.tool()
async def get_current_weather(location: str) -> str:
    """
    获取指定地点的当前真实气象信息。
    """
    try:
        city_adcode = get_city_adcode(location)
        response = requests.get(AMAP_API_URL.format(city=city_adcode, key=AMAP_API_KEY))
        data = response.json()

        if data['status'] == '0':
            raise RuntimeError(f"API请求失败: {data['info']}")

        weather_info = data['lives'][0]
        weather = weather_info['weather']
        temperature = weather_info['temperature']
        humidity = weather_info['humidity']

        return f"{location}的当前天气为：{weather}，温度 {temperature}°C，湿度 {humidity}%。"

    except Exception as e:
        return f"天气信息获取失败: {str(e)}"

@mcp.tool()
async def get_soil_moisture(field_id: str) -> str:
    """
    获取指定农田区域的土壤湿度（模拟）。
    """
    return f"区域 {field_id} 的土壤湿度为 32%。"

@mcp.tool()
async def get_disease_pest_detection(img_path: str) -> str:
    """
    检测图像中农作物存在的病害或虫害（模拟）。
    """
    return f"图片 {img_path} 中存在叶锈病，置信度0.85。"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    
# TODO(wwc, 2025-05-21): 添加其他MCP工具,以及实现真实工具
