# 力维行人检测

基于力维行人检测模型，实现行人检测和识别功能。

## 模型应用开发和部署

### 模型服务化

本模型基于 [ServiceBoot微服务引擎](https://openi.pcl.ac.cn/cubepy/serviceboot) 进行服务化封装，参见： [《CubeAI模型开发指南》](https://openi.pcl.ac.cn/cubeai-model-zoo/cubeai-model-zoo/src/branch/master/docs/CubeAI模型开发指南.md) 

### 直接源代码运行

```
$ sh pip-install-reqs.sh
$ serviceboot start
或
$ python3 run_model_server.py
```

### 本地容器化部署

一键式本地容器化部署和运行，参见： [《CubeAI模型独立部署指南》](https://openi.pcl.ac.cn/cubeai-model-zoo/cubeai-model-zoo/src/branch/master/docs/CubeAI模型独立部署指南.md) 或  [CubeAI Docker Builder](https://openi.pcl.ac.cn/cubeai/cubeai-docker-builder) 

### 云原生网络部署

本模型服务可一键发布至 [CubeAI智立方平台](https://openi.pcl.ac.cn/OpenI/cubeai) 进行共享和部署，参见： [《CubeAI模型发布指南》](https://openi.pcl.ac.cn/cubeai-model-zoo/cubeai-model-zoo/src/branch/master/docs/CubeAI模型发布指南.md) 

### 更多CubeAI模型服务，参见： [《CubeAI服务原生模型示范库》](https://openi.pcl.ac.cn/cubeai-model-zoo/cubeai-model-zoo) 
