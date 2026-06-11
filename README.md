# 在线点餐平台

> `food-order-platform` 是一个基于 `Django + Vue + MySQL` 的在线点餐平台 MVP，用于课程项目验收

## 一、项目简介

本项目面向门店自取场景，提供顾客端点餐下单与商家端订单处理能力

顾客可以浏览食品菜单、选择商品规格、加入购物车、提交订单并完成模拟支付

商家可以维护商品信息、控制商品售罄状态，并推进订单状态流转

项目支持使用 `Docker Compose` 统一启动前端、后端和 MySQL 数据库，验收环境无需单独安装 Python、Node 或 MySQL

## 二、技术选型

| **模块** | **技术** | **说明** |
|---|---|---|
| 后端 | Django、Django REST Framework | 提供业务接口、订单流转和数据持久化逻辑 |
| 前端 | Vue、Vite | 实现顾客端与商家端页面 |
| 数据库 | MySQL | 存储用户、商品、购物车、订单、支付和评价数据 |
| 依赖管理 | uv、pyproject.toml、uv.lock | 管理 Python 虚拟环境与后端依赖 |
| 接口文档 | drf-spectacular | 生成和演示 REST API 文档 |
| 项目打包 | Docker、Docker Compose | 统一编排 MySQL、Django 和 Vue |

## 三、MVP 功能范围

- 手机号快捷登录
- 商品分类浏览与关键字搜索
- 商品规格选择
- 购物车管理
- 订单创建与模拟支付
- 订单状态跟踪
- 商家端商品管理
- 商家端订单处理

## 四、开发约束

后续编码必须遵守 [project-rules.md](project-rules.md)

## 五、Docker 启动

在项目根目录执行：

```powershell
docker compose up --build
```

启动后访问：

```text
前端页面：http://localhost:5173
后端接口：http://localhost:8000/api
接口文档：http://localhost:8000/api/schema/swagger-ui/
```

Docker 内部 MySQL 配置：

```text
DB_NAME=food_order_platform
DB_USER=food_order_user
DB_PASSWORD=food_order_pass
DB_HOST=mysql
DB_PORT=3306
```

如需重置 Docker 数据库：

```powershell
docker compose down -v
docker compose up --build
```

## 六、本地开发

同步 Python 后端依赖：

```powershell
uv sync
```

复制环境变量示例：

```powershell
Copy-Item .env.example .env
```

本地开发阶段可将 `.env` 中的 MySQL 连接信息改成自己电脑上的 MySQL：

```text
DB_NAME=food_order_platform
DB_USER=root
DB_PASSWORD=你的本机 MySQL 密码
DB_HOST=127.0.0.1
DB_PORT=3306
```

进入后端目录并执行迁移：

```powershell
cd backend
uv run python manage.py migrate
uv run python manage.py loaddata demo_data
uv run python manage.py runserver
```

进入前端目录并启动开发服务器：

```powershell
cd frontend
npm install
npm run dev
```

## 七、演示账号

顾客端可使用：

```text
手机号：13800000000
验证码：123456
```

也可以输入其他合法手机号，系统会自动创建新顾客账号

## 八、接口概览

| **接口** | **说明** |
|---|---|
| `POST /api/login/` | 手机号快捷登录 |
| `GET /api/categories/` | 查询商品分类 |
| `GET /api/products/` | 查询商品列表 |
| `POST /api/cart/items/` | 加入购物车 |
| `POST /api/orders/` | 创建订单 |
| `POST /api/payments/mock/` | 模拟支付 |
| `GET /api/orders/` | 查询顾客订单 |
| `GET /api/admin/products/` | 商家查询商品 |
| `PATCH /api/admin/products/{id}/sold-out/` | 商家设置售罄 |
| `GET /api/admin/orders/` | 商家查询订单 |
| `PATCH /api/admin/orders/{id}/status/` | 商家推进订单状态 |

## 九、目录结构

```text
food-order-platform/
  backend/                 # Django 后端项目
    api/                   # 核心业务应用
    config/                # Django 配置
    Dockerfile             # 后端 Docker 镜像
  frontend/                # Vue 前端项目
    src/                   # 前端源码
    Dockerfile             # 前端 Docker 镜像
  docker-compose.yml       # Docker Compose 编排
  pyproject.toml           # uv 项目配置与 Python 后端依赖声明
  uv.lock                  # uv 锁定的精确依赖版本
  project-rules.md         # 项目开发约束
  README.md                # 项目说明
```
