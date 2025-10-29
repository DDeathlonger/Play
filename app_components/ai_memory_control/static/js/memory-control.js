// AI Memory Control Panel - JavaScript Functionality
class MemoryControlPanel {
    constructor() {
        this.currentFile = null;
        this.fileContent = '';
        this.isConnected = false;
        this.apiBase = 'http://localhost:8765';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadFileTree();
        this.checkConnection();
        this.showWelcomeMessage();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        // File tree interaction
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('file-item')) {
                this.loadFile(e.target.dataset.file);
            }
        });

        // Search functionality
        document.getElementById('file-search').addEventListener('input', (e) => {
            this.filterFiles(e.target.value);
        });

        // Editor functionality
        document.getElementById('save-btn').addEventListener('click', () => this.saveFile());
        document.getElementById('preview-btn').addEventListener('click', () => this.togglePreview());
        document.getElementById('emoji-btn').addEventListener('click', () => this.toggleEmojiPicker());

        // Markdown editor
        document.getElementById('markdown-editor').addEventListener('input', (e) => {
            this.fileContent = e.target.value;
            this.updatePreview();
        });

        // Emoji picker
        document.querySelectorAll('.emoji-option').forEach(emoji => {
            emoji.addEventListener('click', (e) => {
                this.insertEmoji(e.target.dataset.emoji);
            });
        });

        // Refresh actions
        document.getElementById('refresh-btn').addEventListener('click', () => this.loadFileTree());
        document.getElementById('new-file-btn').addEventListener('click', () => this.createNewFile());

        // Graph controls
        document.getElementById('layout-select').addEventListener('change', (e) => {
            this.updateGraphLayout(e.target.value);
        });
        document.getElementById('refresh-graph-btn').addEventListener('click', () => this.refreshGraph());
    }

    async checkConnection() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            if (response.ok) {
                this.isConnected = true;
                this.updateConnectionStatus('Connected - MCP Server Active', 'connected');
            } else {
                throw new Error('Server not responding');
            }
        } catch (error) {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected - MCP Server Offline', '');
        }
    }

    updateConnectionStatus(message, className) {
        const statusEl = document.getElementById('connection-status');
        statusEl.textContent = message;
        statusEl.className = `status-indicator ${className}`;
    }

    async loadFileTree() {
        try {
            // Simulate API call - replace with actual MCP endpoint
            const files = await this.fetchFiles();
            this.renderFileTree(files);
        } catch (error) {
            console.error('Failed to load file tree:', error);
            this.showError('Failed to load files from memory system');
        }
    }

    async fetchFiles() {
        // Mock data - replace with actual API call
        return {
            'protocols': [
                'AI_DEVELOPMENT_CYCLE_MANDATORY.md',
                'MANDATORY_VISUAL_VALIDATION.md',
                'AI_UI_INTEGRATION_COMPLETE.md',
                'MEMORY_RETENTION_PROTOCOLS.md'
            ],
            'context': [
                'CODEBASE_CLEANUP_COMPLETE.md',
                'development_patterns.md',
                'UNIFIED_NAMING_CONVENTIONS.md'
            ],
            'guides': [
                'VSCODE_GUIDE.md',
                'UI_TESTING_GUIDE.md',
                'PYTEST_TESTING_SYSTEM.md'
            ],
            'reference': [
                'TECHNICAL_REFERENCE.md',
                'CONSOLIDATED_WORKING_SYSTEMS_ONLY.md',
                'AI_DOCUMENTATION_INDEX.md'
            ]
        };
    }

    renderFileTree(files) {
        const treeContainer = document.querySelector('.file-tree');
        treeContainer.innerHTML = '';

        Object.entries(files).forEach(([category, fileList]) => {
            const categoryEl = document.createElement('div');
            categoryEl.className = 'file-category';

            const titleEl = document.createElement('h3');
            titleEl.textContent = category.toUpperCase();
            categoryEl.appendChild(titleEl);

            fileList.forEach(filename => {
                const fileEl = document.createElement('div');
                fileEl.className = 'file-item';
                fileEl.dataset.file = `${category}/${filename}`;
                fileEl.innerHTML = `
                    <span class="file-name">${filename}</span>
                    <span class="file-size">${Math.floor(Math.random() * 50 + 10)}KB</span>
                `;
                categoryEl.appendChild(fileEl);
            });

            treeContainer.appendChild(categoryEl);
        });
    }

    filterFiles(query) {
        const fileItems = document.querySelectorAll('.file-item');
        fileItems.forEach(item => {
            const filename = item.querySelector('.file-name').textContent;
            const matches = filename.toLowerCase().includes(query.toLowerCase());
            item.style.display = matches ? 'flex' : 'none';
        });
    }

    async loadFile(filepath) {
        try {
            // Clear previous selection
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('active');
            });

            // Mark current selection
            document.querySelector(`[data-file="${filepath}"]`).classList.add('active');

            this.currentFile = filepath;

            // Mock file content - replace with actual API call
            const content = await this.fetchFileContent(filepath);
            this.fileContent = content;

            this.updateFileHeader(filepath);
            this.updateMarkdownContent(content);
            this.updateEditor(content);

            // Switch to viewer tab
            this.switchTab('viewer');

        } catch (error) {
            console.error('Failed to load file:', error);
            this.showError(`Failed to load ${filepath}`);
        }
    }

    async fetchFileContent(filepath) {
        // Mock content - replace with actual API call
        const mockContent = `# ${filepath.split('/').pop()}

## Overview
This is a mock content for demonstration purposes.

### Key Features
- Feature 1: Important functionality
- Feature 2: Additional capabilities
- Feature 3: Extended features

### Technical Details
\`\`\`python
def example_function():
    return "This is example code"
\`\`\`

### References
- Related file 1
- Related file 2
- External documentation

---
*Last updated: ${new Date().toLocaleDateString()}*
`;
        return mockContent;
    }

    updateFileHeader(filepath) {
        const filename = filepath.split('/').pop();
        const category = filepath.split('/')[0];

        document.getElementById('file-title').textContent = filename;
        document.getElementById('file-path').textContent = filepath;
        document.getElementById('file-category').textContent = category;
        document.getElementById('file-modified').textContent = new Date().toLocaleString();
    }

    updateMarkdownContent(content) {
        // Simple markdown-to-HTML conversion (basic)
        const htmlContent = content
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>')
            .replace(/\`(.*?)\`/gim, '<code>$1</code>')
            .replace(/\n\n/gim, '</p><p>')
            .replace(/^(.*)$/gim, '<p>$1</p>');

        document.getElementById('markdown-content').innerHTML = htmlContent;
    }

    updateEditor(content) {
        document.getElementById('markdown-editor').value = content;
        this.updatePreview();
    }

    updatePreview() {
        // Update preview pane with current editor content
        if (document.querySelector('.preview-pane')) {
            this.updateMarkdownContent(this.fileContent);
        }
    }

    switchTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
        });

        // Show selected tab content and mark tab as active
        document.getElementById(`${tabName}-tab`).classList.add('active');
        document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
    }

    showWelcomeMessage() {
        document.getElementById('markdown-content').innerHTML = `
            <div class="welcome-message">
                <h3>🤖 AI Memory Control Panel</h3>
                <p>Welcome to the AI Memory System management interface.</p>
                <p>Select a file from the sidebar to view or edit documentation.</p>
                <p>Use <code>Ctrl+S</code> to save changes and <code>Ctrl+P</code> to toggle preview.</p>
            </div>
        `;
    }

    async saveFile() {
        if (!this.currentFile || !this.fileContent) {
            this.showError('No file selected or content empty');
            return;
        }

        try {
            // Mock save - replace with actual API call
            await this.saveFileContent(this.currentFile, this.fileContent);
            this.showSuccess(`Saved ${this.currentFile}`);

            // Update UI
            document.getElementById('save-btn').disabled = true;
            setTimeout(() => {
                document.getElementById('save-btn').disabled = false;
            }, 2000);

        } catch (error) {
            console.error('Failed to save file:', error);
            this.showError(`Failed to save ${this.currentFile}`);
        }
    }

    async saveFileContent(filepath, content) {
        // Mock API call - replace with actual implementation
        return new Promise(resolve => setTimeout(resolve, 500));
    }

    togglePreview() {
        const previewPane = document.querySelector('.preview-pane');
        if (previewPane.style.display === 'none') {
            previewPane.style.display = 'flex';
            this.updatePreview();
        } else {
            previewPane.style.display = 'none';
        }
    }

    toggleEmojiPicker() {
        const picker = document.querySelector('.emoji-picker');
        picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
    }

    insertEmoji(emoji) {
        const editor = document.getElementById('markdown-editor');
        const cursorPos = editor.selectionStart;
        const textBefore = editor.value.substring(0, cursorPos);
        const textAfter = editor.value.substring(cursorPos);

        editor.value = textBefore + emoji + ' ' + textAfter;
        editor.selectionStart = editor.selectionEnd = cursorPos + emoji.length + 1;

        this.fileContent = editor.value;
        this.updatePreview();
        this.toggleEmojiPicker();
    }

    createNewFile() {
        const filename = prompt('Enter filename (with .md extension):');
        if (filename) {
            this.currentFile = `context/${filename}`;
            this.fileContent = `# ${filename.replace('.md', '')}\n\n## Overview\n\nNew documentation file.\n`;
            this.updateEditor(this.fileContent);
            this.switchTab('editor');
        }
    }

    updateGraphLayout(layout) {
        console.log(`Updating graph layout to: ${layout}`);
        // Implement graph visualization update
    }

    refreshGraph() {
        console.log('Refreshing cross-reference graph');
        // Implement graph refresh
    }

    showError(message) {
        console.error(message);
        // Could implement toast notifications here
    }

    showSuccess(message) {
        console.log(message);
        // Could implement toast notifications here
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.memoryPanel = new MemoryControlPanel();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        window.memoryPanel.saveFile();
    }

    if (e.ctrlKey && e.key === 'p') {
        e.preventDefault();
        window.memoryPanel.togglePreview();
    }
});