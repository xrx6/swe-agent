# SWE Agent 开发学习笔记（进行中）

> 来源：CodeBuddy 辅导课，2026-09-06 起
> 项目：用 Python 写一个 SWE Agent（OpenAI 兼容接口 + 4 个工具 + 文字协议循环）
> 当前进度：第 1~2 步（工具函数）已完成，准备进入第 3 步（SYSTEM_PROMPT）

---

## 一、第 1~2 步 Python 知识清单

> 全部来自实际问过、踩过的坑。每条配自测问句，能答上来就算掌握。

### ① 语法基础

| 知识点 | 自测问句 |
|---|---|
| 关键字参数 | `OpenAI(api_key=..., base_url=...)` 为什么不能按位置传？ |
| 字典字面量 | `{"content": "..."}` 键为什么必须加引号？ |
| f-string | `{}` 里外各是什么世界？没有变量时还需要 f 吗？ |
| 元组 vs 列表 | `hits=[],` 末尾多一个逗号为什么是致命的？ |
| 三目表达式 | `A if hits else B` 展开成普通 if/else 长什么样？ |
| 列表推导式 | `[d for d in dirs if d not in 垃圾堆]` 在干什么？ |
| 转义 vs 插值 | `\n` 和 `{}` 分别是谁的机制？加不加 f 各受什么影响？ |

### ② 真值与 None（问得最多的领域）

| 知识点 | 自测问句 |
|---|---|
| None | 它的类型？和 `""`、`0`、`False` 的关系与区别？ |
| 假值 | 为什么 `""` 和 `None` 都算「假」？ |
| or 短路 | `(result.stdout or "")` 这句在防什么？ |
| is None | 为什么判断 None 用 `is` 不用 `==`？ |

### ③ 文件与路径

| 知识点 | 自测问句 |
|---|---|
| `with open(...) as f` | 不用 with 的风险是什么？ |
| 文件模式 | `"r"` 和 `"w"` 的区别？`"w"` 打开不存在的文件会怎样？ |
| encoding/errors | 中文 Windows 不加 encoding 会怎样？`errors="replace"` 救的是什么场？ |
| os.path.exists | read_file 为什么要先查它？ |
| os.path.join | 为什么不用 `+` 手动拼路径？`.\` 前缀哪来的？ |
| os.walk | root/dirs/files 三兄弟各是什么？剪枝为什么必须 `dirs[:] =`？ |

### ④ 子进程与流

| 知识点 | 自测问句 |
|---|---|
| std 三流 | stdin/stdout/stderr 全称、编号、默认接哪里？ |
| stdout≠stderr | 为什么要分家？`2>&1` 是什么意思？ |
| subprocess.run | `shell=True`、`capture_output`、`text`、`timeout` 各管什么？ |

### ⑤ 控制流

| 知识点 | 自测问句 |
|---|---|
| enumerate(f, 1) | 不用它怎么拿行号？那个 1 是什么？ |
| 元组解包 | `for line_no, line in ...` 是怎么「接住」两个值的？ |
| try/except | `except OSError: continue` 在 search 里兜的什么底？ |
| 提前 return | search 攒够 50 条为什么能「立刻回头」？ |
| `__main__` | `if __name__ == "__main__":` 防的是什么？ |
| print vs return | os.remove 为什么无声无息？ |

### ⑥ 设计原则（比语法更值钱）

1. **工具永不抛异常**——报错也是信息，返回错误字符串让模型自己调整；
2. **Observation 的信息量决定模型下一步决策质量**——报错带文件名、成功带字数，都是为此；
3. **格式即语义**——`( ... )` 标记系统备注，和真实输出划清界限；
4. **函数必须用调用方传的参数**——messages 和 path 两次晾在一边，同一个坑摔了两次。

---

## 二、第 3 步任务：写 SYSTEM_PROMPT（当前进行）

### 为什么这步是 Agent 的灵魂

模型看不到 Python 代码——4 个工具对它不存在，直到在 system prompt 里用文字交给它一份说明书。同时模型天生输出自由文本，而第 4 步的解析器需要固定格式。所以这份 prompt 是**双方签署的协议**：

> 模型承诺按格式输出 ↔ 你承诺每轮把工具结果喂回去

### 要写的 4 个部分

存成常量放文件顶部：`SYSTEM_PROMPT = """..."""`

1. **身份**：一两句——「你是 SWE Agent，通过工具操作计算机完成软件工程任务」
2. **工具说明书**：4 个工具逐个列出：名字 + 用途 + Arg 的 JSON 示例（示例要具体到能照抄）
3. **输出契约**：每次回复只能是两种格式之一——
   - 格式 A：`Thought:` + `Action:` + `Arg:`（单行 JSON）
   - 格式 B：`Thought:` + `Final:`（给用户的总结）
4. **行为规则**：每轮只调一个工具然后停下等 Observation、绝不编造 Observation、JSON 换行用 `\n`、先查看再修改

### 两条经验

- **示例 > 描述**：与其解释 JSON 怎么转义，不如放一条完整的格式 A 样例让它照抄；
- **规则越少越好**：每条规则都在消耗模型注意力。写完自查「这条不写会出什么事？」答不上来就删。

### 过关标准

```python
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "在当前目录创建 test.py，内容打印 hi，并运行验证"},
    ]
    print(chat(messages))
