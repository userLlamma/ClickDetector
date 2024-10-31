# 创建新token
curl -X POST "http://localhost:8000/admin/tokens" \
     -H "x-admin-token: your-secure-admin-token" \
     -H "Content-Type: application/json" \
     -d '{"description": "Test Token", "days": 30}'

# 使用token调用预测接口
curl "http://localhost:8000/predict" \
     -H "x-api-token: your-api-token" \
     -H "Content-Type: application/json" \
     -d '{"data": "..."}'

# 验证token
curl "http://localhost:8000/verify-token" \
     -H "x-api-token: your-api-token"

# 查看所有token
curl "http://localhost:8000/admin/tokens" \
     -H "x-admin-token: your-secure-admin-token"

# 撤销token
curl -X DELETE "http://localhost:8000/admin/tokens/your-api-token" \
     -H "x-admin-token: your-secure-admin-token"