#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
# -*- coding: utf-8 -*-
"""
数据预处理脚本
从完整的 GitHub 仓库 JSON 数据中提取关键文本信息，生成适合 LLM 分析的精简数据。

核心目的：
- 去除无用的 JSON 元数据（API URLs、SHA 值、编码信息等）
- 提取有价值的文本内容（完整保留，不截断）
- 生成结构清晰的分析就绪数据

运行方式：uv run scripts/prepare_for_analysis.py <json_file>
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


def extract_basic_info(data: Dict) -> Dict:
    """提取基础信息（只保留有价值的字段，去除 API URLs 等无用信息）"""
    basic = data.get('basic_info', {})
    return {
        'name': basic.get('name', ''),
        'full_name': basic.get('full_name', ''),
        'description': basic.get('description', ''),
        'homepage': basic.get('homepage', ''),
        'html_url': basic.get('html_url', ''),
        'stars': basic.get('stargazers_count', 0),
        'forks': basic.get('forks_count', 0),
        'watchers': basic.get('watchers_count', 0),
        'open_issues': basic.get('open_issues_count', 0),
        'language': basic.get('language', ''),
        'license': basic.get('license', {}).get('name', '') if basic.get('license') else '',
        'topics': basic.get('topics', []),
        'created_at': basic.get('created_at', ''),
        'updated_at': basic.get('updated_at', ''),
        'pushed_at': basic.get('pushed_at', ''),
        'default_branch': basic.get('default_branch', ''),
        'size_kb': basic.get('size', 0),
        'is_fork': basic.get('fork', False),
        'archived': basic.get('archived', False),
    }


def extract_readme(data: Dict) -> str:
    """提取完整的 README 内容"""
    readme = data.get('readme', {})
    return readme.get('decoded_content', '')


def extract_issues(data: Dict) -> List[Dict]:
    """提取 Issues 信息（完整保留正文内容）"""
    issues = data.get('issues', [])
    extracted = []
    
    for issue in issues:
        extracted.append({
            'number': issue.get('number', 0),
            'title': issue.get('title', ''),
            'state': issue.get('state', ''),
            'comments': issue.get('comments', 0),
            'reactions': issue.get('reactions', {}).get('total_count', 0),
            'created_at': issue.get('created_at', ''),
            'updated_at': issue.get('updated_at', ''),
            'author': issue.get('user', {}).get('login', ''),
            'labels': [label.get('name', '') for label in issue.get('labels', [])],
            'body': issue.get('body', '') or '',  # 完整保留正文
        })
    
    return extracted


def extract_releases(data: Dict) -> List[Dict]:
    """提取 Releases 信息（完整保留发布说明）"""
    releases = data.get('releases', [])
    extracted = []
    
    for release in releases:
        extracted.append({
            'tag_name': release.get('tag_name', ''),
            'name': release.get('name', ''),
            'published_at': release.get('published_at', ''),
            'author': release.get('author', {}).get('login', ''),
            'prerelease': release.get('prerelease', False),
            'body': release.get('body', '') or '',  # 完整保留发布说明
        })
    
    return extracted


def extract_docs(data: Dict) -> Dict[str, str]:
    """提取文档内容（完整保留所有内容）"""
    common_docs = data.get('common_docs', {})
    extracted = {}
    
    for doc_name, doc_data in common_docs.items():
        content = doc_data.get('decoded_content', '')
        if content:
            extracted[doc_name] = content  # 完整保留内容
    
    return extracted


def extract_workflows(data: Dict) -> List[str]:
    """提取工作流名称"""
    workflows = data.get('workflows', [])
    if not workflows:
        return []
    return [wf.get('name', 'unknown') for wf in workflows]


def extract_root_structure(data: Dict) -> List[Dict]:
    """提取根目录结构"""
    root = data.get('root_contents', [])
    if not root:
        return []
    return [
        {'name': item.get('name', ''), 'type': item.get('type', '')}
        for item in root
    ]


def extract_docs_directory(data: Dict) -> List[str]:
    """提取 docs 目录结构"""
    docs_dir = data.get('docs_directory', [])
    if not docs_dir:
        return []
    return [item.get('name', '') for item in docs_dir]


def extract_readme_links(data: Dict) -> List[Dict]:
    """提取 README 中的链接"""
    return data.get('readme_links', [])


def extract_pr_template(data: Dict) -> str:
    """提取 PR 模板内容"""
    pr_template = data.get('pr_template', {})
    if pr_template:
        return pr_template.get('decoded_content', '')
    return ''


def extract_issue_templates(data: Dict) -> List[str]:
    """提取 Issue 模板名称列表"""
    templates = data.get('issue_templates', [])
    if not templates:
        return []
    return [t.get('name', '') for t in templates]


def prepare_for_analysis(input_file: str, output_file: Optional[str] = None) -> Dict:
    """
    主处理函数：从完整 JSON 提取关键文本信息
    
    核心原则：
    - 去除无用元数据（API URLs、SHA、node_id 等）
    - 保留所有有价值的文本内容（不截断）
    - 生成结构清晰的数据
    
    Args:
        input_file: 输入的完整 JSON 文件路径
        output_file: 输出的精简 JSON 文件路径（可选）
    
    Returns:
        精简后的数据字典
    """
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取关键信息（完整保留文本内容）
    analysis_data = {
        'repository_url': data.get('repository_url', ''),
        'owner': data.get('owner', ''),
        'repo': data.get('repo', ''),
        'basic_info': extract_basic_info(data),
        'readme_content': extract_readme(data),
        'readme_links': extract_readme_links(data),
        'issues': extract_issues(data),
        'releases': extract_releases(data),
        'documents': extract_docs(data),
        'pr_template': extract_pr_template(data),
        'issue_templates': extract_issue_templates(data),
        'workflows': extract_workflows(data),
        'root_structure': extract_root_structure(data),
        'docs_directory': extract_docs_directory(data),
    }
    
    # 添加统计信息
    analysis_data['stats'] = {
        'readme_length': len(analysis_data['readme_content']),
        'total_issues': len(analysis_data['issues']),
        'total_releases': len(analysis_data['releases']),
        'total_docs': len(analysis_data['documents']),
        'total_workflows': len(analysis_data['workflows']),
        'has_pr_template': bool(analysis_data['pr_template']),
        'has_issue_templates': len(analysis_data['issue_templates']) > 0,
        'has_docs_directory': len(analysis_data['docs_directory']) > 0,
    }
    
    # 保存到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 分析就绪数据已保存到: {output_file}")
    
    return analysis_data


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='从完整 GitHub 仓库 JSON 数据中提取关键文本信息（去除无用元数据，保留完整内容）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python prepare_for_analysis.py output/facebook_react/raw_data.json
  python prepare_for_analysis.py input.json -o output.json

注意：此脚本只去除无用的 JSON 元数据（如 API URLs、SHA 值等），
所有有价值的文本内容（README、Issue 正文、Release 说明等）都会完整保留。
        '''
    )
    
    parser.add_argument(
        'input_file',
        help='输入的完整 JSON 文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件名（可选，默认为 {input}_analysis_ready.json）'
    )
    
    args = parser.parse_args()
    
    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        # 从输入文件名推断
        input_path = Path(args.input_file)
        base_name = input_path.stem
        if base_name.endswith('_info'):
            base_name = base_name[:-5]
        elif base_name == 'raw_data':
            base_name = 'analysis_ready'
        else:
            base_name = base_name + '_analysis_ready'
        output_file = str(input_path.parent / f"{base_name}.json")
    
    # 执行预处理
    result = prepare_for_analysis(args.input_file, output_file)
    
    # 打印统计
    stats = result['stats']
    print(f"\n📊 数据统计:")
    print(f"  • README: {stats['readme_length']:,} 字符")
    print(f"  • Issues: {stats['total_issues']} 个（完整正文）")
    print(f"  • Releases: {stats['total_releases']} 个（完整说明）")
    print(f"  • 文档: {stats['total_docs']} 个（完整内容）")
    print(f"  • 工作流: {stats['total_workflows']} 个")
    print(f"  • PR 模板: {'有' if stats['has_pr_template'] else '无'}")
    print(f"  • Issue 模板: {'有' if stats['has_issue_templates'] else '无'}")
    print(f"\n✨ 所有文本内容已完整保留，无截断处理")


if __name__ == '__main__':
    main()
