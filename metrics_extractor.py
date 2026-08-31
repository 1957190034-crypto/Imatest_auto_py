"""
从 Imatest 返回的原始 JSON 中提取关键指标。
根据实际返回结构调整字段路径。
"""
from typing import Dict, Any

def extract_key_metrics(module_key: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据模块类型提取关键指标。
    返回一个字典，键为指标名，值为数值或字符串。
    """
    metrics = {}

    # ---------- sfrplus (SFRplus) ----------
    if module_key == "sfrplus":
        results = raw_data.get("sfrplusResults", {})
        # CPIQ 锐度质量损失
        cpiq = results.get("CPIQ", {})
        metrics["sfrplus_QL_computerMonitor"] = cpiq.get("sfrComputerMonitor", {}).get("qualityLoss", [0])[0]
        metrics["sfrplus_QL_phoneDisplay"] = cpiq.get("sfrPhoneDisplay", {}).get("qualityLoss", [0])[0]
        # MTF50 中心值
        mtf50_summary = results.get("mtf50_CP_summary", [])
        metrics["sfrplus_MTF50_center"] = mtf50_summary[0] if mtf50_summary else 0.0
        # 过冲/下冲
        metrics["sfrplus_overshoot_pct"] = results.get("overshoot_Pct_summary", [0])[0]
        metrics["sfrplus_undershoot_pct"] = results.get("undershoot_Pct_summary", [0])[0]
        # 畸变
        metrics["sfrplus_distortion_SMIA_pct"] = results.get("SMIA_TV_Distortion_Pct", [0])[0]
        # 伽马和曝光误差
        metrics["sfrplus_gamma"] = results.get("gamma_from_stepchart", [0])[0]
        metrics["sfrplus_exposure_error_fstops"] = results.get("exposure_error_fstops", [0])[0]
        # 信噪比 Y_SNR_dB 均值
        snr_list = results.get("Y_SNR_dB", [])
        metrics["sfrplus_snr_dB_mean"] = sum(snr_list) / len(snr_list) if snr_list else 0.0
        # 横向色差最大像素
        ca_pixels = results.get("CA_areaPxls", [])
        metrics["sfrplus_lca_max_pixels"] = max(ca_pixels) if ca_pixels else 0.0

    # ---------- checkerboard (棋盘格畸变) ----------
    elif module_key == "checkerboard":
        results = raw_data.get("checkerboardResults", {})
        metrics["distortion_SMIA_pct"] = results.get("SMIA_TV_Distortion_Pct", [0])[0]
        metrics["distortion_max_geo_pct"] = results.get("worst_geometric_distortion_pct", [0])[0]
        metrics["distortion_ISO_pct"] = results.get("ISO_TV_Distortion_Pct", [0])[0]

    # ---------- colorcheck (Colorchecker Colorchecker) ----------
    elif module_key == "color_tone":
        results = raw_data.get("multitestResults", {})
        # 修正指标键名
        metrics["avg_deltaE_00"] = results.get("mean_Delta_E2000", [0])[0]  # 6.91
        metrics["max_deltaE_00"] = results.get("max_Delta_E2000", [0])[0]  # 17.5

        # 白平衡误差 Mired 均值（数组长度 6）
        mired_list = results.get("White_Bal_error_Mired", [])
        if mired_list:
            metrics["white_balance_error_mireds"] = sum(mired_list) / len(mired_list)
        else:
            metrics["white_balance_error_mireds"] = 0.0

        # 饱和度百分比（注意键名）
        metrics["camera_saturation_pct"] = results.get("mean_camera_Saturation_Pct", [0])[0]  # 89.62
    # ---------- random (随机纹理/噪声) ----------
    elif module_key == "random":
        results = raw_data.get("randomResults", {})
        cpiq = results.get("CPIQ", {})
        # texture_QL 可用
        metrics["texture_QL"] = cpiq.get("textureComputerMonitor", {}).get("qualityLoss", [0])[0]  # 12.15

        # MTF50 均值
        mtf50_list = results.get("MTF50_selected_units", [])
        metrics["mtf50_LWPH_mean"] = sum(mtf50_list) / len(mtf50_list) if mtf50_list else 0.0

    # ---------- flatfield (均匀性) ----------
    elif module_key == "flatfield":
        results = raw_data.get("flatfieldResults", {})
        metrics["luminance_uniformity_pct"] = results.get("uniformity_corners_sides_ctr_pct", [0])[0]
        metrics["nonuniformity_pct"] = results.get("nonuniformity_corners_sides_ctr_pct", [0])[0]
        # 色彩均匀性：取四个角落 ΔE00 的最大值
        delta_e_list = results.get("resTable_Delta_E00_ctr", [])
        if len(delta_e_list) >= 5:
            corners = delta_e_list[1:5]  # 索引1~4 对应四角
            metrics["color_uniformity_max_deltaE"] = max(corners)
        else:
            metrics["color_uniformity_max_deltaE"] = 0.0

    else:
        # 未知模块，返回空字典
        pass

    return metrics