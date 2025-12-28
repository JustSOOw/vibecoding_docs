#!/usr/bin/env python3
# /// script
# dependencies = [
#   "requests>=2.31.0",
# ]
# ///
# -*- coding: utf-8 -*-
"""
GitHub 仓库信息获取脚本
获取仓库的所有重要信息，包括 README、Issues、Actions 等

依赖管理：使用 PEP 723 内联依赖声明
运行方式：uv run scripts/fetch_repo_info.py <仓库URL>
虚拟环境：自动管理在系统缓存 (~/.cache/uv/)，不会污染项目或 Skill 目录
"""

import os
import sys
import json
import base64
import re
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import requests


class GitHubRepoAnalyzer:
    """GitHub 仓库分析器"""
    
    # 常见文档文件列表
    COMMON_DOCS = [
        "CHANGELOG.md", "CHANGELOG",
        "SECURITY.md", "SECURITY",
        "FAQ.md", "FAQ",
        "ROADMAP.md", "ROADMAP",
        "ARCHITECTURE.md",
        "DEVELOPMENT.md",
        "INSTALLATION.md",
        "CONFIGURATION.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "LICENSE", "LICENSE.md",
    ]
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            token: GitHub Personal Access Token，如果为 None 则按优先级从多个来源读取：
                   1. .env 文件
                   2. 环境变量 GITHUB_TOKEN
        """
        self.token = token or self._load_token()
        if not self.token:
            print("⚠️  警告: 未设置 GITHUB_TOKEN，将使用未认证请求（速率限制: 60次/小时）")
            print("ℹ️  建议: 复制 .env.example 为 .env 并填入你的 Token")
        
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
        
        self.base_url = 'https://api.github.com'
    
    def _load_token(self) -> Optional[str]:
        """
        从多个来源加载 Token（按优先级）
        
        Returns:
            Token 字符串，如果未找到则返回 None
        """
        # 1. 尝试从 .env 文件读取
        env_file = Path(__file__).parent.parent / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if line.startswith('GITHUB_TOKEN='):
                                token = line.split('=', 1)[1].strip()
                                if token and token != 'your_token_here':
                                    return token
            except Exception as e:
                print(f"⚠️  读取 .env 文件失败: {e}")
        
        # 2. 从环境变量读取
        return os.getenv('GITHUB_TOKEN')
    
    def parse_repo_url(self, repo_url: str) -> tuple:
        """
        解析仓库 URL，提取 owner 和 repo 名称
        
        Args:
            repo_url: GitHub 仓库 URL，例如 https://github.com/facebook/react
        
        Returns:
            (owner, repo) 元组
        """
        # 移除可能的 .git 后缀
        repo_url = repo_url.rstrip('/')
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        # 解析 URL
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]
        else:
            raise ValueError(f"无效的仓库 URL: {repo_url}")
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        发送 GitHub API 请求
        
        Args:
            endpoint: API 端点
            params: 查询参数
        
        Returns:
            响应 JSON 数据，如果失败则返回 None
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"⚠️  资源未找到: {endpoint}")
                return None
            else:
                print(f"⚠️  请求失败 ({response.status_code}): {endpoint}")
                return None
        except Exception as e:
            print(f"❌ 请求异常: {endpoint} - {e}")
            return None
    
    def get_basic_info(self, owner: str, repo: str) -> Optional[Dict]:
        """获取仓库基础信息"""
        print("📊 获取基础信息...")
        return self.make_request(f'/repos/{owner}/{repo}')
    
    def get_readme(self, owner: str, repo: str) -> Optional[Dict]:
        """获取 README 内容"""
        print("📖 获取 README...")
        data = self.make_request(f'/repos/{owner}/{repo}/readme')
        if data and 'content' in data:
            # 解码 Base64 内容
            try:
                content = base64.b64decode(data['content']).decode('utf-8')
                data['decoded_content'] = content
            except Exception as e:
                print(f"⚠️  解码 README 失败: {e}")
        return data
    
    def extract_links_from_markdown(self, content: str) -> List[str]:
        """
        从 Markdown 内容中提取链接
        
        Args:
            content: Markdown 文本
        
        Returns:
            链接列表
        """
        # 匹配 [text](url) 格式的链接
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        links = []
        for text, url in matches:
            # 只保留相对路径（仓库内部文档）
            if not url.startswith(('http://', 'https://', '#', 'mailto:')):
                links.append({'text': text, 'url': url})
        
        return links
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[Dict]:
        """
        获取指定文件的内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件路径
        
        Returns:
            文件信息和内容
        """
        data = self.make_request(f'/repos/{owner}/{repo}/contents/{path}')
        if data and isinstance(data, dict) and 'content' in data:
            try:
                content = base64.b64decode(data['content']).decode('utf-8')
                data['decoded_content'] = content
            except:
                pass
        return data
    
    def get_common_docs(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取常见文档文件"""
        print("📄 检测常见文档文件...")
        docs = {}
        
        for doc_name in self.COMMON_DOCS:
            data = self.get_file_content(owner, repo, doc_name)
            if data:
                docs[doc_name] = data
                print(f"  ✓ 找到: {doc_name}")
        
        return docs
    
    def get_directory_contents(self, owner: str, repo: str, path: str = '') -> Optional[List]:
        """
        获取目录内容
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 目录路径，默认为根目录
        
        Returns:
            文件和目录列表
        """
        endpoint = f'/repos/{owner}/{repo}/contents/{path}' if path else f'/repos/{owner}/{repo}/contents'
        return self.make_request(endpoint)
    
    def get_docs_directory(self, owner: str, repo: str) -> Optional[List]:
        """获取 docs/ 目录内容"""
        print("📚 扫描 docs/ 目录...")
        data = self.get_directory_contents(owner, repo, 'docs')
        if data:
            print(f"  ✓ 找到 {len(data)} 个文件/目录")
        return data
    
    def get_issues(self, owner: str, repo: str, sort: str = 'reactions', per_page: int = 10) -> Optional[List]:
        """
        获取 Issues
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sort: 排序方式，默认按反应数
            per_page: 每页数量
        
        Returns:
            Issue 列表
        """
        print(f"🔥 获取 Top {per_page} 热门 Issues...")
        params = {
            'sort': sort,
            'per_page': per_page,
            'state': 'all'  # 包含开放和关闭的 Issue
        }
        return self.make_request(f'/repos/{owner}/{repo}/issues', params)
    
    def get_workflows(self, owner: str, repo: str) -> Optional[List]:
        """获取 GitHub Actions 工作流"""
        print("⚙️  获取 GitHub Actions 工作流...")
        data = self.get_directory_contents(owner, repo, '.github/workflows')
        if data:
            print(f"  ✓ 找到 {len(data)} 个工作流")
        return data
    
    def get_releases(self, owner: str, repo: str, per_page: int = 5) -> Optional[List]:
        """获取最新的 Releases"""
        print(f"🚀 获取最新 {per_page} 个 Releases...")
        params = {'per_page': per_page}
        return self.make_request(f'/repos/{owner}/{repo}/releases', params)
    
    def get_pr_template(self, owner: str, repo: str) -> Optional[Dict]:
        """获取 PR 模板"""
        print("📝 获取 PR 模板...")
        # PR 模板可能在多个位置
        possible_paths = [
            '.github/PULL_REQUEST_TEMPLATE.md',
            'PULL_REQUEST_TEMPLATE.md',
            '.github/pull_request_template.md',
        ]
        
        for path in possible_paths:
            data = self.get_file_content(owner, repo, path)
            if data:
                print(f"  ✓ 找到: {path}")
                return data
        
        return None
    
    def get_issue_templates(self, owner: str, repo: str) -> Optional[List]:
        """获取 Issue 模板"""
        print("📋 获取 Issue 模板...")
        data = self.get_directory_contents(owner, repo, '.github/ISSUE_TEMPLATE')
        if data:
            print(f"  ✓ 找到 {len(data)} 个模板")
        return data
    
    def analyze_repo(self, repo_url: str) -> Dict:
        """
        分析仓库并获取所有信息
        
        Args:
            repo_url: GitHub 仓库 URL
        
        Returns:
            包含所有信息的字典
        """
        print(f"\n🔍 开始分析仓库: {repo_url}\n")
        
        # 解析 URL
        owner, repo = self.parse_repo_url(repo_url)
        print(f"📦 仓库: {owner}/{repo}\n")
        
        # 收集所有信息
        result = {
            'repository_url': repo_url,
            'owner': owner,
            'repo': repo,
            'basic_info': self.get_basic_info(owner, repo),
            'readme': self.get_readme(owner, repo),
            'common_docs': self.get_common_docs(owner, repo),
            'docs_directory': self.get_docs_directory(owner, repo),
            'root_contents': self.get_directory_contents(owner, repo),
            'issues': self.get_issues(owner, repo),
            'workflows': self.get_workflows(owner, repo),
            'releases': self.get_releases(owner, repo),
            'pr_template': self.get_pr_template(owner, repo),
            'issue_templates': self.get_issue_templates(owner, repo),
        }
        
        # 从 README 中提取链接
        if result['readme'] and 'decoded_content' in result['readme']:
            readme_content = result['readme']['decoded_content']
            result['readme_links'] = self.extract_links_from_markdown(readme_content)
            print(f"\n🔗 从 README 中提取了 {len(result['readme_links'])} 个内部链接")
        
        print("\n✅ 分析完成！\n")
        return result


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='分析 GitHub 仓库并获取所有重要信息',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python fetch_repo_info.py https://github.com/facebook/react
  python fetch_repo_info.py https://github.com/torvalds/linux --token ghp_xxx
  python fetch_repo_info.py https://github.com/microsoft/vscode -o custom_output.json
        '''
    )
    
    parser.add_argument(
        'repo_url',
        help='GitHub 仓库 URL'
    )
    
    parser.add_argument(
        '-t', '--token',
        help='GitHub Personal Access Token（可选，也可通过 .env 文件或环境变量设置）'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件名（可选，默认保存到 output/{owner}_{repo}/raw_data.json）'
    )
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = GitHubRepoAnalyzer(token=args.token)
    
    # 分析仓库
    result = analyzer.analyze_repo(args.repo_url)
    
    # 确定输出路径
    if args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        # 默认保存到 output/{owner}_{repo}/ 目录
        script_dir = Path(__file__).parent.parent  # .claude/skills/github-repo-analyzer/
        output_dir = script_dir / 'output' / f"{result['owner']}_{result['repo']}"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'raw_data.json'
    
    # 保存为 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"📁 数据已保存到: {output_file}")


if __name__ == '__main__':
    main()

