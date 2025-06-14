# Alist_aliyun_auth

这是一个用于alist上，阿里云盘认证的程序。

1. 安装依赖
    - `pip install Flast requests waitress`
    - 安装`nginx`
---
2. 修改`app.py`中
    - 端口
    - 回调地址
---
3. 修改`results.html`
    - 修改`https://<auth.example.com>/api/token` 到你的域名
---
4. 导入环境变量

    - `export ALIYUN_CLIENT_ID=\<your_id\>`
    - `export ALIYUN_CLIENT_SECRET=\<your_secret\>`
--- 
5. 在`nginx`中添加服务
    - 将`auth.example.com.conf` 中的域名修改为你的域名和端口，使用\<\>包含的内容需要替换，
    - 将`auth.example.com.conf` 修改为你的域名，并放到 `/etc/nginx/conf.d`
    - 将 `nginx.conf` 移动到 `/etc/nginx/nginx.conf`
    - 重启nginx服务以及启动`app.py`
---
## 致谢
- https://github.com/AlistGo/auth
