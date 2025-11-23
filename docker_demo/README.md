# README

一个基于Flask的简单网站, 没啥功能. 

在这个项目中, 我计划实现以下目标: 

- [x] 使用Flask制作一个简单的Web APP
- [x] 了解如何将程序打包, 并且共享给别人
- [x] 了解WSGI, 包括Server和APP
- [x] 尝试使用docker部署

## Flask

Flask是一个轻量化 WSGI (Web Server Gateway Interface) web应用框架. 

### Minimal App

`app = Flask(__name__)`, 这个 inst 是我们的 WSGI app, 参数通常就是name, 这样才能定位到 server 所需资源

在函数上加上 decorator `@app.route(<url>)`, 不同的 URL 将触发不同的函数, 返回不同的内容给浏览器

函数可以返回:

1. `rendor_template()`, 内容是一个文件名, 文件应该在templates路径下
2. `app.send_static_file()`, 内容是一个文件名, 随便什么路径
3. 或者直接返回HTML字符串

### HTML

- `<a>` anchor, 在HTML上创造一个锚点. 可以配合`href (hypertext reference)`使用, 也可以有其他用法
- `<p>` paragraph, 开始一个新段落
- `<img src="xxxx">`插入一个图片
- `<li>` list
- `<br>` break line

### Response to POST

`@app.route()`默认只响应GET, 但是可以在参数里加上`methods=[GET, POST]`来响应post请求

- 可以通过`request.method`确定是否为POST方法
- 通过`request.form['key_name']`获取具体的请求值, 例如请求`http://127.0.0.1:5000?arg1=4&arg2=5`

或者也可以用`app.get(url), app.post(url)`来分离

### Template

Flask内置了Jinja, 这样可以方便地修改HTML内容, 而不是手动写很多的escape. 使用起来只需要`render_template(template, **kw)`

Jinja 模板的规则大概是这样的: 

```jinja2
{% if person %}
  <h1>Hello {{ person }}!</h1>
{% else %}
  <h1>Hello, World!</h1>
{% endif %}
```

Template还有个神奇作用, 可以继承. 

### Rules for app.route

route不止可以接收一个URL, 还可以匹配URL规则, 并且从中提取内容, 例如:

```python
from markupsafe import escape

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return f'User {escape(username)}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

```



## Python Packaging

推荐使用的package layout:

```
my_package/
|--pyprojexct.toml
|--src/my_package
       |--__init__.py
       |--modult.py
       
my_package/
|--pyproject.toml
|--my_package
   |--__init__.py
   |--module.py
```

Python内置的setuptools可以用来打包和分发程序, 目前的标准是使用`pyproject.toml`来描述打包的信息.

setuptools只是个后端, build是前端. 

setuptools中, 对于`pyproject.toml`的描述很详细, 对于这个项目来说, 最重要的事情其实是: 如何包含必要的文件. setuptools默认只会导入py文件, 而其他类型的文件需要手动 include 才行, 建议用`MANIFEST.in`包含额外的文件. 

打包成whl之后, 通过pip install安装后的site-packages将包含: 

```
my_pakcage/
my_package-1.2.3.dist-info/
```

而`my_package`中将包含`module.py`等文件

## Python venv

我们可能希望在虚拟环境中调试，以避免干扰开发环境。Python venv可以创建虚拟环境，并通过`scripts/activate`激活虚拟环境。 

可以在虚拟环境中安装以上构建的Flask应用, 并在site-packages中验证内容正确性. 



## WSGI

Python Web Server Gateway Interface, 是web服务器和Python Web应用之间的接口标准协议. 有多种Web服务器 (nginx, apache, waitress), 也有多种Python Web APP开发框架 (django, flask), WSGI使得Web应用可以兼容一系列Web服务器.

在前段时间开发Flask APP时, 通过`app.run()`的方式可以调用Flask内置的WSGI Server, 但这只是个调试用的server, 并不是为了安全, 稳定和高效而生. 

在这里尝试使用waitress作为Server. 只需要安装waitress和自定义的安装包, 然后执行即可. 

```
waitress-serve --host=127.0.0.1 --port=8848 <package>:<module>
```

## Docker

### Build Image

通过Dockerfile构建镜像. 这个项目基于3.12开发, 因此可以从`python:3.12-slim`创建镜像. 

安装WSGI Server, 这很简单, `RUN pip install --no-cache-dir waitress`将在build时安装`waitress`. 

安装WSGI App需要先将wheel文件拷贝到某个临时位置, 然后再删除掉

```dockerfile
COPY /dist/docker_demo-0.6.0-py3-none-any.whl /tmp/
RUN pip install --no-cache-dir /tmp/docker_demo-0.6.0-py3-none-any.whl
RUN rm /tmp/docker_demo-0.6.0-py3-none-any.whl
```

如果要在container run的时候运行`waitress-serve`, 还需要一个shell命令: 

```dockerfile
CMD ["waitress-serve", "--host=0.0.0.0", "--port=11451", "docker_demo:app"]
```

> 0.0.0.0指的是在本机的任意IP上都bind到11451端口

- 使用`docker build -t <package>:<tag> .` build
- `docker images`可以查看镜像
- `docker save <image> -o <filename>`可以导出镜像

将镜像copy到其他机器上就可以运行了

### Run Container

- 使用`docker load -i <image>` 加载本地镜像
- `docker images`可以查看镜像
- `docker run <image>`可以运行容器

如果load后看不见images, 说明`docker save`用的是id而不是name-tag, 可以重新导出, 或者用`docker tag <id> <name>`"重命名"

默认情况下, 此时会发现从外部 (浏览器) 或者内部 (`curl`)都无法访问WSGI App

`docker ps -a`可以查看镜像, 可以看到App对应的PORT为空, 说明并没有建立端口映射. 可以`docker run -p <outer>:<inner>`手动指定端口映射. 

发现此时`docker run`在前台? 需要加一个`-d` 来后台运行

### Container Manage

如果在`docker ps -a` 中看到了一些没在运行的container, 可以用`docker container prune`删除他们

`docker kill/stop`可以停止容器运行



