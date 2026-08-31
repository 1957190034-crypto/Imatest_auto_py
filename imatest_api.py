from imatest.it import ImatestLibrary
import json
from typing import Dict, Any

def run_module_on_image(imatest: ImatestLibrary, module_key: str, img_path: str,
                        root_dir: str, ini_file: str, op_mode: int) -> Dict[str, Any]:
    """
    执行单个模块的单张图片测试，返回解析后的字典。
    如果失败，抛出异常。
    """
    method_name = f"{module_key}_json"
    if not hasattr(imatest, method_name):
        raise AttributeError(f"Method {method_name} not found in ImatestLibrary")
    func = getattr(imatest, method_name)
    json_str = func(
        input_file=img_path,
        root_dir=root_dir,
        op_mode=op_mode,
        ini_file=ini_file
    )
    return json.loads(json_str)