"""
Location utilities - 地理位置相关工具
"""
import math
from typing import Tuple


def haversine_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float
) -> float:
    """
    计算两点之间的Haversine距离（公里）
    
    Args:
        lat1: 第一个点的纬度
        lon1: 第一个点的经度
        lat2: 第二个点的纬度
        lon2: 第二个点的经度
    
    Returns:
        两点之间的距离（公里）
    """
    R = 6371  # 地球半径（公里）
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon / 2) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def get_bounding_box(
    lat: float, 
    lon: float, 
    distance_km: float
) -> Tuple[float, float, float, float]:
    """
    获取以某点为中心、给定距离为半径的矩形边界框
    用于数据库经纬度范围查询优化
    
    Args:
        lat: 中心点纬度
        lon: 中心点经度
        distance_km: 半径（公里）
    
    Returns:
        (min_lat, max_lat, min_lon, max_lon)
    """
    # 1度纬度 ≈ 111公里
    lat_delta = distance_km / 111.0
    
    # 1度经度 ≈ 111 * cos(纬度) 公里
    lon_delta = distance_km / (111.0 * math.cos(math.radians(lat)))
    
    return (
        lat - lat_delta,  # 最小纬度
        lat + lat_delta,  # 最大纬度
        lon - lon_delta,  # 最小经度
        lon + lon_delta,  # 最大经度
    )


def is_within_distance(
    lat1: float, 
    lon1: float, 
    lat2: float, 
    lon2: float, 
    distance_km: float
) -> bool:
    """判断两点是否在指定距离内"""
    return haversine_distance(lat1, lon1, lat2, lon2) <= distance_km


def format_distance(distance_km: float) -> str:
    """格式化距离为人类可读字符串"""
    if distance_km < 1:
        return f"{int(distance_km * 1000)}m"
    else:
        return f"{distance_km:.1f}km"
