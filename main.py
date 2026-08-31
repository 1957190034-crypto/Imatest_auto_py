"""
Imatest IT 自动化测试主程序（优化版）
- 结果集中存放于 output/批次时间戳/ 下
- 断点续跑、进度条、日志
"""
import os
import sys
import yaml
import traceback
from datetime import datetime
from tqdm import tqdm

# 导入自定义模块
from imatest.it import ImatestLibrary
from file_utils import (
    get_image_paths, save_raw_json, save_metrics_csv,
    load_processed_set, save_processed_set, make_image_id
)
from imatest_api import run_module_on_image
from metrics_extractor import extract_key_metrics
from logger_config import setup_logger

# 初始化日志
logger = setup_logger()

def load_config(config_path="config.yaml"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, config_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    # 1. 加载配置
    config = load_config()
    images_base = config["paths"]["images_base"]
    output_base = config["paths"].get("output_base", "./output")  # 新增
    extensions = tuple(config["image_extensions"])
    modules_map = config["modules"]
    processing = config["processing"]
    imatest_cfg = config["imatest"]

    # 创建本次运行的批次标识（时间戳）
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_root = os.path.join(output_base, batch_id)
    os.makedirs(output_root, exist_ok=True)
    logger.info(f"输出根目录: {output_root}")

    # 解析 op_mode
    op_mode_str = imatest_cfg["op_mode"]
    op_mode = getattr(ImatestLibrary, op_mode_str, ImatestLibrary.OP_MODE_STANDARD)

    # 2. 初始化 Imatest 引擎
    logger.info("初始化 Imatest 引擎...")
    imatest = ImatestLibrary()

    # 3. 断点续跑记录
    processed_set = set()
    if processing["resume_enabled"]:
        processed_set = load_processed_set(processing["processed_record"])
        logger.info(f"加载断点记录：已处理 {len(processed_set)} 张图片")

    # 4. 遍历所有设备
    if not os.path.isdir(images_base):
        logger.error(f"图片根目录不存在：{images_base}")
        return

    for device_name in os.listdir(images_base):
        device_dir = os.path.join(images_base, device_name)
        if not os.path.isdir(device_dir):
            continue

        logger.info(f"\n===== 开始处理设备: {device_name} =====")

        for module_folder, module_key in modules_map.items():
            img_paths = get_image_paths(device_dir, module_folder, extensions)
            if not img_paths:
                logger.info(f"模块 {module_folder} 无图片，跳过")
                continue

            logger.info(f"  模块 {module_folder} 共 {len(img_paths)} 张图片")

            # 构建当前设备/模块的输出子目录（镜像原始结构）
            out_subdir = os.path.join(output_root, device_name, module_folder)
            os.makedirs(out_subdir, exist_ok=True)

            for img_path in tqdm(img_paths, desc=f"{device_name}/{module_folder}", unit="img"):
                img_name = os.path.basename(img_path)
                img_id = make_image_id(device_name, module_folder, img_path)

                if img_id in processed_set:
                    logger.debug(f"跳过已处理图片: {img_path}")
                    continue

                row = {
                    "device": device_name,
                    "module": module_folder,
                    "image": img_name,
                    "error": None
                }

                try:
                    # 调用 Imatest API
                    raw_data = run_module_on_image(
                        imatest, module_key, img_path,
                        imatest_cfg["root_dir"],
                        imatest_cfg["ini_file"],
                        op_mode
                    )

                    imatest.close_all_figs()

                    # 保存原始 JSON（可选）
                    if processing["save_raw_json"]:
                        base_name = os.path.splitext(img_name)[0]
                        json_path = os.path.join(out_subdir, f"{base_name}.json")
                        save_raw_json(raw_data, json_path)
                        logger.debug(f"JSON 已保存: {json_path}")

                    # 提取关键指标
                    metrics = extract_key_metrics(module_key, raw_data)
                    row.update(metrics)
                    row["error"] = ""

                    # 保存该图片的独立指标 CSV
                    if processing.get("save_per_image_csv", True):
                        base_name = os.path.splitext(img_name)[0]
                        csv_path = os.path.join(out_subdir, f"{base_name}_metrics.csv")
                        save_metrics_csv([row], csv_path)
                        logger.debug(f"指标 CSV 已保存: {csv_path}")


                except Exception as e:
                    error_msg = f"{type(e).__name__}: {str(e)}"
                    logger.error(f"处理图片失败 {img_path}: {error_msg}")
                    traceback.print_exc()
                    row["error"] = error_msg


                # 无论成功或失败，记录到已处理集合
                processed_set.add(img_id)

                if processing["resume_enabled"]:
                    save_processed_set(processing["processed_record"], processed_set)

    # 5. 终止引擎
    imatest.terminate_library()
    logger.info(f"所有设备测试完成，结果保存在 {output_root}，引擎已终止")

if __name__ == "__main__":
    main()
