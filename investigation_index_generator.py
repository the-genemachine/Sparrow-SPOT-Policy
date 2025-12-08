#!/usr/bin/env python3
"""
Investigation Index Generator
Creates an interactive index.html file for browsing investigation results
"""

import json
from pathlib import Path
from datetime import datetime


def generate_investigation_index(output_dir, document_name=None):
    """
    Generate an index.html file for the investigation results
    
    Args:
        output_dir: Path to the investigation output directory (parent of subdirectories)
        document_name: Name of the document being analyzed
    
    Returns:
        Path to the generated index.html file
    """
    
    output_dir = Path(output_dir)
    
    if not output_dir.exists():
        raise ValueError(f"Output directory does not exist: {output_dir}")
    
    # Get document info
    if not document_name:
        document_name = output_dir.name
    
    # Build file structure
    categories = {
        'Core Analysis': 'core',
        'Certificates': 'certificates',
        'Reports': 'reports',
        'Threats & DPA': 'threats',
        'Transparency': 'transparency',
        'Narratives': 'narrative',
        'Q&A': 'qa',
        'Logs': 'logs'
    }
    
    files_data = {}
    total_files = 0
    total_size = 0
    
    for category, folder in categories.items():
        folder_path = output_dir / folder
        files_data[category] = []
        
        if folder_path.exists():
            for file_path in sorted(folder_path.iterdir()):
                if file_path.is_file():
                    stat = file_path.stat()
                    files_data[category].append({
                        'name': file_path.name,
                        'path': f"{folder}/{file_path.name}",
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': file_path.suffix.lstrip('.')
                    })
                    total_files += 1
                    total_size += stat.st_size
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document_name} - Investigation Results Viewer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
        }}
        
        .container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            padding: 5px;
            gap: 5px;
        }}
        
        header {{
            background: white;
            padding: 10px 15px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex-shrink: 0;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 2px;
            font-size: 1.5em;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 0.85em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            padding: 0 5px;
            flex-shrink: 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            font-size: 0.75em;
        }}
        
        .stat-value {{
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.7em;
            opacity: 0.9;
        }}
        
        .main-grid {{
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 5px;
            flex: 1;
            overflow: hidden;
            padding: 0 5px 5px 5px;
        }}
        
        .sidebar {{
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 200px);
        }}
        
        #sidebarContainer {{
            overflow-y: auto;
            flex: 1;
        }}
        
        .search-box {{
            padding: 8px;
            border-bottom: 1px solid #eee;
            flex-shrink: 0;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-size: 0.85em;
        }}
        
        .sidebar-section {{
            border-bottom: 1px solid #eee;
        }}
        
        .sidebar-header {{
            background: #0066cc;
            color: white;
            padding: 10px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
            font-size: 0.9em;
        }}
        
        .sidebar-header:hover {{
            background: #0052a3;
        }}
        
        .file-list {{
            padding: 0;
            display: none;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .file-list.active {{
            display: block;
        }}
        
        .file-item {{
            padding: 8px 10px;
            cursor: pointer;
            border-left: 3px solid transparent;
            transition: all 0.2s;
            color: #333;
            font-size: 0.85em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .file-item:hover {{
            background: #e6f2ff;
            border-left-color: #0066cc;
            padding-left: 12px;
        }}
        
        .file-item.active {{
            background: #cce5ff;
            border-left-color: #0066cc;
            font-weight: 600;
            color: #0052a3;
        }}
        
        .content-area {{
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            flex: 1;
        }}
        
        #contentArea {{
            display: flex;
            flex-direction: column;
            flex: 1;
            overflow: hidden;
            width: 100%;
            height: 100%;
        }}
        
        .content-header {{
            border-bottom: 1px solid #eee;
            padding: 10px 15px;
            flex-shrink: 0;
            min-height: 40px;
        }}
        
        .content-header h2 {{
            color: #333;
            font-size: 1.1em;
            margin-bottom: 3px;
        }}
        
        .file-metadata {{
            display: flex;
            gap: 12px;
            color: #666;
            font-size: 0.75em;
            flex-wrap: wrap;
        }}
        
        .file-metadata span {{
            display: flex;
            align-items: center;
            gap: 3px;
        }}
        
        .content-body {{
            flex: 1;
            overflow: auto;
            margin: 0;
            border: 0;
            background: #fafafa;
            position: relative;
        }}
        
        .text-content, .json-content, .markdown-content {{
            padding: 10px;
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #333;
            font-size: 0.8em;
            line-height: 1.5;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            height: auto;
            min-height: 100%;
        }}
        
        .markdown-content {{
            font-family: inherit;
        }}
        
        .html-content {{
            width: 100%;
            height: 100%;
        }}
        
        .html-content iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 6px;
            padding: 8px 15px;
            border-top: 1px solid #eee;
            flex-shrink: 0;
            background: #fafafa;
        }}
        
        button {{
            padding: 6px 12px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: #0066cc;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #0052a3;
        }}
        
        .btn-secondary {{
            background: #f0f0f0;
            color: #333;
            border: 1px solid #ddd;
        }}
        
        .btn-secondary:hover {{
            background: #e0e0e0;
        }}
        
        .empty-state {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            color: #999;
            font-size: 0.9em;
            width: 100%;
        }}
        
        .empty-state svg {{
            width: 60px;
            height: 60px;
            margin-bottom: 10px;
            opacity: 0.3;
        }}
        
        .loading {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 {document_name} Investigation Results</h1>
            <p class="subtitle">Sparrow SPOT Scale™ v8.6.1 Analysis Viewer</p>
        </header>
        
        <div class="stats-grid" id="statsGrid"></div>
        
        <div class="main-grid">
            <div class="sidebar">
                <div class="search-box">
                    <input type="text" id="searchBox" placeholder="Search files..." onkeyup="filterFiles()">
                </div>
                <div id="sidebarContainer"></div>
            </div>
            
            <div class="content-area">
                <div id="contentArea">
                    <div class="empty-state">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                            <polyline points="13 2 13 9 20 9"></polyline>
                        </svg>
                        <p>Select a file from the sidebar to view results</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const filesData = {json.dumps(files_data)};
        let currentFile = null;

        function init() {{
            buildSidebar();
            updateStats();
        }}

        function buildSidebar() {{
            const container = document.getElementById('sidebarContainer');
            container.innerHTML = '';

            for (const [category, files] of Object.entries(filesData)) {{
                const section = document.createElement('div');
                section.className = 'sidebar-section';

                const header = document.createElement('div');
                header.className = 'sidebar-header active';
                header.innerHTML = `<span>${{category}}</span> <span>▼</span>`;
                header.onclick = () => toggleSection(header);

                const fileList = document.createElement('div');
                fileList.className = 'file-list active';

                files.forEach(file => {{
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.textContent = file.name;
                    item.dataset.path = file.path;
                    item.onclick = () => loadFile(file);
                    fileList.appendChild(item);
                }});

                section.appendChild(header);
                section.appendChild(fileList);
                container.appendChild(section);
            }}
        }}

        function toggleSection(header) {{
            const fileList = header.nextElementSibling;
            const isActive = header.classList.toggle('active');
            fileList.classList.toggle('active', isActive);
            const span = header.querySelector('span:last-child');
            span.textContent = isActive ? '▼' : '▶';
        }}

        function filterFiles() {{
            const query = document.getElementById('searchBox').value.toLowerCase();
            const items = document.querySelectorAll('.file-item');
            
            items.forEach(item => {{
                if (item.textContent.toLowerCase().includes(query)) {{
                    item.style.display = '';
                    item.parentElement.classList.add('active');
                    item.parentElement.previousElementSibling.classList.add('active');
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        async function loadFile(file) {{
            currentFile = file;
            
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`[data-path="${{file.path}}"]`).classList.add('active');

            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = '<div class="loading">Loading file</div>';

            try {{
                const response = await fetch(file.path);
                const content = await response.text();
                displayContent(file, content);
            }} catch (error) {{
                contentArea.innerHTML = `<div class="empty-state" style="color: #e74c3c;">⚠️ Error loading file: ${{error.message}}</div>`;
            }}
        }}

        function displayContent(file, content) {{
            const contentArea = document.getElementById('contentArea');
            const fileSize = new Blob([content]).size;

            let viewer = '';

            if (file.type === 'json') {{
                try {{
                    const formatted = JSON.stringify(JSON.parse(content), null, 2);
                    viewer = `<pre class="json-content">${{escapeHtml(formatted)}}</pre>`;
                }} catch(e) {{
                    viewer = `<pre class="text-content">${{escapeHtml(content)}}</pre>`;
                }}
            }} else if (file.type === 'html' || file.type === 'htm') {{
                viewer = `<div class="html-content"><iframe srcdoc="${{escapeHtml(content)}}"></iframe></div>`;
            }} else if (file.type === 'md') {{
                viewer = `<div class="markdown-content">${{markdownToHtml(content)}}</div>`;
            }} else {{
                viewer = `<pre class="text-content">${{escapeHtml(content)}}</pre>`;
            }}

            contentArea.innerHTML = `
                <div class="content-header">
                    <h2>${{file.name}}</h2>
                    <div class="file-metadata">
                        <span>📁 ${{file.path}}</span>
                        <span>📦 ${{formatFileSize(fileSize)}}</span>
                    </div>
                </div>
                <div class="content-body">
                    ${{viewer}}
                </div>
                <div class="action-buttons">
                    <button class="btn-primary" onclick="downloadFile()">⬇️ Download</button>
                    <button class="btn-secondary" onclick="copyContent()">📋 Copy</button>
                    <button class="btn-secondary" onclick="openInNewTab()">🔗 New Tab</button>
                </div>
            `;
        }}

        function escapeHtml(text) {{
            const map = {{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'}};
            return text.replace(/[&<>"']/g, m => map[m]);
        }}

        function markdownToHtml(md) {{
            let html = escapeHtml(md);
            html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
            html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            html = html.replace(/_(.*?)_/g, '<em>$1</em>');
            html = html.replace(/\\n/g, '<br>');
            return `<div style="line-height: 1.8; color: #333;">${{html}}</div>`;
        }}

        function formatFileSize(bytes) {{
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
        }}

        function downloadFile() {{
            if (!currentFile) return;
            const link = document.createElement('a');
            link.href = currentFile.path;
            link.download = currentFile.name;
            link.click();
        }}

        function copyContent() {{
            const content = document.querySelector('.text-content, .json-content, .markdown-content');
            if (content) {{
                navigator.clipboard.writeText(content.textContent);
                alert('Content copied to clipboard!');
            }}
        }}

        function openInNewTab() {{
            if (!currentFile) return;
            window.open(currentFile.path, '_blank');
        }}

        function updateStats() {{
            let totalCategories = Object.keys(filesData).length;
            let totalFiles = {total_files};
            let totalSize = {total_size};

            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${{totalCategories}}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{totalFiles}}</div>
                    <div class="stat-label">Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{formatFileSize(totalSize)}}</div>
                    <div class="stat-label">Total Size</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">v8.6.1</div>
                    <div class="stat-label">Sparrow Version</div>
                </div>
            `;
        }}

        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""
    
    # Write index.html to parent directory
    index_path = output_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return index_path
