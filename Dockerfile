FROM cubenet/python3810:0.0.3
ENV LANG=C.UTF-8 APP_PROFILE=prod
WORKDIR /serviceboot
ADD . /serviceboot
RUN sh pip-install-reqs.sh && \
    rm -rf /root/.cache/pip && \
    serviceboot compile_python
CMD sh -c "cd picasso_install_gpu_x86_64 && \
    sh server.sh restart && \
    cd .. && \
    serviceboot start && \
    tail -f /dev/null"

