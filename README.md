# Imatest 自动化图像质量测试脚本框架

本系统是基于 Imatest IT 计算引擎与 Master 基准配置体系使用python语言开发的自动化图像质量测试框脚本，面向摄像头模组量产验证与图像质量评估场景，通过调用 Imatest IT Python API（imatest-it 库），基于 Master 配置文件，实现对 SFRplus（分辨率与综合画质分析）、Colorchecker（色彩还原与白平衡精度）、Flatfield（亮度均匀性与颜色阴影）、Random（纹理锐度与枯叶图分析）以及 Checkerboard（高密度畸变与MTF测量）五大核心测试模块的自动化调度与批量执行。系统通过配置文件驱动测试流程，可对多设备、多模块的测试图卡进行并行处理，输出结构化测试数据，为图像质量调优与产品一致性验证提供标准化、可追溯的量化评估依据。


## ✨ 核心功能

### 一、智能去重机制

框架具备智能去重功能，运行时会自动标记已测试图片，再次执行脚本时自动跳过已测试文件，避免重复测试，有效节省时间。

### 二、配置文件驱动

所有测试指标（如 MTF50、畸变、ΔE 等）均在 `imatest_base.ini` 配置文件中设定，测试过程完全由配置文件驱动，无需修改代码即可灵活调整测试参数。该配置文件基于 Imatest 在标准测试图上提取的指标参数生成，确保测试标准的一致性和可追溯性。

### 三、非交互式运行模式

脚本运行过程中不会弹出分析图或其他交互窗口，完全以非交互式后台模式执行，大幅减少内存占用，尤其适合处理大批量图片时显著提升测试效率。

### 四、结构化数据输出

测试完成后，所有结果统一保存至 `output/` 文件夹，按设备类型和测试模块分类存放，并以时间戳命名区分不同测试批次，确保数据管理清晰有序。

### 五、灵活的数据保存策略

框架支持根据配置文件灵活选择保留 Imatest 生成的原始分析图片、JSON、CSV 等文件，同时具备指标提纯功能，可根据指定阈值自动筛选数据，生成独立的精简 CSV 汇总文件，便于快速查看结果。

### 六、进度可视化与便捷操作

运行脚本前，需将待测测试图卡按 SFRplus、Colorchecker、Flatfield、Random、Checkerboard 等对应模块分类放入指定文件夹。脚本启动后，终端会实时显示进度条及待测测试图片数量，方便用户掌握整体测试进度。


## 📁 项目目录结构

项目根目录/

├── config.yaml # 配置文件：目录路径、各模块文件名、支持的处理图像扩展名、处理选项

├── file_utils.py # 文件工具：根据配置筛选目录名，管理测试数据和断点数据（已处理图片标识集合）

├── imatest_api.py # Imatest API 封装：根据配置的目录名调用 ImatestLibrary 对相应模块方法

├── imatest_base_ini # 基准配置文件：Master 版本运行后保存的各模块参数配置文件

├── logger_config.py # 日志配置：控制台输出日志，实时显示进度条及时间进度等信息

├── metrics_extractor.py # 指标提取：筛选目录导出模块名，对测试数据提纯并另存为特定 CSV 文件

├── main.py # 主入口：统筹调用各模块，包括初始化日志、加载配置、加载断点、调用 Imatest API、保存测试数据等

├── test_images/ # 待测测试图卡目录（按设备/模块分类存放）

│ └── [设备名]/

│ ├── SFRplus/

│ ├── Colorchecker/

│ ├── Checkboard/

│ ├── Flatfield/

│ └── Random/

└── output/ # 测试结果输出目录（自动创建，按时间戳命名）

│ └── [设备名]_[时间戳]/

│ ├── SFRplus/

│ ├── Colorchecker/

│ ├── ...

└── ...


## 📂 目录结构示意图

`test_images/` 目录可容纳多台设备、多个模块的待测测试图片：

<img width="575" alt="test_images 目录结构" src="https://github.com/user-attachments/assets/bbc8fcbb-c9ed-42f1-b5e5-1c524b5239c7" />

`output/` 目录自动创建，测试数据以时间戳命名区分批次：

<img width="576" height="410" alt="image" src="https://github.com/user-attachments/assets/ef15cc8b-f788-4eed-b5f5-ac22f75f357b" />

各模块测试数据按模块分类保存：

<img width="349" alt="模块数据目录" src="https://github.com/user-attachments/assets/94fe699b-55fd-4131-8d95-0cb05a2c549e" />


## 📄 核心文件说明

| 文件 | 功能说明 |

| `config.yaml` | 配置参数，包括目录路径、各模块文件名、支持的图像扩展名、处理选项 |

| `file_utils.py` | 根据配置筛选目录名，维护测试数据和断点数据（已处理图片的标识集合） |

| `imatest_api.py` | 根据配置的目录名，对号调用 `ImatestLibrary` 的对应模块方法 |

| `imatest_base_ini` | Master 版本运行后保存的各模块参数配置文件 |

| `logger_config.py` | 日志输出，在控制台显示进度条及时间进度等信息 |

| `metrics_extractor.py` | 筛选目录得出模块名，对测试数据提纯并另存为特定 CSV 文件 |

| `main.py` | 程序主入口，统筹调用各模块：初始化日志 → 加载配置 → 加载断点 → 调用 Imatest API → 保存测试数据 |

## 📄 安装核心依赖

一、安装 Imatest IT 计算引擎和 Mater GUI软件

从 Imatest 官网下载并安装 Imatest IT（独立命令行/计算引擎版）和Mater GUI交互式软件。

在 Imatest master中导出imatest_base.ini文件

二、安装 imatest-it Python 库

Imatest IT 安装完成后，在安装目录的 python/ 子目录下找到 whl 包进行安装：

参考路径：../Imatest/v23.2/IT/libs/library/python/imatest_it-23.2.16-py2.py3-none-any.whl
