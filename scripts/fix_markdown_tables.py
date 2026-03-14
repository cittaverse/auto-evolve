#!/usr/bin/env python3
"""Fix markdown table alignment for awesome-lint compliance."""

import re
import sys

def fix_table_alignment(content):
    """Fix table cell padding and alignment."""
    lines = content.split('\n')
    result = []
    in_table = False
    table_lines = []
    
    for i, line in enumerate(lines):
        # Detect table start (line with | and |---| pattern follows)
        if '|' in line and not in_table:
            # Check if next line is a separator
            if i + 1 < len(lines) and re.match(r'^\s*\|?\s*[-:|]+\s*\|', lines[i + 1]):
                in_table = True
                table_lines = [line]
                continue
        
        if in_table:
            if '|' in line or re.match(r'^\s*[-:|]+\s*$', line):
                table_lines.append(line)
            else:
                # Table ended, process and output
                result.extend(process_table(table_lines))
                table_lines = []
                in_table = False
                result.append(line)
        else:
            result.append(line)
    
    # Handle table at end of file
    if table_lines:
        result.extend(process_table(table_lines))
    
    return '\n'.join(result)

def process_table(table_lines):
    """Process a table and fix alignment."""
    if len(table_lines) < 2:
        return table_lines
    
    # Parse all rows
    rows = []
    for line in table_lines:
        # Split by | and clean
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        rows.append(cells)
    
    # Find max width for each column
    if not rows:
        return table_lines
    
    num_cols = max(len(row) for row in rows)
    col_widths = [0] * num_cols
    
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    # Ensure minimum width of 3 for separator row
    for i in range(num_cols):
        col_widths[i] = max(col_widths[i], 3)
    
    # Rebuild table with proper alignment
    result = []
    for row_idx, row in enumerate(rows):
        # Pad row to num_cols
        while len(row) < num_cols:
            row.append('')
        
        # Format cells with proper padding (1 space on each side)
        formatted_cells = []
        for i, cell in enumerate(row):
            # For separator row (contains ---), use dashes
            if row_idx == 1 and re.match(r'^-+:?-*$', cell.strip()):
                # Check for alignment markers
                if cell.startswith(':') and cell.endswith(':'):
                    formatted_cells.append(':' + '-' * (col_widths[i] - 2) + ':')
                elif cell.startswith(':'):
                    formatted_cells.append(':' + '-' * (col_widths[i] - 1))
                elif cell.endswith(':'):
                    formatted_cells.append('-' * (col_widths[i] - 1) + ':')
                else:
                    formatted_cells.append('-' * col_widths[i])
            else:
                # Regular cell: pad to col_width with 1 space on each side
                formatted_cells.append(' ' + cell.ljust(col_widths[i]) + ' ')
        
        result.append('|' + '|'.join(formatted_cells) + '|')
    
    return result

def fix_awesome_badge(content):
    """Ensure awesome badge is on the same line as main heading."""
    # Check if badge is already on heading line
    if re.match(r'^# .* \[!\[Awesome\]', content):
        return content
    
    # Find heading and badge
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('# ') and '[![Awesome]' in lines[i + 1] if i + 1 < len(lines) else False:
            # Move badge to heading line
            badge_line = lines[i + 1]
            lines[i] = lines[i] + ' ' + badge_line.strip()
            lines[i + 1] = ''
            break
    
    return '\n'.join(lines)

def fix_list_items(content):
    """Fix list item formatting."""
    lines = content.split('\n')
    result = []
    
    for line in lines:
        # Check for list items with links
        if re.match(r'^\s*[-*]\s*\[', line):
            # Ensure description ends with proper punctuation
            if not re.search(r'[.!?]\s*$', line):
                # Add period if missing
                line = line.rstrip() + '.'
        result.append(line)
    
    return '\n'.join(result)

if __name__ == '__main__':
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'README.md'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply fixes
    content = fix_awesome_badge(content)
    content = fix_table_alignment(content)
    content = fix_list_items(content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed {filepath}")
