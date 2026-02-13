import os
import subprocess

#method1
shell_path = './server.sh'
shell_args = ['autorestart']
result = subprocess.run(['sh']+[shell_path] + shell_args)
# print("The result is: ",result)

#method2
# autorestart_sh = 'sh /data/rguo/pro_manage/picasso_v2.0/build/picasso_install_gpu_x86_64/server.sh autorestart'
# result = os.system(autorestart_sh)
# print("The result is: ",result)

