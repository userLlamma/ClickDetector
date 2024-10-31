# 使用默认配置
python -m export.export_model

# 指定配置文件
python -m export.export_model --config path/to/config.yaml

# 指定输出路径
python -m export.export_model --output path/to/output.pt

# 举例，在src目录下的cmd终端
python -m deploy.export.export_model --config deploy\export\configs\export_config.yaml --output deploy\weights