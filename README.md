# 在线点餐平台

> `food-order-platform` 是一个基于 `Django + Vue + MySQL` 的在线点餐平台 MVP，用于课程项目验收

## 一、项目简介

本项目面向门店自取场景，提供顾客端点餐下单与商家端订单处理能力

顾客可以浏览食品菜单、选择商品规格、加入购物车、提交订单并完成模拟支付

商家可以维护商品信息、控制商品售罄状态，并推进订单状态流转

项目完成后使用 `Docker Compose` 打包运行环境，统一启动前端、后端和 MySQL 数据库，降低验收环境配置成本

## 二、技术选型

| **模块** | **技术** | **说明** |
|---|---|---|
| 后端 | Django、Django REST Framework | 提供业务接口、订单流转和数据持久化逻辑 |
| 前端 | Vue、Vite | 实现顾客端与商家端页面 |
| 数据库 | MySQL | 存储用户、商品、购物车、订单、支付和评价数据 |
| 依赖管理 | uv、requirements.txt | 管理 Python 虚拟环境与后端依赖 |
| 接口文档 | drf-spectacular | 生成和演示 REST API 文档 |
| 项目打包 | Docker、Docker Compose | 最终交付时统一编排 MySQL、Django 和 Vue |

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
