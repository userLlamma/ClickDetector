# 添加新token
python scripts/manage_tokens.py add -d "Client A Testing" --days 30 --prefix client_a

# 撤销token
python scripts/manage_tokens.py revoke --token client_a_5k4j6h_20241130

# 列出所有token
python scripts/manage_tokens.py list

# 检查token状态
python scripts/manage_tokens.py check --token client_a_5k4j6h_20241130