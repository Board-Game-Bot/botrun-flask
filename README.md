# Bot Run System

这是用于管理 Board Bot Game App 的代码运行后台的项目。

# 思想

Board Bot Game 运行用户代码需要做到两点：**支持多语言**，**防止运行用户提交的恶意代码**。

显然，符合这两个条件的是**沙箱**，但是如果要说有没有现成可用的沙箱方案，那就是**Docker**。因此，本项目实际上相当于是管理 Docker 分配的项目，充其量只是一个**管理系统**。

尽管 Docker 是开箱即用，但仍然不够完美，因为其容器的创建，即便是很轻便的 alpine 系列的镜像，仍然需要相当长的时间才能启动，因此后续将使用新的沙箱（可能需要自己搓轮子）。

# 设计

本项目当前比较简单，因此只需要列出所有的需要的功能即可。

## 技术栈

<img src="https://skillicons.dev/icons?i=python,flask,docker" width="25%">

这里的**输入/输出**，均为一般网络请求的**请求/响应**。

## 功能

- 接收用户的代码并尝试编译
  - 输入：用户代码文本
  - 输出：编译结果
 
- 接收用户的代码，启动容器
  - 输入：用户代码文本
  - 输出：启动结果，以及相应的容器ID
 
- 接收用户的输入内容，运行代码
  - 输入：容器ID，输入内容
  - 输出：运行结果（有可能有 Runtime Error）
 
- 关闭容器
  - 输入：容器ID
  - 输出：无
 
- 查看所有已生成的容器
  - 输入：无
  - 输出：所有的容器的信息

- 查看所有支持的语言
  - 输入：无
  - 输出：所有支持的语言
 
- 查看所有语言的配置（各语言使用什么镜像、运行时间限制、内存限制等等）
  - 输入：无
  - 输出：配置信息
 
- 查看某个语言的配置
  - 输入：语言
  - 输出：对应的配置信息
 
- 配置某个语言对应的镜像
  - 输入：语言，配置信息
  - 输出：配置结果
 
- 查询可使用的镜像
  - 输入：镜像模糊名
  - 输出：镜像模糊查询的结果