```

跑两三次，模型每次都稳定输出严格的三件套格式 → 过关。

---

## 三、完整还原：my_agent.py 的诞生时间线（来自本地文件历史）

> 来源：CodeBuddy 在本地保存的 11 个文件快照（`User/History/1bfc676a/`）。
> 聊天正文存在云端拿不到，但代码演进比聊天记录更干貨——每一步都带时间戳。

| 时间 | 发生了什么 |
|---|---|
| 09-05 19:35 | **起点**：只有 `import` + `API_KEY` + `base_url` 四行（照着教程图抄的配置） |
| 09-05 19:50 | CodeBuddy 给出 224 行**参考框架**（ReAct 循环 + 五大组件的注释版蓝图） |
| 09-05 19:58 | 删掉参考，回到四行**从头自己写**（教学生式：先看蓝图，再亲手重建） |
| 09-05 20:13 | 写 chat()：`client = OpenAI(API_KEY, base_url)` ← **位置参数 bug** |
| 09-05 20:16 | 修复 → `OpenAI(api_key=API_KEY, base_url=base_url)` 关键字参数 |
| 09-05 20:19 | 补 `messages=messages, temperature=0.2` + 测试调用 |
| 09-05 20:22 | 加 `if __name__ == '__main__':` 守卫 |
| 09-06 02:41 | 深夜加班：+ `run_command`（subprocess + 超时/错误处理） |
| 09-06 22:42 | + `write_file` + `search`（自带 4 个 bug） |
| 09-06 22:43 | 测试改为四件套联测 + `os.remove` 清理 |
| 09-06 22:47 | **修复 4 个 bug，第 2 步收官** ✅ |

### 四个 bug 的修复现场（22:42 → 22:47 的 diff）

```python
# bug 1：逗号把列表变成单元素元组，.append 直接崩
- hits=[],
+ hits=[]

# bug 2：忽略调用方传的参数，永远搜当前目录（path 形同虚设）
- for root,dirs,files in os.walk("."):
+ for root,dirs,files in os.walk(path):

# bug 3：读文件不设上限，巨文件会撑爆模型上下文
- return f.read()
+ content = f.read()
+ if len(content) > 3000:
+     content = content[:3000] + "\n...(内容过长已截断)"
+ return content

# bug 4：报错不带文件名，模型拿到信息无法定位
- return f"(文件不存在)"
+ return f"(文件{path}不存在)"
```

每个 bug 都对应第⑥节一条设计原则的反面教材：元组逗号是语法课学费；`os.walk(".")` 违反「函数必须用调用方的参数」；无截断违反「Observation 信息量要可控」；报错无文件名违反「报错也是信息」。

### 会话里其他值得记的细节

- search 的测试输出把 `my_agent.py:70` 的测试代码自己也搜出来了——工具「无差别」是正常现象，模型自己会分辨噪音，不用修；
- 参考框架被自己删掉重写这件事本身就是这套教学法的关键：看懂 ≠ 会写。

---

## ⚠️ 安全提醒（重要）

`my_agent.py` 顶部**明文写着 API key**。这个目录有 git 仓库（search 剪枝了 `.git`），一旦 commit + push，key 就泄了。两个处理方式任选：

```python
# 方式一：环境变量（推荐）
import os
API_KEY = os.environ["ZHIPU_API_KEY"]   # 运行前 set ZHIPU_API_KEY=xxx

# 方式二：至少把它挪进 .gitignore 排除的配置文件
```

---

## 待办

- [ ] **给 API key 挪窝**（见上方安全提醒，先做这个）
- [ ] 写 SYSTEM_PROMPT（按上面 4 部分结构）
- [ ] 跑过关标准测试，观察输出格式稳定性
- [ ] 第 4 步：解析器（预告：靠固定格式拆出 Action/Arg）

## 复习自查（合并版）

1. `result.stdout or ""` 防的是哪两种情况？
2. 剪枝为什么必须写 `dirs[:] = [...]` 而不能 `dirs = [...]`？
3. 工具函数为什么选择返回错误字符串而不是 raise？
4. 格式 A 三件套的顺序是什么？Arg 为什么必须是单行 JSON？
5. SYSTEM_PROMPT 里「示例 > 描述」这条经验针对的是模型的什么能力？
