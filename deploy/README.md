# 模型格式验证
python scripts/verify_traced_model.py ../weights/model_cpu.pt


# deploy/  目录下 测试服务
uvicorn inference.app.main:app --reload

# deploy/  目录下  后台启动服务五
```
nohup uvicorn inference.app.main:app --host 0.0.0.0 --port 11235 --log-config   /home/ubuntu/ClickDetector/deploy/inference/configs/log_config.yml > app.log 2>&1 &

# 查看进程
ps aux | grep uvicorn

# 如果需要停止服务
kill $(pgrep -f uvicorn)
```