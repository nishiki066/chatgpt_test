from app import create_app

# 创建 Flask 应用实例
app = create_app()

if __name__ == "__main__":
    # 运行 Flask 开发服务器
    app.run(host="0.0.0.0", port=5000, debug=True)
