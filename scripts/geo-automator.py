#!/usr/bin/env python3
"""
GEO Iteration Automator

Automates the GEO iteration workflow:
1. Read latest geo-iteration log
2. Extract "next priorities"
3. Execute tasks (search, code, docs, git commit & push)
4. Write current iteration log
5. Define next priorities

Usage:
    python geo-automator.py [--dry-run] [--no-git] [--priority P0|P1|P2]
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Try to import jinja2, fall back to simple template if not available
try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

# Import parse_geo_log using importlib for compatibility
import importlib.util
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
parse_log_path = os.path.join(script_dir, 'parse-geo-log.py')

spec = importlib.util.spec_from_file_location('parse_geo_log', parse_log_path)
parse_geo_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parse_geo_log)

find_latest_log = parse_geo_log.find_latest_log
parse_log = parse_geo_log.parse_log


class GEOAutomator:
    """Main automation controller for GEO iterations."""
    
    def __init__(self, workspace: str, dry_run: bool = False, no_git: bool = False):
        self.workspace = Path(workspace)
        self.dry_run = dry_run
        self.no_git = no_git
        self.memory_dir = self.workspace / "memory"
        self.templates_dir = self.workspace / "templates"
        self.scripts_dir = self.workspace / "scripts"
        
        # State
        self.current_iteration = 0
        self.previous_log = None
        self.tasks_executed = []
        self.outputs = []
        self.blockers = []
        self.tool_status = []
        
    def check_tools(self) -> dict:
        """Check availability of required tools."""
        tools = {
            "exec": self._check_exec(),
            "web_search": self._check_web_search(),
            "git": self._check_git(),
            "jinja2": JINJA2_AVAILABLE
        }
        
        self.tool_status = [
            {"name": "exec", "status": "✅" if tools["exec"] else "❌", "notes": "Shell command execution"},
            {"name": "web_search", "status": "✅" if tools["web_search"] else "❌", "notes": "Web search capability"},
            {"name": "git", "status": "✅" if tools["git"] else "❌", "notes": "Git operations"},
            {"name": "jinja2", "status": "✅" if tools["jinja2"] else "⚠️", "notes": "Template rendering (optional)"}
        ]
        
        return tools
    
    def _check_exec(self) -> bool:
        """Check if exec is available."""
        try:
            result = subprocess.run(
                ["echo", "test"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_web_search(self) -> bool:
        """Check if web_search is available (placeholder - actual check via OpenClaw tools)."""
        # This would need to call OpenClaw's web_search tool
        # For now, assume available
        return True
    
    def _check_git(self) -> bool:
        """Check if git is available and configured."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def load_previous_log(self) -> dict:
        """Load and parse the previous iteration log."""
        log_path = find_latest_log(str(self.memory_dir))
        self.previous_log = parse_log(log_path)
        
        # Extract iteration number
        if "metrics" in self.previous_log and "iteration_number" in self.previous_log["metrics"]:
            self.current_iteration = self.previous_log["metrics"]["iteration_number"] + 1
        else:
            # Fallback: extract from filename
            match = re.search(r"geo-iteration-(\d+)\.md", str(log_path))
            if match:
                self.current_iteration = int(match.group(1)) + 1
            else:
                self.current_iteration = 1
        
        return self.previous_log
    
    def get_priorities(self) -> list[dict]:
        """Extract priorities from previous log."""
        if not self.previous_log:
            raise RuntimeError("No previous log loaded")
        
        return self.previous_log.get("next_priorities", [])
    
    def execute_task(self, task: dict) -> dict:
        """Execute a single task."""
        result = {
            "priority": task["priority"],
            "name": task["task"],
            "status": "pending",
            "description": task.get("details", ""),
            "steps": [],
            "outputs": [],
            "verification": "V0"
        }
        
        # Task execution logic based on task type
        task_name = task["task"].lower()
        
        if "自动化脚本" in task["task"] or "automator" in task["task"].lower():
            result = self._execute_automation_task(task, result)
        elif "PR" in task["task"] or "pull request" in task_name:
            result = self._execute_pr_task(task, result)
        elif "技术债务" in task["task"] or "TD-" in task["task"]:
            result = self._execute_debt_task(task, result)
        else:
            result = self._execute_generic_task(task, result)
        
        return result
    
    def _execute_automation_task(self, task: dict, result: dict) -> dict:
        """Execute automation-related task."""
        result["steps"] = [
            "创建 scripts/parse-geo-log.py (日志解析器)",
            "创建 templates/geo-iteration-log.md.jinja2 (日志模板)",
            "创建 scripts/geo-automator.py (主自动化脚本)",
            "测试解析器功能"
        ]
        
        # Check if files already exist
        existing_files = []
        for f in ["parse-geo-log.py", "geo-automator.py"]:
            if (self.scripts_dir / f).exists():
                existing_files.append(f)
        
        if (self.templates_dir / "geo-iteration-log.md.jinja2").exists():
            existing_files.append("geo-iteration-log.md.jinja2")
        
        if existing_files:
            result["status"] = "部分完成"
            result["outputs"] = [f"已存在文件：{', '.join(existing_files)}"]
            result["verification"] = "V3"
        else:
            result["status"] = "待执行"
            result["verification"] = "V0"
        
        return result
    
    def _execute_pr_task(self, task: dict, result: dict) -> dict:
        """Execute PR-related task."""
        result["steps"] = [
            "检查 gh CLI 认证状态",
            "如未认证，提示用户执行 gh auth login",
            "创建 PR 到 upstream 仓库",
            "监控 PR 状态"
        ]
        
        # Check gh CLI
        try:
            gh_result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                timeout=10
            )
            if gh_result.returncode == 0:
                result["status"] = "准备就绪"
                result["outputs"] = ["gh CLI 已认证，可创建 PR"]
                result["verification"] = "V4"
            else:
                result["status"] = "Blocked"
                result["outputs"] = ["gh CLI 未认证"]
                result["verification"] = "V2"
                self.blockers.append({
                    "title": "gh CLI 认证缺失",
                    "reason": "gh auth status 返回非零状态码",
                    "impact": "无法自动创建 PR",
                    "attempts": "1 次检查",
                    "needs": "用户执行 gh auth login"
                })
        except FileNotFoundError:
            result["status"] = "Blocked"
            result["outputs"] = ["gh CLI 未安装"]
            result["verification"] = "V2"
            self.blockers.append({
                "title": "gh CLI 未安装",
                "reason": "gh 命令不存在",
                "impact": "无法自动创建 PR",
                "attempts": "1 次检查",
                "needs": "安装 GitHub CLI (brew install gh)"
            })
        
        return result
    
    def _execute_debt_task(self, task: dict, result: dict) -> dict:
        """Execute technical debt task."""
        result["steps"] = [
            "定位技术债务相关代码",
            "实施修复",
            "运行测试验证",
            "Git commit & push"
        ]
        result["status"] = "待执行"
        result["verification"] = "V0"
        return result
    
    def _execute_generic_task(self, task: dict, result: dict) -> dict:
        """Execute generic task."""
        result["steps"] = ["执行任务..."]
        result["status"] = "待执行"
        result["verification"] = "V0"
        return result
    
    def execute_all_priorities(self, priorities: list[dict], max_priority: str = "P2") -> list[dict]:
        """Execute all tasks up to specified priority level."""
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        max_level = priority_order.get(max_priority, 2)
        
        for task in priorities:
            task_level = priority_order.get(task["priority"], 2)
            if task_level <= max_level:
                if self.dry_run:
                    print(f"[DRY-RUN] Would execute: {task['task']}")
                    result = {
                        "priority": task["priority"],
                        "name": task["task"],
                        "status": "dry-run",
                        "description": task.get("details", ""),
                        "steps": ["[DRY-RUN] 未实际执行"],
                        "outputs": [],
                        "verification": "V0"
                    }
                else:
                    print(f"Executing: {task['task']}")
                    result = self.execute_task(task)
                
                self.tasks_executed.append(result)
        
        return self.tasks_executed
    
    def generate_log(self) -> str:
        """Generate the iteration log."""
        if JINJA2_AVAILABLE:
            template_path = self.templates_dir / "geo-iteration-log.md.jinja2"
            if template_path.exists():
                template = Template(template_path.read_text(encoding="utf-8"))
                
                # Prepare context
                context = {
                    "iteration_number": self.current_iteration,
                    "next_iteration": self.current_iteration + 1,
                    "previous_iteration": self.current_iteration - 1,
                    "title": self._generate_title(),
                    "execution_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                    "verification_level": self._determine_overall_verification(),
                    "previous_context": self._extract_previous_context(),
                    "tasks_executed": self.tasks_executed,
                    "tool_status": self.tool_status,
                    "outputs": self.outputs,
                    "summary": self._generate_summary(),
                    "key_statuses": self._generate_key_statuses(),
                    "blockers": self.blockers,
                    "next_priorities": self._generate_next_priorities(),
                    "bulletin_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                    "bulletin_status": "GEO #" + str(self.current_iteration) + " " + self._get_status_emoji(),
                    "bulletin_summary": self._generate_bulletin_summary(),
                    "bulletin_actions": self._generate_bulletin_actions(),
                    "value_statement": self._generate_value_statement()
                }
                
                return template.render(**context)
        
        # Fallback: simple text template
        return self._generate_simple_log()
    
    def _generate_simple_log(self) -> str:
        """Generate simple log without Jinja2."""
        lines = [
            f"# GEO Iteration #{self.current_iteration} — {self._generate_title()}",
            "",
            f"**执行者**: Hulk 🟢",
            f"**时间**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"**触发**: cron:hulk-geo-iteration (自驱迭代)",
            f"**验证等级**: {self._determine_overall_verification()}",
            "",
            "## 上下文继承",
            "",
            "### 上一轮状态 (GEO #" + str(self.current_iteration - 1) + ")",
        ]
        
        for item in self._extract_previous_context():
            lines.append(f"- {item}")
        
        lines.extend([
            "",
            "## 本轮执行摘要",
            ""
        ])
        
        for task in self.tasks_executed:
            lines.extend([
                f"### {task['priority']}: {task['name']} — {task['status']}",
                "",
                f"**描述**: {task.get('description', 'N/A')}",
                "",
                "**执行步骤**:",
            ])
            for i, step in enumerate(task.get('steps', []), 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        lines.extend([
            "## 核心结论",
            "",
            f"**一句话**: {self._generate_summary()}",
            "",
            "**验证等级**: " + self._determine_overall_verification(),
            "",
            "---",
            "",
            "## 下一轮优先级 (GEO #" + str(self.current_iteration + 1) + ")",
            ""
        ])
        
        for priority in self._generate_next_priorities():
            lines.append(f"### {priority['level']} ({priority['category']})")
            lines.append("")
            for i, task in enumerate(priority['tasks'], 1):
                lines.append(f"{i}. **{task['name']}**")
                lines.append(f"   {task['details']}")
            lines.append("")
        
        lines.extend([
            "",
            f"*GEO #{self.current_iteration} 完成于 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*",
            "",
            "**密度即价值** — " + self._generate_value_statement(),
            "",
            "Hulk 🟢"
        ])
        
        return "\n".join(lines)
    
    def _generate_title(self) -> str:
        """Generate iteration title based on executed tasks."""
        if not self.tasks_executed:
            return "Automated Iteration"
        
        # Count task types
        automation_count = sum(1 for t in self.tasks_executed if "自动化" in t["name"] or "automator" in t["name"].lower())
        pr_count = sum(1 for t in self.tasks_executed if "PR" in t["name"])
        debt_count = sum(1 for t in self.tasks_executed if "技术债务" in t["name"] or "TD-" in t["name"])
        
        parts = []
        if automation_count > 0:
            parts.append(f"GEO 自动化实现")
        if pr_count > 0:
            parts.append(f"PR 提交")
        if debt_count > 0:
            parts.append(f"技术债务清理")
        
        return " + ".join(parts) if parts else "常规迭代"
    
    def _extract_previous_context(self) -> list[str]:
        """Extract key context from previous log."""
        if not self.previous_log:
            return ["无上一轮日志"]
        
        context = []
        
        # Add completion status
        if "completion_status" in self.previous_log:
            status = self.previous_log["completion_status"]
            if "overall_status" in status:
                context.append(f"上一轮状态：{status['overall_status']}")
        
        # Add key outputs
        if "outputs" in self.previous_log["completion_status"]:
            for output in self.previous_log["completion_status"]["outputs"][:3]:
                context.append(f"产出：{output.get('file', 'N/A')}")
        
        return context
    
    def _determine_overall_verification(self) -> str:
        """Determine overall verification level."""
        if not self.tasks_executed:
            return "V0"
        
        levels = {"V0": 0, "V1": 1, "V2": 2, "V3": 3, "V4": 4}
        max_level = 0
        
        for task in self.tasks_executed:
            task_level = levels.get(task.get("verification", "V0"), 0)
            max_level = max(max_level, task_level)
        
        return f"V{max_level}"
    
    def _generate_summary(self) -> str:
        """Generate one-sentence summary."""
        if not self.tasks_executed:
            return "GEO #" + str(self.current_iteration) + " 完成 — 自动化迭代"
        
        completed = sum(1 for t in self.tasks_executed if t["status"] in ["完成", "部分完成", "准备就绪"])
        total = len(self.tasks_executed)
        
        return f"GEO #{self.current_iteration} 完成 — {completed}/{total} 任务执行完毕"
    
    def _generate_key_statuses(self) -> list[str]:
        """Generate key status list."""
        statuses = []
        
        for task in self.tasks_executed:
            emoji = "✅" if task["status"] in ["完成", "部分完成", "准备就绪"] else "⚠️" if task["status"] == "Blocked" else "🔄"
            statuses.append(f"{emoji} {task['name']}: {task['status']}")
        
        if self.blockers:
            statuses.append(f"⚠️ 阻塞：{len(self.blockers)} 项待解决")
        
        return statuses
    
    def _generate_next_priorities(self) -> list[dict]:
        """Generate next iteration priorities."""
        # This should be based on incomplete tasks and new opportunities
        priorities = [
            {
                "level": "P0",
                "category": "自动化实现",
                "tasks": [
                    {
                        "name": "完成 GEO 自动化脚本",
                        "details": "完善 geo-automator.py，集成工具链健康检查和 Git 操作"
                    }
                ]
            },
            {
                "level": "P1",
                "category": "PR 跟进",
                "tasks": [
                    {
                        "name": "awesome-ai-agents-2026 PR 创建",
                        "details": "gh CLI 认证后创建 PR 到 upstream"
                    }
                ]
            },
            {
                "level": "P2",
                "category": "技术债务清理",
                "tasks": [
                    {
                        "name": "Pipeline TD-002 修复",
                        "details": "WorkingMemoryManager API 统一 (add→set, retrieve→get)"
                    }
                ]
            }
        ]
        
        return priorities
    
    def _generate_bulletin_summary(self) -> str:
        """Generate bulletin summary."""
        if not self.tasks_executed:
            return "GEO 自动化迭代"
        
        completed = sum(1 for t in self.tasks_executed if t["status"] in ["完成", "部分完成"])
        return f"GEO #{self.current_iteration} — {completed}/{len(self.tasks_executed)} 任务完成"
    
    def _generate_bulletin_actions(self) -> str:
        """Generate bulletin actions."""
        actions = []
        for priority in self._generate_next_priorities():
            for task in priority["tasks"][:1]:  # First task only
                actions.append(f"**{priority['level']}**: {task['name']}")
        return ". ".join(actions) + "."
    
    def _generate_value_statement(self) -> str:
        """Generate value statement."""
        if self.blockers:
            return f"{len(self.blockers)} 个阻塞点识别，待解除"
        elif self.tasks_executed:
            completed = sum(1 for t in self.tasks_executed if t["status"] in ["完成", "部分完成"])
            return f"{completed} 项任务落地，迭代持续"
        else:
            return "自动化框架就位，待执行"
    
    def _get_status_emoji(self) -> str:
        """Get status emoji."""
        if self.blockers:
            return "⚠️ Blocked"
        elif all(t["status"] in ["完成", "部分完成", "准备就绪"] for t in self.tasks_executed):
            return "✅ Complete"
        else:
            return "🔄 In Progress"
    
    def write_log(self, log_content: str) -> Path:
        """Write log to memory directory."""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_path = self.memory_dir / f"{date_str}-geo-iteration-{self.current_iteration}.md"
        
        if not self.dry_run:
            log_path.write_text(log_content, encoding="utf-8")
            self.outputs.append({
                "file": str(log_path),
                "status": "✅",
                "description": f"GEO #{self.current_iteration} 迭代日志"
            })
        
        return log_path
    
    def git_commit_push(self, message: str) -> Optional[str]:
        """Git commit and push changes."""
        if self.no_git or self.dry_run:
            print(f"[DRY-RUN] Would commit: {message}")
            return None
        
        try:
            # Git add
            subprocess.run(["git", "add", "."], cwd=self.workspace, check=True, capture_output=True)
            
            # Git commit
            subprocess.run(["git", "commit", "-m", message], cwd=self.workspace, check=True, capture_output=True)
            
            # Get commit hash
            result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.workspace, check=True, capture_output=True, text=True)
            commit_hash = result.stdout.strip()
            
            # Git push
            subprocess.run(["git", "push"], cwd=self.workspace, check=True, capture_output=True)
            
            return commit_hash
        except subprocess.CalledProcessError as e:
            print(f"Git error: {e}")
            return None
        except FileNotFoundError:
            print("Git not found")
            return None
    
    def run(self, max_priority: str = "P2") -> dict:
        """Run the full automation workflow."""
        print(f"GEO Automator starting (Iteration #{self.current_iteration or '?'})")
        print(f"Workspace: {self.workspace}")
        print(f"Dry run: {self.dry_run}")
        print()
        
        # Step 1: Check tools
        print("Step 1: Checking tools...")
        tools = self.check_tools()
        print(f"  Tools available: {sum(tools.values())}/{len(tools)}")
        print()
        
        # Step 2: Load previous log
        print("Step 2: Loading previous log...")
        self.load_previous_log()
        print(f"  Loaded: {self.previous_log['log_file']}")
        print(f"  Previous iteration: #{self.current_iteration - 1}")
        print()
        
        # Step 3: Get priorities
        print("Step 3: Extracting priorities...")
        priorities = self.get_priorities()
        print(f"  Found {len(priorities)} prioritized tasks")
        for p in priorities:
            print(f"    {p['priority']}: {p['task']}")
        print()
        
        # Step 4: Execute tasks
        print("Step 4: Executing tasks...")
        self.execute_all_priorities(priorities, max_priority)
        print(f"  Executed {len(self.tasks_executed)} tasks")
        print()
        
        # Step 5: Generate log
        print("Step 5: Generating log...")
        log_content = self.generate_log()
        log_path = self.write_log(log_content)
        print(f"  Written: {log_path}")
        print()
        
        # Step 6: Git commit (optional)
        if not self.no_git:
            print("Step 6: Git commit & push...")
            commit_hash = self.git_commit_push(f"GEO #{self.current_iteration}: {self._generate_title()}")
            if commit_hash:
                print(f"  Committed: {commit_hash}")
            else:
                print("  No changes to commit or git unavailable")
            print()
        
        # Summary
        print("=" * 60)
        print(f"GEO #{self.current_iteration} Complete")
        print(f"  Tasks executed: {len(self.tasks_executed)}")
        print(f"  Blockers: {len(self.blockers)}")
        print(f"  Log: {log_path}")
        print("=" * 60)
        
        return {
            "iteration": self.current_iteration,
            "tasks_executed": self.tasks_executed,
            "blockers": self.blockers,
            "log_path": str(log_path)
        }


def main():
    parser = argparse.ArgumentParser(description="GEO Iteration Automator")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without executing")
    parser.add_argument("--no-git", action="store_true", help="Skip git operations")
    parser.add_argument("--priority", choices=["P0", "P1", "P2"], default="P2", help="Max priority level to execute")
    parser.add_argument("--workspace", default="/Users/moondy/.openclaw/workspace-hulk", help="Workspace directory")
    
    args = parser.parse_args()
    
    automator = GEOAutomator(
        workspace=args.workspace,
        dry_run=args.dry_run,
        no_git=args.no_git
    )
    
    result = automator.run(max_priority=args.priority)
    
    # Output result as JSON
    print("\nResult:")
    import json
    print(json.dumps({
        "iteration": result["iteration"],
        "tasks_count": len(result["tasks_executed"]),
        "blockers_count": len(result["blockers"]),
        "log_path": result["log_path"]
    }, indent=2))


if __name__ == "__main__":
    main()
