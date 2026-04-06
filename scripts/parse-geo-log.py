#!/usr/bin/env python3
"""
GEO Iteration Log Parser

Parses GEO iteration logs to extract:
- Previous round's "next priorities" (下一轮优先级)
- Task completion status
- Key metrics (duration, outputs, verification levels)

Usage:
    python parse-geo-log.py <log-file>
    python parse-geo-log.py --latest  # Auto-find latest log
"""

import re
import sys
import json
from pathlib import Path
from datetime import datetime


def find_latest_log(memory_dir: str = "memory") -> Path:
    """Find the latest geo-iteration log file."""
    memory_path = Path(memory_dir)
    if not memory_path.exists():
        raise FileNotFoundError(f"Memory directory not found: {memory_dir}")
    
    # Pattern: YYYY-MM-DD-geo-iteration-N.md
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-geo-iteration-(\d+)\.md")
    
    logs = []
    for f in memory_path.iterdir():
        match = pattern.match(f.name)
        if match:
            date_str = match.group(1)
            iteration_num = int(match.group(2))
            logs.append((date_str, iteration_num, f))
    
    if not logs:
        raise FileNotFoundError("No geo-iteration logs found")
    
    # Sort by date, then by iteration number
    logs.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return logs[0][2]


def extract_next_priorities(content: str) -> list[dict]:
    """Extract '下一轮优先级' section from log content."""
    # Find the section - handle both "## 下一轮优先级" and "## 下一轮优先级 (GEO #N)"
    section_pattern = r"## 下一轮优先级.*?(?=##\s+(?:BULLETIN|\*|GEO|#|$)|$)"
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not section_match:
        return []
    
    section = section_match.group(0)
    priorities = []
    
    # Parse P0, P1, P2 sections - handle both "### P0 (category)" and "### P0: category"
    priority_pattern = r"###\s*(P[0-2])\s*(?:\(|:|\s)+([^\n]*)\n+(.*?)(?=###\s*P[0-2]|$)"
    for match in re.finditer(priority_pattern, section, re.DOTALL | re.IGNORECASE):
        priority_level = match.group(1)
        category = match.group(2).strip()
        tasks_text = match.group(3)
        
        # Parse individual tasks - handle "1. **task name**" followed by details
        task_pattern = r"(\d+)\.\s*\*\*([^*]+)\*\*\s*\n?(.*?)?(?=\d+\.\s*\*\*|$)"
        for task_match in re.finditer(task_pattern, tasks_text, re.DOTALL):
            task_num = task_match.group(1)
            task_name = task_match.group(2).strip()
            task_details = task_match.group(3).strip() if task_match.group(3) else ""
            
            # Clean up task details (remove leading whitespace and extra newlines)
            task_details = re.sub(r'^\s+', '', task_details)
            task_details = re.sub(r'\n\s*', ' ', task_details)
            
            priorities.append({
                "priority": priority_level,
                "category": category,
                "task": task_name,
                "details": task_details
            })
    
    return priorities


def extract_completion_status(content: str) -> dict:
    """Extract completion status from log."""
    status = {
        "completed_tasks": [],
        "blocked_tasks": [],
        "outputs": [],
        "verification_level": "V0"
    }
    
    # Find completion status
    status_pattern = r"## 状态\s*\n+(完成|部分完成|Blocked|纯巡检无新产出)"
    status_match = re.search(status_pattern, content)
    if status_match:
        status["overall_status"] = status_match.group(1)
    
    # Find outputs
    outputs_pattern = r"## 产出物清单.*?\| 文件\|(.*?)\| 状态\|(.*?)\|(.*?)\|(.*?)(?=##|$)"
    outputs_match = re.search(outputs_pattern, content, re.DOTALL)
    if outputs_match:
        # Parse table rows
        table_text = outputs_match.group(0)
        row_pattern = r"\| `(.+?)` \| (✅|⚠️|❌) .+? \| (.+?) \|"
        for row_match in re.finditer(row_pattern, table_text):
            status["outputs"].append({
                "file": row_match.group(1),
                "status": row_match.group(2),
                "description": row_match.group(3)
            })
    
    # Find verification level
    v_pattern = r"\*\*验证等级\*\*:\s*(V[0-4])"
    v_match = re.search(v_pattern, content)
    if v_match:
        status["verification_level"] = v_match.group(1)
    
    return status


def extract_metrics(content: str) -> dict:
    """Extract iteration metrics."""
    metrics = {}
    
    # Find execution time
    time_pattern = r"\*\*时间\*\*:\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC)"
    time_match = re.search(time_pattern, content)
    if time_match:
        metrics["execution_time"] = time_match.group(1)
    
    # Find iteration number
    iter_pattern = r"# GEO Iteration #(\d+)"
    iter_match = re.search(iter_pattern, content)
    if iter_match:
        metrics["iteration_number"] = int(iter_match.group(1))
    
    return metrics


def parse_log(log_path: Path) -> dict:
    """Parse a GEO iteration log file."""
    content = log_path.read_text(encoding="utf-8")
    
    return {
        "log_file": str(log_path),
        "parsed_at": datetime.utcnow().isoformat(),
        "metrics": extract_metrics(content),
        "next_priorities": extract_next_priorities(content),
        "completion_status": extract_completion_status(content),
        "raw_content": content[:500]  # First 500 chars for context
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse-geo-log.py <log-file|--latest>")
        sys.exit(1)
    
    if sys.argv[1] == "--latest":
        log_path = find_latest_log()
        print(f"Found latest log: {log_path}")
    else:
        log_path = Path(sys.argv[1])
        if not log_path.exists():
            print(f"Error: File not found: {log_path}")
            sys.exit(1)
    
    result = parse_log(log_path)
    
    # Output as JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
