"""
数据统计相关的辅助函数。
"""

import numpy as np

def robust_mean_std(data, iterations=3, sigma_clip=3.0):
    """
    使用sigma-clipping计算稳健的均值和标准差。

    参数:
        data (array-like): 输入数据。
        iterations (int): sigma-clipping的迭代次数。
        sigma_clip (float): 用于clipping的sigma倍数。

    返回:
        tuple: (稳健均值, 稳健标准差)
    """
    data = np.asarray(data)
    data = data[np.isfinite(data)] # 移除NaN和inf
    if len(data) == 0:
        return np.nan, np.nan

    current_data = data.copy()
    for _ in range(iterations):
        if len(current_data) < 2:
            break # 不足以计算std
        mean = np.nanmean(current_data)
        std = np.nanstd(current_data)
        if std == 0: # 如果所有值都相同
            break 
        
        lower_bound = mean - sigma_clip * std
        upper_bound = mean + sigma_clip * std
        
        mask = (current_data >= lower_bound) & (current_data <= upper_bound)
        if np.sum(mask) == len(current_data): # 如果没有数据被剔除
            break
        current_data = current_data[mask]
    
    robust_mean = np.nanmean(current_data)
    robust_std = np.nanstd(current_data)
    
    return robust_mean, robust_std

def weighted_mean(data, weights):
    """
    计算加权平均值。

    参数:
        data (array-like): 输入数据。
        weights (array-like): 对应的权重。

    返回:
        float: 加权平均值。
    """
    data = np.asarray(data)
    weights = np.asarray(weights)
    
    if len(data) != len(weights):
        raise ValueError("数据和权重的长度必须一致。")
    
    finite_mask = np.isfinite(data) & np.isfinite(weights) & (weights > 0)
    data = data[finite_mask]
    weights = weights[finite_mask]

    if len(data) == 0 or np.sum(weights) == 0:
        return np.nan
        
    return np.sum(data * weights) / np.sum(weights)

def weighted_std(data, weights):
    """
    计算加权标准差。

    参数:
        data (array-like): 输入数据。
        weights (array-like): 对应的权重。

    返回:
        float: 加权标准差。
    """
    data = np.asarray(data)
    weights = np.asarray(weights)

    if len(data) != len(weights):
        raise ValueError("数据和权重的长度必须一致。")

    finite_mask = np.isfinite(data) & np.isfinite(weights) & (weights > 0)
    data = data[finite_mask]
    weights = weights[finite_mask]

    if len(data) < 2 or np.sum(weights) == 0:
        return np.nan

    mean_w = weighted_mean(data, weights)
    if np.isnan(mean_w):
        return np.nan
        
    variance_w = np.sum(weights * (data - mean_w)**2) / np.sum(weights)
    # 对于有偏估计，有时会使用 (M-1)/M * sum(weights) 作为分母，其中M是非零权重的数量
    # M = np.sum(weights > 0)
    # if M > 1:
    #     variance_w = np.sum(weights * (data - mean_w)**2) / ((M-1)/M * np.sum(weights))
    # else:
    #     return np.nan

    return np.sqrt(variance_w)

if __name__ == '__main__':
    print("data_stats.py 包含数据统计的辅助函数。")

    # 示例 robust_mean_std
    d1 = np.array([1, 2, 3, 4, 5, 100])
    mean_r, std_r = robust_mean_std(d1)
    print(f"\n数据: {d1}")
    print(f"普通均值: {np.mean(d1):.2f}, 普通标准差: {np.std(d1):.2f}")
    print(f"稳健均值: {mean_r:.2f}, 稳健标准差: {std_r:.2f}")

    d2 = np.array([1, 1, 1, 1, 10, 10, np.nan, 12])
    mean_r2, std_r2 = robust_mean_std(d2)
    print(f"\n数据: {d2}")
    print(f"普通均值 (nanmean): {np.nanmean(d2):.2f}, 普通标准差 (nanstd): {np.nanstd(d2):.2f}")
    print(f"稳健均值: {mean_r2:.2f}, 稳健标准差: {std_r2:.2f}")

    # 示例 weighted_mean 和 weighted_std
    vals = np.array([1, 2, 3, 4, 5])
    wgts = np.array([1, 1, 10, 1, 1])
    mean_w = weighted_mean(vals, wgts)
    std_w = weighted_std(vals, wgts)
    print(f"\n数据: {vals}, 权重: {wgts}")
    print(f"加权均值: {mean_w:.2f}")
    print(f"加权标准差: {std_w:.2f}")

    vals_nan = np.array([1, 2, np.nan, 4, 5])
    wgts_zero = np.array([1, 0, 10, 1, 1])
    mean_w_edge = weighted_mean(vals_nan, wgts_zero)
    std_w_edge = weighted_std(vals_nan, wgts_zero)
    print(f"\n数据: {vals_nan}, 权重: {wgts_zero}")
    print(f"加权均值 (含nan/零权重): {mean_w_edge:.2f}")
    print(f"加权标准差 (含nan/零权重): {std_w_edge:.2f}")
