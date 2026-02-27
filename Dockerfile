FROM cubenet/python3810:0.0.3
ENV LANG=C.UTF-8 APP_PROFILE=prod
WORKDIR /serviceboot
ADD . /serviceboot
RUN ls -l picasso_install_gpu_x86_64

# 先复制全部文件
#COPY . .
# 检查文件是否存在
#RUN ls -l picasso_install_gpu_x86_64.part_*
#RUN cat picasso_install_gpu_x86_64.part_* > picasso_install_gpu_x86_64.tar
#RUN tar -xf picasso_install_gpu_x86_64.tar
#RUN rm picasso_install_gpu_x86_64.tar picasso_install_gpu_x86_64.part_*
# 合并、解压tar包并删除
#RUN cat picasso_install_gpu_x86_64.part_* > picasso_install_gpu_x86_64.tar && \
#    tar -xf picasso_install_gpu_x86_64.tar && \
#    rm picasso_install_gpu_x86_64.tar picasso_install_gpu_x86_64.part_*

# 安装依赖并编译
RUN sh pip-install-reqs.sh && \
    rm -rf /root/.cache/pip && \
    serviceboot compile_python

# 启动服务
CMD sh -c "cd picasso_install_gpu_x86_64 && \
    sh server.sh restart && \
    cd .. && \
    serviceboot start && \
    tail -f /dev/null"

