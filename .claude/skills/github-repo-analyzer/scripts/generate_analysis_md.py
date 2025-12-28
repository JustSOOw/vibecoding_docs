#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
# -*- coding: utf-8 -*-
"""
生成适合 LLM 直接分析的 Markdown 格式数据
解决 Read 工具单行字符限制导致的内容截断问题

运行方式：uv run scripts/generate_analysis_md.py <json_file>
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict


def generate_markdown(data: Dict) -> str:
    """将 JSON 数据转换为格式化的 Markdown，适合 LLM 分析"""

    md_lines = []

    # 基本信息
    md_lines.append("# GitHub Repository Analysis Data")
    md_lines.append("")
    md_lines.append(f"**Repository**: {data.get('repository_url', '')}")
    md_lines.append(f"**Owner**: {data.get('owner', '')}")
    md_lines.append(f"**Name**: {data.get('repo', '')}")
    md_lines.append("")

    # 统计信息
    basic = data.get('basic_info', {})
    md_lines.append("## Basic Statistics")
    md_lines.append("")
    md_lines.append(f"- **Stars**: {basic.get('stars', 0):,}")
    md_lines.append(f"- **Forks**: {basic.get('forks', 0):,}")
    md_lines.append(f"- **Open Issues**: {basic.get('open_issues', 0):,}")
    md_lines.append(f"- **Language**: {basic.get('language', 'N/A')}")
    md_lines.append(f"- **License**: {basic.get('license', 'N/A')}")
    md_lines.append(f"- **Topics**: {', '.join(basic.get('topics', []))}")
    md_lines.append(f"- **Created**: {basic.get('created_at', 'N/A')}")
    md_lines.append(f"- **Last Updated**: {basic.get('updated_at', 'N/A')}")
    md_lines.append(f"- **Last Push**: {basic.get('pushed_at', 'N/A')}")
    md_lines.append("")

    # README 内容（完整保留）
    readme = data.get('readme_content', '')
    if readme:
        md_lines.append("## README Content")
        md_lines.append("")
        md_lines.append("```markdown")
        md_lines.append(readme)
        md_lines.append("```")
        md_lines.append("")

    # Issues（完整保留正文）
    issues = data.get('issues', [])
    if issues:
        md_lines.append("## Issues")
        md_lines.append("")
        md_lines.append(f"Total Issues: {len(issues)}")
        md_lines.append("")
        for issue in issues:
            md_lines.append(f"### Issue #{issue.get('number')} - {issue.get('title', '')}")
            md_lines.append("")
            md_lines.append(f"- **State**: {issue.get('state', '')}")
            md_lines.append(f"- **Author**: {issue.get('author', '')}")
            md_lines.append(f"- **Created**: {issue.get('created_at', '')}")
            md_lines.append(f"- **Updated**: {issue.get('updated_at', '')}")
            md_lines.append(f"- **Comments**: {issue.get('comments', 0)}")
            md_lines.append(f"- **Reactions**: {issue.get('reactions', 0)}")

            labels = issue.get('labels', [])
            if labels:
                md_lines.append(f"- **Labels**: {', '.join(labels)}")

            md_lines.append("")
            md_lines.append("**Body**:")
            md_lines.append("")
            md_lines.append("```")
            md_lines.append(issue.get('body', '') or '(no content)')
            md_lines.append("```")
            md_lines.append("")

    # Releases（完整保留发布说明）
    releases = data.get('releases', [])
    if releases:
        md_lines.append("## Releases")
        md_lines.append("")
        md_lines.append(f"Total Releases: {len(releases)}")
        md_lines.append("")
        for release in releases:
            md_lines.append(f"### {release.get('name', '')} ({release.get('tag_name', '')})")
            md_lines.append("")
            md_lines.append(f"- **Published**: {release.get('published_at', '')}")
            md_lines.append(f"- **Author**: {release.get('author', '')}")
            md_lines.append(f"- **Prerelease**: {release.get('prerelease', False)}")
            md_lines.append("")
            md_lines.append("**Release Notes**:")
            md_lines.append("")
            md_lines.append("```markdown")
            md_lines.append(release.get('body', '') or '(no release notes)')
            md_lines.append("```")
            md_lines.append("")

    # Documents（完整保留内容）
    docs = data.get('documents', {})
    if docs:
        md_lines.append("## Documentation Files")
        md_lines.append("")
        md_lines.append(f"Total Documents: {len(docs)}")
        md_lines.append("")
        for doc_name, doc_content in docs.items():
            md_lines.append(f"### {doc_name}")
            md_lines.append("")
            md_lines.append("```markdown")
            md_lines.append(doc_content)
            md_lines.append("```")
            md_lines.append("")

    # PR 模板
    pr_template = data.get('pr_template', '')
    if pr_template:
        md_lines.append("## Pull Request Template")
        md_lines.append("")
        md_lines.append("```markdown")
        md_lines.append(pr_template)
        md_lines.append("```")
        md_lines.append("")

    # Issue 模板
    issue_templates = data.get('issue_templates', [])
    if issue_templates:
        md_lines.append("## Issue Templates")
        md_lines.append("")
        for template in issue_templates:
            md_lines.append(f"- {template}")
        md_lines.append("")

    # GitHub Actions 工作流
    workflows = data.get('workflows', [])
    if workflows:
        md_lines.append("## GitHub Actions Workflows")
        md_lines.append("")
        md_lines.append(f"Total Workflows: {len(workflows)}")
        md_lines.append("")
        for workflow in workflows:
            md_lines.append(f"- {workflow}")
        md_lines.append("")

    # 目录结构
    root_structure = data.get('root_structure', [])
    if root_structure:
        md_lines.append("## Repository Root Structure")
        md_lines.append("")
        for item in root_structure:
            icon = "📁" if item.get('type') == 'dir' else "📄"
            md_lines.append(f"{icon} {item.get('name', '')}")
        md_lines.append("")

    # Docs 目录
    docs_dir = data.get('docs_directory', [])
    if docs_dir:
        md_lines.append("## Documentation Directory")
        md_lines.append("")
        for item in docs_dir:
            md_lines.append(f"- {item}")
        md_lines.append("")

    # README 链接
    readme_links = data.get('readme_links', [])
    if readme_links:
        md_lines.append("## README Links")
        md_lines.append("")
        md_lines.append(f"Total Links: {len(readme_links)}")
        md_lines.append("")
        for link in readme_links[:20]:  # 限制前 20 个
            text = link.get('text', '')
            url = link.get('url', '')
            md_lines.append(f"- [{text}]({url})")
        if len(readme_links) > 20:
            md_lines.append(f"- ... and {len(readme_links) - 20} more links")
        md_lines.append("")

    return "\n".join(md_lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将 analysis_ready.json 转换为适合 LLM 分析的 Markdown 格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python generate_analysis_md.py output/facebook_react/analysis_ready.json
  python generate_analysis_md.py input.json -o output.md

这个脚本解决了 Read 工具单行 2000 字符限制导致的内容截断问题。
生成的 Markdown 文件可以被 LLM 完整读取和分析。
        '''
    )

    parser.add_argument(
        'input_file',
        help='输入的 analysis_ready.json 文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        help='输出文件名（可选，默认为 {input}_for_llm.md）'
    )

    args = parser.parse_args()

    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_for_llm.md")

    # 读取 JSON
    print(f"📖 读取: {args.input_file}")
    with open(args.input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 生成 Markdown
    print(f"🔄 生成 Markdown 格式...")
    markdown_content = generate_markdown(data)

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"✅ Markdown 文件已保存: {output_file}")
    print(f"📏 文件大小: {len(markdown_content):,} 字符")
    print(f"📄 文件行数: {markdown_content.count(chr(10)) + 1:,} 行")
    print(f"\n💡 现在 LLM 可以完整读取所有内容进行分析！")


if __name__ == '__main__':
    main()
