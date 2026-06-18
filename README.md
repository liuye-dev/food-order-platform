# 在线点餐平台

> `food-order-platform` 是一个基于 `Django + Vue + SQLite` 的在线点餐平台 MVP，用于课程项目验收。

## 一、项目简介

本项目面向门店自取场景，提供顾客端点餐下单与商家端订单处理能力。

顾客可以浏览食品菜单、选择商品规格、加入购物车、提交订单并完成模拟支付。

商家可以维护商品信息、控制商品售罄状态，并推进订单状态流转。

项目使用 SQLite 作为本地演示数据库，老师运行时不需要安装或配置额外数据库。

## 二、技术选型

| **模块** | **技术** | **说明** |
|---|---|---|
| 后端 | Django、Django REST Framework | 提供业务接口、订单流转和数据持久化逻辑 |
| 前端 | Vue、Vite | 实现顾客端与商家端页面 |
| 数据库 | SQLite | 本地文件数据库，降低运行和验收配置成本 |
| 依赖管理 | uv、pyproject.toml、uv.lock | 管理 Python 虚拟环境与后端依赖 |
| 接口文档 | drf-spectacular | 生成和演示 REST API 文档 |

## 三、MVP 功能范围

- 手机号快捷登录
- 商品分类浏览与关键字搜索
- 商品规格选择
- 购物车管理
- 订单创建与模拟支付
- 订单状态跟踪
- 商家端商品管理
- 商家端订单处理

## 四、一键启动

老师本机只需要安装 Python、uv、Node.js。

在项目根目录双击或执行：

```powershell
start-demo.cmd
```

脚本会自动完成：

- 安装 Python 后端依赖
- 创建 SQLite 本地数据库
- 执行 Django 迁移
- 导入 demo 数据
- 打开后端服务窗口
- 打开前端服务窗口

启动后访问：

```text
前端页面：http://localhost:5173
后端接口：http://localhost:8000/api/health/
接口文档：http://localhost:8000/api/schema/swagger-ui/
```

## 五、手动启动

后端终端：

```powershell
cd D:\Code\Python\Practice\food-order-platform
uv sync
uv run python backend\manage.py migrate
uv run python backend\manage.py loaddata demo_data
uv run python backend\manage.py runserver
```

前端终端：

```powershell
cd D:\Code\Python\Practice\food-order-platform\frontend
npm install
npm run dev
```

## 六、演示账号

顾客端可使用：

```text
手机号：13800000000
验证码：123456
```

也可以输入其他合法手机号，系统会自动创建新顾客账号。

商家端演示账号：

```text
账号：admin
密码：123456
```

## 七、接口概览

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

## 八、目录结构

```text
food-order-platform/
  backend/                 # Django 后端项目
    api/                   # 核心业务应用
      models.py            # 数据模型与领域对象
      serializers.py       # API 输出与表单数据序列化
      services.py          # 登录、购物车、下单、支付、订单流转等业务规则
      responses.py         # 统一接口响应格式
      exceptions.py        # 业务异常定义
      views.py             # HTTP 请求适配层
    config/                # Django 配置
  frontend/                # Vue 前端项目
    src/                   # 前端源码
      components/          # 顾客端、商家端、规格弹窗等页面组件
      api.js               # 前端 API 请求封装
      App.vue              # 应用壳、全局状态与业务协调
      styles.css           # 全局样式
  pyproject.toml           # uv 项目配置与 Python 后端依赖声明
  uv.lock                  # uv 锁定的精确依赖版本
  project-rules.md         # 项目开发约束
  start-demo.cmd           # 本地演示启动脚本
  README.md                # 项目说明
```
