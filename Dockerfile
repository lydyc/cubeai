FROM cubenet/python3810:0.0.3
ENV LANG=C.UTF-8 APP_PROFILE=prod
WORKDIR /serviceboot

# 1. 安装 git + gdb + vim
RUN apt-get update && \
    apt-get install -y \
        git \
        gdb \
        wget \
        tar \
        vim \
    && rm -rf /var/lib/apt/lists/*

# 2. 下载并解压大文件(-c 断点续传)
RUN wget -c http://tc0x03g16.hn-bkt.clouddn.com/picasso_install_gpu_x86_64.tar.gz && \
    tar -xzf picasso_install_gpu_x86_64.tar.gz && \
    rm -f picasso_install_gpu_x86_64.tar.gz

# 3. 复制代码
ADD . /serviceboot

# 4. 查看文件大小
RUN du -sh picasso_install_gpu_x86_64

# 5. 安装依赖并编译
RUN sh pip-install-reqs.sh && \
    rm -rf /root/.cache/pip && \
    serviceboot compile_python

# 7. 启动服务
CMD sh -c "cd picasso_install_gpu_x86_64 && \
    sh server.sh restart && \
    cd .. && \
    serviceboot start && \
    tail -f /dev/null"