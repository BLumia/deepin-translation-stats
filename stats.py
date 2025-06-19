#!/usr/bin/env python3
"""
翻译完成度统计工具

读取包名列表文件，使用 apt source 获取源码，然后使用 deepin-translation-utils 
统计翻译完成情况，输出包含指定语言的行（默认为 zh_HK 和 zh_TW）。
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def check_dependencies():
    """检查必需的依赖工具是否存在"""
    # 检查 apt 命令
    try:
        subprocess.run(['apt', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 apt 命令，请确保在支持 apt 的系统上运行此工具", file=sys.stderr)
        sys.exit(1)
    
    # 检查 deepin-translation-utils 命令
    try:
        subprocess.run(['deepin-translation-utils', '--help'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误: 未找到 deepin-translation-utils 命令，请先安装此工具", file=sys.stderr)
        sys.exit(1)


def read_package_list(file_path: str) -> List[str]:
    """读取包名列表文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return packages
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件 {file_path} 失败: {e}", file=sys.stderr)
        sys.exit(1)


def download_source_package(package_name: str, source_dir: Path) -> Tuple[bool, str]:
    """
    下载软件包源码
    
    Returns:
        (success: bool, message: str)
    """
    # 检查源码是否已存在
    existing_dirs = list(source_dir.glob(f"{package_name}*"))
    if existing_dirs:
        return True, f"源码已存在，跳过下载: {existing_dirs[0]}"
    
    # 下载源码
    try:
        result = subprocess.run(
            ['apt', 'source', package_name],
            cwd=source_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return True, "下载成功"
    except subprocess.CalledProcessError as e:
        return False, f"apt source 失败: {e.stderr.strip()}"
    except Exception as e:
        return False, f"下载异常: {str(e)}"


def find_source_directory(package_name: str, source_dir: Path) -> str:
    """查找软件包的源码目录"""
    # 查找以包名开头的目录
    matching_dirs = [path for path in source_dir.glob(f"{package_name}*") if path.is_dir()]
    if not matching_dirs:
        return ""
    
    # 选择第一个匹配的目录
    return str(matching_dirs[0])


def get_translation_stats(source_path: str) -> Tuple[bool, str]:
    """
    获取翻译统计信息
    
    Returns:
        (success: bool, output_or_error: str)
    """
    try:
        result = subprocess.run(
            ['deepin-translation-utils', 'stats', source_path],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"deepin-translation-utils 执行失败 (返回码: {e.returncode}): {e.stderr.strip()}"
    except Exception as e:
        return False, f"执行异常: {str(e)}"


def filter_translation_lines(output: str, languages: List[str]) -> str:
    """过滤包含指定语言的行"""
    lines = output.split('\n')
    filtered_lines = []
    for line in lines:
        if any(lang in line for lang in languages):
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)


def process_package(package_name: str, source_dir: Path, languages: List[str]) -> None:
    """处理单个软件包"""
    print(f"{package_name}:")
    print()
    
    # 下载源码
    success, message = download_source_package(package_name, source_dir)
    if not success:
        print(message)
        print()
        return
    
    # 查找源码目录
    source_path = find_source_directory(package_name, source_dir)
    if not source_path:
        print(f"错误: 未找到包 {package_name} 的源码目录")
        print()
        return
    
    # 获取翻译统计
    success, output = get_translation_stats(source_path)
    if not success:
        print(output)
        print()
        return
    
    # 过滤并输出结果
    filtered_output = filter_translation_lines(output, languages)
    if filtered_output.strip():
        print(filtered_output)
    else:
        lang_list = ', '.join(languages)
        print(f"未找到包含 {lang_list} 的翻译统计信息")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='翻译完成度统计工具')
    parser.add_argument('package_file', help='包名列表文件路径')
    parser.add_argument('--source-dir', default='pkg-sources', 
                       help='源码存储目录 (默认: pkg-sources)')
    parser.add_argument('--languages', default='zh_CN,zh_HK,zh_TW',
                       help='要统计的语言列表，用逗号分隔 (默认: zh_CN,zh_HK,zh_TW)')
    
    args = parser.parse_args()
    
    # 检查依赖
    check_dependencies()
    
    # 解析语言列表
    languages = [lang.strip() for lang in args.languages.split(',') if lang.strip()]
    if not languages:
        print("错误: 语言列表为空", file=sys.stderr)
        sys.exit(1)
    
    # 读取包名列表
    packages = read_package_list(args.package_file)
    if not packages:
        print("错误: 包名列表为空", file=sys.stderr)
        sys.exit(1)
    
    # 创建源码存储目录
    source_dir = Path(args.source_dir)
    source_dir.mkdir(exist_ok=True)
    
    # 处理每个包
    for package_name in packages:
        process_package(package_name, source_dir, languages)


if __name__ == "__main__":
    main()
