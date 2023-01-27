from pkg.compiler import config
import os
import subprocess

debug = True

class SandBox:

  bots = dict()
  cwd = ""

  @staticmethod
  def _get_local_images():
    command = 'docker images --no-trunc'
    try:
      result = SandBox._exec(command) 
    except RuntimeError:
      raise RuntimeError("Get local images failed")
    
    images = []
    list_row = result.split('\n')
    for line in list_row[1: ]:
      line = line.split()
      if len(line) < 7:
        continue
      images.append({
        'repo': line[0],
        'tag': line[1],
        'id': line[2],
        'time': ' '.join(line[3:6]),
        'size': line[-1],
      })

    return images
  
  @staticmethod
  def _exec(cmd, is_run=False) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
    
    if p.returncode != 0:
      if debug:
        print(p.stderr)
      raise RuntimeError("Execute failed")
    
    if is_run and (p.stdout == None or len(p.stdout) == 0):
      raise RuntimeError("TLE or empty output")
   
    return p.stdout

  def __init__(self, uuid, code, lang):
    self.uuid = uuid
    self.code = code
    self.config = config[lang]

    self.path_code = "%scode-%s.%s" % (SandBox.cwd, self.uuid, self.config['suffix'])
    self.path_target = "%sprog-%s" % (SandBox.cwd, self.uuid)
    self.path_data = "%sdata-%s" % (SandBox.cwd, self.uuid)
    
    self.id_container = None
    self.proc = None
    self.has_compiled = False
    
    self.create()
  
  # 创建容器并准备好代码
  def create(self):
    if self.id_container is not None:
      return 
    
    images_local = SandBox._get_local_images()
    images_to_use = self.config['images']
    images_available = filter(lambda x: x['repo'] in images_to_use, images_local)

    image = ""
    if images_available is not None:
      image = max(images_available, key=lambda x: x['tag'])
      image = "%s:%s" % (image['repo'], image['tag'])
    else:
      # docker pull
      pass
    
    try:
      self._run_container(image)
      self._prepare_code()
    except RuntimeError as reason:
      return str(reason) 

    return "ok"

  # 编译并返回结果
  def compile(self):
    if self.has_compiled or self.config.get('compile_command') is None:
      return "ok"
    
    compile_command = self.config['compile_command'].format(code=self.path_code, target=self.path_target)
    command = 'docker exec %s %s' % (self.id_container, compile_command)
    try:
      SandBox._exec(command)
      self._update_container()
    except RuntimeError as reason:
      return str(reason)
        
    self.has_compiled = True
    return "ok"
    
  # 准备数据
  def prepare(self, data):
    try:
      self._prepare_data(data)
    except RuntimeError as reason:
      return str(reason)

    return "ok"
  
  # 运行并返回结果
  def run(self):
    run_command = self.config['run_command'].format(code=self.path_code, target=self.path_target, data=self.path_data)
    command = 'docker exec %s /bin/sh -c "timeout %d %s"' % (self.id_container, self.config['time_limit'] / 1000, run_command)
    try:
      result = SandBox._exec(command, True)
    except RuntimeError as reason:
      return str(reason)
    
    return result.strip()

  # 关闭容器
  def stop(self):
    try:
      self._stop_container()
      self._remove_container()
    except RuntimeError:
      pass
    finally:
      return "ok"

  def _run_container(self, image):
    command = "docker run -itd %s" % image
    try:
      result = SandBox._exec(command)
    except RuntimeError as reason:
      raise reason
    
    self.id_container = result.strip()

  def _prepare_code(self):
    file_code = open(self.path_code, 'w')
    file_code.write(self.code)
    file_code.close()
    
    command = "docker cp %s %s:/" % (self.path_code, self.id_container)
    try:
      SandBox._exec(command)
    except RuntimeError:
      raise RuntimeError("Prepare code failed")
    finally:
      os.remove(self.path_code)
    

  def _prepare_data(self, data):
    file_data = open(self.path_data, "w")
    file_data.write(data)
    file_data.close()

    command = "docker cp %s %s:/" % (self.path_data, self.id_container)
    try:
      SandBox._exec(command)
    except RuntimeError:
      raise RuntimeError("Prepare data failed")
    finally:
      os.remove(self.path_data)
  
  def _update_container(self):
    command = 'docker update --cpus="1" --memory="%dm" %s' % (self.config['memory_limit'], self.id_container)
    try:
      SandBox._exec(command)
    except RuntimeError:
      raise RuntimeError("Update container failed")

  def _stop_container(self):
    command = 'docker kill %s' % (self.id_container)
    try:
      SandBox._exec(command)
    except RuntimeError:
      raise RuntimeError("Stop container failed")

  def _remove_container(self):
    command = 'docker rm %s' % (self.id_container)
    try:
      SandBox._exec(command)
    except RuntimeError:
      raise RuntimeError("Remove container failed")
