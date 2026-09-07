import os,re,sys,subprocess
from pathlib import Path
from openai import OpenAI

def load_env(path):
    if Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(Path(__file__).parent.parent / ".env")  # 密钥在 swe-agent/.env,已被 .gitignore 排除
API_KEY = os.environ.get("GLM_API_KEY", "")
base_url = "https://open.bigmodel.cn/api/paas/v4"
client =OpenAI(api_key=API_KEY,base_url=base_url)

def chat(messages):
    response=client.chat.completions.create(
        model="glm-5.3",
        messages=messages,
        temperature=0.2
    )  # 提示：model 和 messages 两个参数
    return response.choices[0].message.content   # 提示：从 resp 里取出回复文本（打印 resp 看看结构就知道了）

def run_command(command):
    try:
        result=subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60
        )
        output=(result.stdout or "")+(result.stderr or "")
        output=output.strip()
        if output == "":
            return "(命令执行成功，无输出)"
        return output
    except subprocess.TimeoutExpired:
        return "(命令执行超时)"

def read_file(path):
    if not os.path.exists(path):
        return f"(文件{path}不存在)"
    with open(path,"r",encoding="utf-8",errors="replace") as f:
        content = f.read()
        if len(content) > 3000:
            content = content[:3000] + "\n...(内容过长已截断)"
        return content


def write_file(path,content):
    with open(path,"w",encoding="utf-8",errors="replace") as f:
        f.write(content)
    return f"(成功写入{path}，共{len(content)}字符)"

def search(pattern,path="."):
    hits=[]
    for root,dirs,files in os.walk(path):
        dirs[:]=[d for d in dirs if d not in {".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}] 
        for name in files:
            fp=os.path.join(root,name)   
            try:
                with open(fp,"r",encoding="utf-8",errors="replace") as f:
                    for line_no,line in enumerate(f,1):
                        if pattern in line:
                           hits.append(f"{fp}:{line_no}:{line.rstrip()}") 
                           if len(hits)>=50:
                              return "\n".join(hits)+"\n(以上是前50条匹配结果,已截断)"   
            except OSError:
                continue          
    return "\n".join(hits)if hits else "(未找到匹配项)"                

if __name__ == '__main__':
    print(run_command("echo hello"))
    print(read_file("my_agent.py"))
    print(write_file("test_rw.txt", "abc"))
    print(search("def chat"))
    os.remove("test_rw.txt")
