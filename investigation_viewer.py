#!/usr/bin/env python3
"""
Investigation Results Viewer
Serves generated analysis files with a web interface for easy browsing
"""

import os
import json
import mimetypes
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
import sys

# Configuration
INVESTIGATION_DIR = Path("/home/gene/Sparrow-SPOT-Policy/test_articles/Bill-C15/Investigation")
PORT = 8765

class InvestigationHandler(SimpleHTTPRequestHandler):
    """Custom handler for serving investigation files"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/files':
            self.serve_file_list()
        elif self.path.startswith('/api/file/'):
            self.serve_file_content()
        else:
            # Try to serve static file
            super().do_GET()
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = self.generate_dashboard()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_file_list(self):
        """Serve list of all files as JSON"""
        files_data = self.get_files_structure()
        json_response = json.dumps(files_data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-Length', len(json_response))
        self.end_headers()
        self.wfile.write(json_response.encode())
    
    def serve_file_content(self):
        """Serve actual file content"""
        # Extract file path from URL: /api/file/core/Bill-C15-00.json
        file_path_encoded = self.path.replace('/api/file/', '')
        file_path = INVESTIGATION_DIR / file_path_encoded
        
        # Security check - prevent path traversal
        try:
            file_path = file_path.resolve()
            if not str(file_path).startswith(str(INVESTIGATION_DIR.resolve())):
                self.send_error(403, "Access denied")
                return
        except:
            self.send_error(400, "Invalid path")
            return
        
        if not file_path.exists():
            self.send_error(404, "File not found")
            return
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            if file_path.suffix == '.json':
                content_type = 'application/json'
            elif file_path.suffix in ['.html', '.htm']:
                content_type = 'text/html'
            elif file_path.suffix in ['.md', '.txt', '.log']:
                content_type = 'text/plain'
            else:
                content_type = 'application/octet-stream'
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.send_header('Content-Length', len(content))
            self.send_header('Content-Disposition', f'inline; filename="{file_path.name}"')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, str(e))
    
    def get_files_structure(self):
        """Build directory structure with file metadata"""
        structure = {}
        
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
        
        for category, folder in categories.items():
            folder_path = INVESTIGATION_DIR / folder
            structure[category] = []
            
            if folder_path.exists():
                for file_path in sorted(folder_path.iterdir()):
                    if file_path.is_file():
                        stat = file_path.stat()
                        structure[category].append({
                            'name': file_path.name,
                            'path': f"{folder}/{file_path.name}",
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'type': file_path.suffix.lstrip('.')
                        })
        
        return structure
    
    def generate_dashboard(self):
        """Generate the main dashboard HTML"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bill C-15 Investigation Results Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            width: 100%;
            height: 100%;
            overflow: hidden;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            display: flex;
            flex-direction: column;
        }
        
        .container {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            padding: 5px;
            gap: 5px;
        }
        
        header {
            background: white;
            padding: 10px 15px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex-shrink: 0;
        }
        
        h1 {
            color: #333;
            margin-bottom: 2px;
            font-size: 1.5em;
        }
        
        .subtitle {
            color: #666;
            font-size: 0.85em;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            padding: 0 5px;
            flex-shrink: 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
            font-size: 0.75em;
        }
        
        .stat-value {
            font-size: 1.3em;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 0.7em;
            opacity: 0.9;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 5px;
            flex: 1;
            overflow: hidden;
            padding: 0 5px 5px 5px;
        }
        
        .sidebar {
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 200px);
        }
        
        #sidebarContainer {
            overflow-y: auto;
            flex: 1;
        }
        
        .search-box {
            padding: 8px;
            border-bottom: 1px solid #eee;
            flex-shrink: 0;
        }
        
        .search-box input {
            width: 100%;
            padding: 6px;
            border: 1px solid #ddd;
            border-radius: 3px;
            font-size: 0.85em;
        }
        
        .sidebar-section {
            border-bottom: 1px solid #eee;
        }
        
        .sidebar-header {
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
        }
        
        .sidebar-header:hover {
            background: #0052a3;
        }
        
        .file-list {
            padding: 0;
            display: none;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .file-list.active {
            display: block;
        }
        
        .file-item {
            padding: 8px 10px;
            cursor: pointer;
            border-left: 3px solid transparent;
            transition: all 0.2s;
            color: #333;
            font-size: 0.85em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        .file-item:hover {
            background: #e6f2ff;
            border-left-color: #0066cc;
            padding-left: 12px;
        }
        
        .file-item.active {
            background: #cce5ff;
            border-left-color: #0066cc;
            font-weight: 600;
            color: #0052a3;
        }
        
        .content-area {
            background: white;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            flex: 1;
        }
        
        #contentArea {
            display: flex;
            flex-direction: column;
            flex: 1;
            overflow: hidden;
            width: 100%;
            height: 100%;
        }
        
        .content-header {
            border-bottom: 1px solid #eee;
            padding: 10px 15px;
            flex-shrink: 0;
            min-height: 40px;
        }
        
        .content-header h2 {
            color: #333;
            font-size: 1.1em;
            margin-bottom: 3px;
        }
        
        .file-metadata {
            display: flex;
            gap: 12px;
            color: #666;
            font-size: 0.75em;
            flex-wrap: wrap;
        }
        
        .file-metadata span {
            display: flex;
            align-items: center;
            gap: 3px;
        }
        
        .content-body {
            flex: 1;
            overflow: auto;
            margin: 0;
            border: 0;
            background: #fafafa;
            position: relative;
        }
        
        .text-content, .json-content, .markdown-content {
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
        }
        
        .markdown-content {
            font-family: inherit;
        }
        
        .html-content {
            width: 100%;
            height: 100%;
        }
        
        .html-content iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        
        .action-buttons {
            display: flex;
            gap: 6px;
            padding: 8px 15px;
            border-top: 1px solid #eee;
            flex-shrink: 0;
            background: #fafafa;
        }
        
        button {
            padding: 6px 12px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #0066cc;
            color: white;
        }
        
        .btn-primary:hover {
            background: #0052a3;
        }
        
        .btn-secondary {
            background: #f0f0f0;
            color: #333;
            border: 1px solid #ddd;
        }
        
        .btn-secondary:hover {
            background: #e0e0e0;
        }
        
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            color: #999;
            font-size: 0.9em;
            width: 100%;
        }
        
        .empty-state svg {
            width: 60px;
            height: 60px;
            margin-bottom: 10px;
            opacity: 0.3;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 Bill C-15 Investigation Results</h1>
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
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:60px; height:60px; opacity:0.3;">
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
        let allFiles = {};
        let currentFile = null;

        async function init() {
            try {
                const response = await fetch('/api/files');
                allFiles = await response.json();
                buildSidebar();
                updateStats();
            } catch (error) {
                console.error('Error loading files:', error);
                document.getElementById('sidebarContainer').innerHTML = '<div style="padding: 20px; color: red;">Error loading files</div>';
            }
        }

        function buildSidebar() {
            const container = document.getElementById('sidebarContainer');
            container.innerHTML = '';

            for (const [category, files] of Object.entries(allFiles)) {
                const section = document.createElement('div');
                section.className = 'sidebar-section';

                const header = document.createElement('div');
                header.className = 'sidebar-header active';
                header.innerHTML = `<span>${category}</span> <span>▼</span>`;
                header.onclick = () => toggleSection(header);
                header.dataset.category = category;

                const fileList = document.createElement('div');
                fileList.className = 'file-list active';
                fileList.dataset.category = category;

                files.forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'file-item';
                    item.textContent = file.name;
                    item.dataset.path = file.path;
                    item.dataset.category = category;
                    item.onclick = () => loadFile(file);
                    fileList.appendChild(item);
                });

                section.appendChild(header);
                section.appendChild(fileList);
                container.appendChild(section);
            }
        }

        function toggleSection(header) {
            const fileList = header.nextElementSibling;
            const isActive = header.classList.toggle('active');
            fileList.classList.toggle('active', isActive);
            const span = header.querySelector('span:last-child');
            span.textContent = isActive ? '▼' : '▶';
        }

        function filterFiles() {
            const query = document.getElementById('searchBox').value.toLowerCase();
            const items = document.querySelectorAll('.file-item');
            
            items.forEach(item => {
                if (item.textContent.toLowerCase().includes(query)) {
                    item.style.display = '';
                    item.parentElement.classList.add('active');
                    item.parentElement.previousElementSibling.classList.add('active');
                } else {
                    item.style.display = 'none';
                }
            });
        }

        async function loadFile(file) {
            currentFile = file;
            
            // Update active item
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
            document.querySelector(`[data-path="${file.path}"]`).classList.add('active');

            const contentArea = document.getElementById('contentArea');
            contentArea.innerHTML = '<div class="loading">Loading file</div>';

            try {
                const response = await fetch(`/api/file/${file.path}`);
                const content = await response.text();
                displayContent(file, content);
            } catch (error) {
                contentArea.innerHTML = `<div class="empty-state" style="color: #e74c3c;">⚠️ Error loading file: ${error.message}</div>`;
            }
        }

        function displayContent(file, content) {
            const contentArea = document.getElementById('contentArea');
            const fileSize = new Blob([content]).size;
            const now = new Date().toLocaleString();

            let viewer = '';

            if (file.type === 'json') {
                try {
                    const formatted = JSON.stringify(JSON.parse(content), null, 2);
                    viewer = `<pre class="json-content">${escapeHtml(formatted)}</pre>`;
                } catch(e) {
                    viewer = `<pre class="text-content">${escapeHtml(content)}</pre>`;
                }
            } else if (file.type === 'html' || file.type === 'htm') {
                viewer = `<div class="html-content"><iframe srcdoc="${escapeHtml(content)}"></iframe></div>`;
            } else if (file.type === 'md') {
                viewer = `<div class="markdown-content">${markdownToHtml(content)}</div>`;
            } else {
                viewer = `<pre class="text-content">${escapeHtml(content)}</pre>`;
            }

            contentArea.innerHTML = `
                <div class="content-header">
                    <h2>${file.name}</h2>
                    <div class="file-metadata">
                        <span>📁 ${file.path}</span>
                        <span>📦 ${formatFileSize(fileSize)}</span>
                    </div>
                </div>
                <div class="content-body">
                    ${viewer}
                </div>
                <div class="action-buttons">
                    <button class="btn-primary" onclick="downloadFile()">⬇️ Download</button>
                    <button class="btn-secondary" onclick="copyContent()">📋 Copy</button>
                    <button class="btn-secondary" onclick="openInNewTab()">🔗 New Tab</button>
                </div>
            `;
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        function markdownToHtml(md) {
            let html = escapeHtml(md);
            html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
            html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
            html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
            html = html.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            html = html.replace(/_(.*?)_/g, '<em>$1</em>');
            html = html.replace(/\\n/g, '<br>');
            return `<div>${html}</div>`;
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
        }

        function downloadFile() {
            if (!currentFile) return;
            window.location.href = `/api/file/${currentFile.path}`;
        }

        function copyContent() {
            const content = document.querySelector('.text-content, .json-content, .markdown-content');
            if (content) {
                navigator.clipboard.writeText(content.textContent);
                alert('Content copied to clipboard!');
            }
        }

        function openInNewTab() {
            if (!currentFile) return;
            window.open(`/api/file/${currentFile.path}`, '_blank');
        }

        function updateStats() {
            let totalFiles = 0;
            let totalSize = 0;

            for (const files of Object.values(allFiles)) {
                totalFiles += files.length;
                totalSize += files.reduce((sum, f) => sum + f.size, 0);
            }

            const statsGrid = document.getElementById('statsGrid');
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${Object.keys(allFiles).length}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${totalFiles}</div>
                    <div class="stat-label">Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${formatFileSize(totalSize)}</div>
                    <div class="stat-label">Total Size</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">v8.6.1</div>
                    <div class="stat-label">Sparrow Version</div>
                </div>
            `;
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def main():
    """Start the investigation viewer server"""
    
    # Check if investigation directory exists
    if not INVESTIGATION_DIR.exists():
        print(f"❌ Investigation directory not found: {INVESTIGATION_DIR}")
        sys.exit(1)
    
    # Create and start server
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, InvestigationHandler)
    
    url = f"http://localhost:{PORT}"
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   📋 Bill C-15 Investigation Results Viewer               ║
║   Sparrow SPOT Scale™ v8.6.1                              ║
║                                                            ║
║   🌐 Opening: {url:<37} ║
║   📁 Serving: {str(INVESTIGATION_DIR)[-35:]:<37} ║
║                                                            ║
║   Press Ctrl+C to stop the server                         ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Open browser automatically
    try:
        webbrowser.open(url)
    except:
        print(f"⚠️  Could not open browser automatically. Visit: {url}")
    
    # Start server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped.")
        sys.exit(0)


if __name__ == '__main__':
    main()
