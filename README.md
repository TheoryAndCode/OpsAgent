# 1 项目简介（详细介绍请查看设计说明文档）

## 1.1 项目背景

- 这个项目是一个基于**Ubuntu**操作系统的智能代理（可以理解为OpenClaw丐版）。
- 用于让用户通过命令行可以实现对操作系统的控制。
- 实现了web端简化操作，对用户权限做了分离，可以循环实现需求。

## 1.2 项目实现

- 涉及主要技术如下：streamlit、LangChain & LangGraph、paramiko、Docker、Ubuntu。
- 使用ReAct + 两个工具实现（详细功能请查看**演示视频**和**设计说明文档**）。

# 2 项目部署方法

## 2.1 Ubuntu环境安装

- Docker环境：该项目首先需要一个Docker环境（关于如何安装Docker这里不再赘述）。
- 部署Ubuntu：直接运行我们提供的docker-compose.yml文件即可自动拉取镜像并创建容器。

```shell
docker compose up -d
```

- 安装SSH服务：进入到容器中，执行以下命令安装。

```
# 强制非交互式安装 + 自动设置时区(上海) + 换国内源 + 安装SSH(全程无弹窗) DEBIAN_FRONTEND=noninteractive apt update && \ 
DEBIAN_FRONTEND=noninteractive apt install -y openssh-server tzdata && \ 
ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \ 
mkdir -p /var/run/sshd
```

```
# 允许root远程登录
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config 
# 设置账号密码（比如123456） 
echo 'root:123456' | chpasswd 
# 启动SSH服务
/usr/sbin/sshd
```

## 2.2 项目环境安装

- 项目环境一键安装：进入项目后使用以下命令可以直接一键安装环境。

```shell
pip install -r requirements
！！注意运行该系统需要一个阿里云大模型密钥，请将密钥配置进系统环境中！！
```

- 环境简要说明：
  - 大模型密钥：该项目用的是阿里云百炼平台，注意我将密钥设置到了系统环境中。
  - python 3.10：使用这个版本主要原因是本地有，不用再配了。
  - LangChain & LangGraph：注意还要补充一些社区环境，比如langchain_community等。
  - paramiko：用于连接ssh执行命令的工具库。

## 2.3 项目启动方法

1.先启动docker容器

```shell
docker compose up -d
```

2.进入到ubuntu容器里，启动ssh服务

```shell
docker exec -it agent-target-os bash
/usr/sbin/sshd
```

3.启动项目入口

```shell
streamlit run web.py
```