# 卫星店商业规划与预测系统

本系统是一款面向连锁餐饮企业的卫星店商业工具，通过整合门店单量预测、成本结构分析和利润测算功能，为商店运营策略提供数据支持。

## 功能特性

- **项目管理**: 支持新建、加载、保存项目，方便地管理不同店铺的规划。
- **交互式参数输入**: 通过命令行界面引导用户输入所有必要的商业参数。
- **CSV批量导入**: 支持通过预设的CSV模板文件批量导入项目数据。
- **单量预测引擎**: 基于区位、品类、价格等因素科学预测未来单量。
- **成本与利润分析**: 自动区分固定与变动成本，进行本量利（CVP）分析和边际贡献分析。
- **敏感性分析**: 自动分析关键变量（如成本、客单价）对利润的影响程度。
- **PDF报告导出**: 一键生成包含核心指标、分析图表和优化建议的可行性分析报告。

## 环境配置

1.  **克隆或下载项目**:
    ```bash
    git clone <your-repo-url>
    cd StoreTool
    ```

2.  **创建并激活Python虚拟环境**:
    建议使用 Python 3.9 或更高版��。

    在 Windows 上:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

    在 macOS / Linux 上:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **安装依赖**:
    激活虚拟环境后，运行以下命令安装所有必需的库。项目启动所需的字体文件也会被自动下载。
    ```bash
    pip install -r src/requirements.txt
    ```

## 如何使用

1.  **启动程序**:
    在项目根目录下，运行以下命令启动应用：
    ```bash
    python src/main.py
    ```

2.  **主菜单**:
    程序启动后，您会看到主菜单，可以选择：
    - **新建项目**: 开始一个全新的店铺规划。
    - **加载项目**: 从之前保存的 `.json` 文件加载一个项目。
    - **从CSV导入项目**: 根据 `src/data/template.csv` 模板批量创建一个或多个项目。
    - **退出**: 关闭程序。

3.  **项目操作**:
    进入一个项目后，您可以：
    - **编辑参数**: 分类修改店铺的各项参数，如基本信息、成本结构等。
    - **执行分析**: 运行预测和分析引擎，查看核心指标和敏感性分析的计算结果。
    - **保存项目**: 将当前项目的所有配置保存到一个 `.json` 文件中。
    - **导出PDF报告**: 在 `evaluation` 文件夹���生成一份完整的PDF可行性分析报告。

## CSV 模板说明

您可以在 `src/data/template.csv` 找到数据导入模板。请参照该文件的列和格式准备您的数据。

- `project_name`: 项目名称
- `city`: 城市
- `area`: 区域
- `business_circle_type`: 商圈类型 (e.g., 核心商圈, 次级商圈, 社区)
- `longitude`, `latitude`: 经纬度
- `category1_name`, `category2_name`, `category3_name`: 三级品类名称
- `category1_ratio`, `category2_ratio`, `category3_ratio`: 对应品类销售额占比 (三者相加应为1.0)
- `avg_item_price`: 客单价
- `ingredient_cost_ratio`: 食材成本占单品售价的比例
- `packaging_cost_ratio`: 包材成本占单品售价的比例
- `monthly_rent`: 月租金
- `monthly_labor_cost`: 月人力成本 (核心全职员工)
- `monthly_marketing_cost`: 月推广费用
- `commission_rate`: 平台佣金率