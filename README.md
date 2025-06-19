# 翻译完成度统计工具

此工具接受一个文本文件路径作为参数，会读取指向文件所给定的包名列表（每行一个），使用 `apt source` 获取其对应的源码，然后针对每个获取到源码的包，依次使用 `deepin-translation-utils` 命令行工具的 `deepin-translation-utils stats path/to/source/root/` 命令的标准输出获取翻译完成情况，取其包含 `zh_HK` 与 `zh_TW` 的行进行输出。

## 使用方法

```bash
python stats.py packages.txt [--source-dir 源码存储目录] [--languages 语言列表]
```

也可以使用 [uv](https://docs.astral.sh/uv/):

```bash
uv run stats.py packages.txt [--source-dir 源码存储目录] [--languages 语言列表]
```

### 参数说明

- `packages.txt`: 包名列表文件，每行一个包名
- `--source-dir`: 可选参数，指定源码存储目录。默认使用当前工作目录下的 `pkg-sources` 子目录
- `--languages`: 可选参数，指定要统计的语言列表，用逗号分隔。默认为 `zh_HK,zh_TW`

### 工作流程

1. 读取包名列表文件
2. 对每个包使用 `apt source` 下载源码到指定目录
3. 如果源码目录已存在，则跳过下载步骤
4. 对每个源码包执行 `deepin-translation-utils stats` 命令
5. 过滤输出中包含指定语言的行（默认为 `zh_HK` 或 `zh_TW`）
6. 按指定格式输出结果到标准输出

## 依赖要求

- 系统环境：Deepin/Debian 或其他支持 `apt source` 的系统
- 必需工具：`deepin-translation-utils` 命令行工具
- Python版本：>=3.12

## 错误处理

当软件包 `apt source` 失败、`deepin-translation-utils` 命令执行返回非零值，或发生其他异常时，该包将被标记为无法进行翻译统计，并在输出中显示相关错误信息。

处理完成后不会自动清理下载的源码，以便后续重复使用。

## 使用示例

```bash
# 使用默认语言 (zh_HK, zh_TW)
python stats.py packages.txt

# 指定自定义源码目录
python stats.py packages.txt --source-dir /tmp/sources

# 指定特定语言
python stats.py packages.txt --languages zh_CN,zh_TW

# 指定多种语言
python stats.py packages.txt --languages zh_HK,zh_TW,zh_CN,ja_JP

# 组合使用多个参数
python stats.py packages.txt --source-dir /tmp/sources --languages zh_CN,zh_TW
```

## 输出格式示例

假定`包名1`可以正常得到结果，`包名2`出错，则格式如下：

```plain
包名1:

deepin-translation-utils提供的输出中，包含 zh_HK 或 zh_TW 的行的原样内容。

包名2:

错误原因
```