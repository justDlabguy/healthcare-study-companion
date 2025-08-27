#!/usr/bin/env python3
import re
from datetime import datetime
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import sys
import argparse

class TaskManager:
    def __init__(self, plan_file: str = "plan.md"):
        self.plan_file = Path(plan_file)
        self.content = self._read_plan()
        self.sections = self._parse_sections()
        
    def _read_plan(self) -> List[str]:
        if not self.plan_file.exists():
            self._create_default_plan()
        return self.plan_file.read_text(encoding='utf-8').splitlines()
    
    def _create_default_plan(self):
        default_content = """# Project Plan

## Project Overview
- **Project Name**: [Project Name]
- **Description**: [Brief description of the project]
- **Start Date**: [YYYY-MM-DD]
- **Target Completion Date**: [YYYY-MM-DD]

## Tasks

### Backlog
- [ ] Sample Task (Details: This is a sample task, Priority: Medium)

### In Progress

### Completed

## Progress
- **Total Tasks**: 1
- **Completed**: 0 (0%)
- **Remaining**: 1
- **Last Updated**: {0}""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.plan_file.write_text(default_content, encoding='utf-8')
        return default_content.splitlines()

    def _parse_sections(self) -> Dict[str, List[str]]:
        sections = {}
        current_section = None
        
        for line in self.content:
            if line.startswith('### '):
                current_section = line[4:].strip()
                sections[current_section] = []
            elif current_section is not None and line.strip():
                sections[current_section].append(line)
        
        return sections

    def add_task(self, title: str, details: str = "", priority: str = "Medium", section: str = "Backlog"):
        task = f"- [ ] {title}"
        if details or priority:
            task += f" (Details: {details}, Priority: {priority})"
        
        if section not in self.sections:
            self.sections[section] = []
        
        self.sections[section].append(task)
        self._update_progress()
        self._write_plan()
        return task

    def update_task_status(self, task_title: str, new_status: str):
        task_found = False
        current_section = None
        
        for section, tasks in list(self.sections.items()):
            for i, task in enumerate(tasks):
                if task_title.lower() in task.lower():
                    current_section = section
                    task_content = tasks.pop(i)
                    task_found = True
                    
                    # Update task status
                    if new_status.lower() == 'in progress':
                        task_content = task_content.replace('- [ ]', '- [•]')
                        task_content += f" (Assigned to: [Name], Started: {datetime.now().strftime('%Y-%m-%d')})"
                        self.sections.setdefault('In Progress', []).append(task_content)
                    elif new_status.lower() == 'completed':
                        task_content = task_content.replace('- [ ]', '- [x]')
                        if '(Assigned to:' in task_content:
                            task_content = task_content.split('(Assigned to:')[0].strip()
                        task_content += f" (Completed: {datetime.now().strftime('%Y-%m-%d')})"
                        self.sections.setdefault('Completed', []).append(task_content)
                    else:
                        tasks.insert(i, task_content)  # Put it back if status is unknown
                    
                    break
        
        if task_found:
            self._update_progress()
            self._write_plan()
            return True
        return False

    def _update_progress(self):
        total_tasks = 0
        completed_tasks = 0
        
        for section, tasks in self.sections.items():
            for task in tasks:
                if task.strip().startswith('- ['):
                    total_tasks += 1
                    if task.strip().startswith('- [x]') or task.strip().startswith('- [X]'):
                        completed_tasks += 1
        
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        remaining = total_tasks - completed_tasks
        
        # Update progress section
        progress_lines = [
            "## Progress",
            f"- **Total Tasks**: {total_tasks}",
            f"- **Completed**: {completed_tasks} ({progress:.1f}%)",
            f"- **Remaining**: {remaining}",
            f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        self.sections['Progress'] = progress_lines

    def _write_plan(self):
        output = ["# Project Plan\n"]
        output.append("## Project Overview")
        output.extend([line for line in self.content if line.startswith("- **")])
        output.append("\n## Tasks\n")
        
        for section, tasks in self.sections.items():
            if section == 'Progress':
                continue
            output.append(f"### {section}")
            output.extend(tasks)
            output.append("")
        
        output.append("## Progress")
        output.extend([line for line in self.sections.get('Progress', []) if not line.startswith('##')])
        
        self.plan_file.write_text('\n'.join(output), encoding='utf-8')
        
        # Commit changes to git
        try:
            subprocess.run(["git", "add", str(self.plan_file)], check=True)
            subprocess.run(["git", "commit", "-m", f"docs: update project plan - {datetime.now().strftime('%Y-%m-%d %H:%M')}"], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not commit changes to git: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Manage project tasks in plan.md")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Add task command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('title', help='Task title')
    add_parser.add_argument('--details', default="", help='Task details')
    add_parser.add_argument('--priority', default="Medium", choices=["High", "Medium", "Low"], 
                          help='Task priority')
    add_parser.add_argument('--section', default="Backlog", 
                          choices=["Backlog", "In Progress", "Completed"],
                          help='Section to add the task to')
    
    # Update task command
    update_parser = subparsers.add_parser('update', help='Update task status')
    update_parser.add_argument('title', help='Task title (partial match)')
    update_parser.add_argument('status', choices=['in progress', 'completed'], 
                             help='New status for the task')
    
    args = parser.parse_args()
    manager = TaskManager()
    
    if args.command == 'add':
        task = manager.add_task(args.title, args.details, args.priority, args.section)
        print(f"Added task: {task}")
    elif args.command == 'update':
        if manager.update_task_status(args.title, args.status):
            print(f"Task '{args.title}' marked as {args.status}")
        else:
            print(f"Task '{args.title}' not found", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()