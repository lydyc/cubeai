FROM cubenet/python3810:0.0.3
ENV LANG=C.UTF-8 APP_PROFILE=prod
WORKDIR /serviceboot

# 1. 安装 git + git-lfs
RUN apt-get update && \
    apt-get install -y git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# 2. 拉取仓库到 serviceboot 目录下
RUN git clone --depth 1 https://github.com/lydyc/cubeai_picasso.git

# 3. 拉取 LFS 文件
WORKDIR /serviceboot/cubeai_picasso
RUN git lfs pull

# 4. 复制代码
WORKDIR /serviceboot
ADD . /serviceboot

# 5. 查看文件大小
RUN du -sh cubeai_picasso/picasso_install_gpu_x86_64

# 6. 安装依赖并编译
RUN sh pip-install-reqs.sh && \
    rm -rf /root/.cache/pip && \
    serviceboot compile_python

# 7. 启动服务
CMD sh -c "cd cubeai_picasso/picasso_install_gpu_x86_64 && \
    sh server.sh restart && \
    cd ../.. && \
    serviceboot start && \
    tail -f /dev/null"

