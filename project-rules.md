# 在线点餐平台项目守则

> 本文件是 `food-order-platform` 的项目级开发守则，用于约束后续编码、文档、演示和验收相关改动。每次修改代码或文档前，应先阅读本文件，确保改动仍然服务于课程 MVP 目标

## 一、项目定位

本项目中文名固定为**在线点餐平台**，代码名固定为 `food-order-platform`

项目目标是完成一个可运行、可演示、可追溯到需求分析报告和详细设计报告的课程验收 MVP

系统面向门店自取点餐场景，核心闭环如下：

```text
顾客登录
  -> 浏览菜单
  -> 选择商品规格
  -> 加入购物车
  -> 提交订单
  -> 模拟支付
  -> 商家查看订单
  -> 商家推进订单状态
  -> 顾客查看订单状态
```

## 二、需求来源

所有功能应尽量追溯到需求分析报告中的 5 个 Feature 和 11 个 User Story

| **编号** | **名称** | **实现要求** |
|---|---|---|
| F01 / US01 | 手机号快捷登录 | 使用固定验证码或模拟验证码，新用户自动创建 |
| F01 / US02 | 个人资料与地址维护 | 可简化为昵称、手机号、地址模型或基础资料维护 |
| F01 / US03 | 积分与优惠券查看 | 可使用字段、模型或静态展示预留 |
| F02 / US04 | 动态分类浏览 | 支持分类展示和商品名模糊搜索 |
| F02 / US05 | 商品规格深度定制 | 支持单选、多选规格，并影响价格 |
| F03 / US06 | 购物车实时管理 | 支持加入、数量修改、删除和总价计算 |
| F03 / US07 | 模拟在线支付 | 生成唯一订单号，支付成功后进入制作中 |
| F04 / US08 | 订单实时状态流转 | 展示制作中、请取货、已完成等状态 |
| F04 / US09 | 历史订单评价 | 已完成订单支持五星评价 |
| F05 / US10 | 商品上下架控制 | 商家可新增、编辑商品并设置售罄 |
| F05 / US11 | 订单接单处理 | 商家可查看订单并推进状态 |

> 新增功能如果无法对应上述 Feature 或 User Story，应先确认是否确实属于课程验收范围

## 三、技术栈约束

| **层次** | **技术** | **说明** |
|---|---|---|
| 前端 | Vue、Vite | 实现登录页、顾客端和商家端页面 |
| 后端 | Django、Django REST Framework | 提供 REST API 和业务规则 |
| 数据库 | SQLite | 使用本地文件数据库，降低验收运行成本 |
| 依赖管理 | uv、pyproject.toml、uv.lock | Python 依赖以锁文件为准 |
| 接口文档 | drf-spectacular | 提供 Swagger API 文档 |

项目当前不使用 Docker 和外部数据库，默认通过 `start-win.cmd` 或 `start-mac.sh` 本地启动

## 四、目录职责

| **路径** | **职责** |
|---|---|
| `backend/api/models.py` | 数据模型和领域对象 |
| `backend/api/serializers.py` | API 数据序列化 |
| `backend/api/services.py` | 登录、购物车、下单、支付、订单流转等业务规则 |
| `backend/api/views.py` | HTTP 请求适配层，只做参数读取、调用服务和返回响应 |
| `backend/api/responses.py` | 统一接口响应结构 |
| `backend/api/exceptions.py` | 业务异常定义 |
| `backend/api/fixtures/demo_data.json` | 演示数据 |
| `frontend/src/components/` | 登录页、顾客端、商家端和规格弹窗组件 |
| `frontend/src/api.js` | 前端 API 请求封装 |
| `frontend/src/App.vue` | 应用壳、登录状态和全局业务协调 |
| `start-win.cmd` | Windows 本地演示启动脚本 |
| `start-mac.sh` | macOS 本地演示启动脚本 |
| `README.md` | 给老师或同学看的运行说明 |
| `编码实现报告.md` | 课程提交用编码实现说明 |

## 五、后端开发规则

- API 返回格式保持统一：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 视图层 `views.py` 不应堆业务逻辑，复杂规则优先放入 `services.py`
- 业务错误应使用 `BusinessError` 或统一错误响应处理
- 订单金额必须由后端重新计算，前端金额只用于展示
- 创建订单前必须重新校验商品是否售罄
- 订单明细必须保存商品名称、价格和规格快照，避免商品后续修改影响历史订单
- 模拟支付成功后必须同步创建支付记录并更新订单状态
- 商家端只能按合法顺序推进订单状态，避免状态回退
- 修改模型后必须同步生成并提交 migration

## 六、前端开发规则

- 前端必须体现顾客端和商家端两个角色
- 系统先进入独立登录页，再根据登录角色进入对应页面
- 登录页不默认填充手机号、验证码、商家账号或密码
- 页面展示统一使用“在线点餐平台”作为项目名称
- 不在页面中展示技术栈宣传文案，例如 `Django + Vue + SQLite`
- 顾客端优先保证点餐链路完整
- 商家端优先保证商品售罄和订单状态推进
- 页面状态变化必须能反映后端数据变化
- 公共请求逻辑放在 `frontend/src/api.js`
- 大块页面优先拆成组件，避免 `App.vue` 继续膨胀

## 七、数据库与数据规则

- 数据库使用 SQLite，默认文件为 `backend/db.sqlite3`
- `backend/db.sqlite3` 不提交到 Git
- `.env` 不提交到 Git
- `.env.example` 只保留可公开的示例配置
- 演示数据使用 `backend/api/fixtures/demo_data.json`
- 本地初始化顺序应为：

```powershell
uv run python backend\manage.py migrate
uv run python backend\manage.py loaddata demo_data
```

macOS 可使用对应路径分隔符：

```bash
uv run python backend/manage.py migrate
uv run python backend/manage.py loaddata demo_data
```

## 八、运行与演示规则

Windows 推荐启动方式：

```powershell
start-win.cmd
```

macOS 推荐启动方式：

```bash
bash start-mac.sh
```

启动后访问：

```text
前端页面：http://localhost:5173
后端接口：http://localhost:8000/api/health/
接口文档：http://localhost:8000/api/schema/swagger-ui/
```

演示账号：

```text
顾客手机号：13800000000
顾客验证码：123456

商家账号：admin
商家密码：123456
```

## 九、文档规则

- README 面向运行和验收，应优先说明如何启动、如何访问、使用什么账号
- 编码实现报告面向课程提交，应说明项目简介、Prompt、Vibe Coding 过程、AI 生成后的修改、存在问题和需求追溯关系
- 修改启动方式、技术栈、目录结构后，必须同步更新 README 和编码实现报告
- 修改功能范围后，必须同步更新需求追溯表
- 文档使用标准 Markdown，不使用平台专用富文本标签

## 十、提交前检查清单

每次完成改动后至少检查以下事项：

- 是否仍然使用“在线点餐平台”作为项目名称
- 是否没有引入课程范围外的复杂功能
- 是否没有提交 `.env`、`.venv/`、`node_modules/`、`frontend/dist/`、`backend/db.sqlite3`
- 后端是否能通过系统检查：

```powershell
uv run python backend\manage.py check
```

- 模型和迁移是否一致：

```powershell
uv run python backend\manage.py makemigrations --check --dry-run
```

- 前端是否能构建：

```powershell
cd frontend
npm run build
```

- README、编码实现报告、项目守则是否和当前实现一致
