/**
 * =============================================================================
 * ACCESSIBLE MATH READER - APP.JS
 * =============================================================================
 * Main JavaScript file for frontend interactivity.
 * 
 * Features:
 * - Theme toggle (dark/light mode)
 * - Sidebar collapse/expand
 * - Tab switching for output views
 * - Example expression insertion
 * - History management (localStorage)
 * - Keyboard shortcuts
 * - Menu interactions
 * 
 * Author: Accessible Math Reader Contributors
 * Version: 0.2.0
 * =============================================================================
 */

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Accessible Math Reader initialized');
    
    // Initialize theme from localStorage or default to dark
    initializeTheme();
    
    // Initialize sidebar state
    initializeSidebar();
    
    // Load history from localStorage
    loadHistory();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup form submission handler to save to history
    setupFormHandler();
    
    // Setup settings change handlers
    setupSettingsHandlers();
});

// =============================================================================
// THEME MANAGEMENT
// =============================================================================

/**
 * Initialize theme from localStorage or system preference
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('amr-theme');
    
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    } else {
        // Default to dark mode as per user preference
        document.documentElement.setAttribute('data-theme', 'dark');
    }
}

/**
 * Toggle between dark and light themes
 */
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('amr-theme', newTheme);
    
    // Announce theme change for screen readers
    announceToScreenReader(`Switched to ${newTheme} mode`);
}

/**
 * Toggle high contrast mode
 */
function toggleHighContrast() {
    const html = document.documentElement;
    html.classList.toggle('high-contrast');
    
    const isHighContrast = html.classList.contains('high-contrast');
    localStorage.setItem('amr-high-contrast', isHighContrast);
    
    announceToScreenReader(`High contrast mode ${isHighContrast ? 'enabled' : 'disabled'}`);
}

// =============================================================================
// SIDEBAR MANAGEMENT
// =============================================================================

/**
 * Initialize sidebar state from localStorage
 */
function initializeSidebar() {
    const savedState = localStorage.getItem('amr-sidebar-collapsed');
    const sidebar = document.getElementById('sidebar');
    
    if (savedState === 'true') {
        sidebar.classList.add('collapsed');
    }
}

/**
 * Toggle sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('collapsed');
    
    const isCollapsed = sidebar.classList.contains('collapsed');
    localStorage.setItem('amr-sidebar-collapsed', isCollapsed);
    
    announceToScreenReader(`Sidebar ${isCollapsed ? 'collapsed' : 'expanded'}`);
}

// =============================================================================
// TAB MANAGEMENT
// =============================================================================

/**
 * Switch to a specific output tab
 * @param {string} tabName - Name of the tab to switch to (formula, speech, braille, accessible)
 */
function switchTab(tabName) {
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        const isActive = tab.id === `tab-${tabName}`;
        tab.classList.toggle('tab--active', isActive);
        tab.setAttribute('aria-selected', isActive);
    });
    
    // Update tab panels
    const panels = document.querySelectorAll('.tab-panel');
    panels.forEach(panel => {
        const isActive = panel.id === `panel-${tabName}`;
        panel.classList.toggle('tab-panel--active', isActive);
        panel.hidden = !isActive;
    });
    
    // Announce tab change for screen readers
    announceToScreenReader(`${tabName} tab selected`);
}

// =============================================================================
// EXAMPLE EXPRESSIONS
// =============================================================================

/**
 * LaTeX examples covering various math features
 * Comprehensive example includes: fractions, exponents, integrals, summations, 
 * Greek letters, square roots, and subscripts
 */
const EXAMPLES = {
    // Comprehensive example covering most features
    comprehensive: String.raw`\int_0^\infty \sum_{n=1}^{N} \frac{\pi x^2}{\sqrt{a_n + b^3}} dx`,
    
    // Simple fraction
    fraction: String.raw`\frac{a + b}{c - d}`,
    
    // Quadratic formula
    quadratic: String.raw`x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}`,
    
    // Definite integral
    integral: String.raw`\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}`,
    
    // Summation series
    summation: String.raw`\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}`,
    
    // 2x2 Matrix
    matrix: String.raw`\begin{pmatrix} a & b \\ c & d \end{pmatrix}`
};

/**
 * Insert an example expression into the input textarea
 * @param {string} exampleName - Name of the example to insert
 */
function insertExample(exampleName) {
    const textarea = document.getElementById('math_input');
    const example = EXAMPLES[exampleName];
    
    if (example && textarea) {
        textarea.value = example;
        textarea.focus();
        
        announceToScreenReader(`Inserted ${exampleName} example`);
    }
}

// =============================================================================
// HISTORY MANAGEMENT
// =============================================================================

const MAX_HISTORY_ITEMS = 10;

/**
 * Load history from localStorage and display it
 */
function loadHistory() {
    const history = getHistory();
    displayHistory(history);
}

/**
 * Get history array from localStorage
 * @returns {Array} Array of history items
 */
function getHistory() {
    const saved = localStorage.getItem('amr-history');
    return saved ? JSON.parse(saved) : [];
}

/**
 * Save a new expression to history
 * @param {string} expression - LaTeX/MathML expression to save
 */
function saveToHistory(expression) {
    if (!expression || expression.trim() === '') return;
    
    let history = getHistory();
    
    // Remove duplicate if exists
    history = history.filter(item => item !== expression);
    
    // Add to beginning
    history.unshift(expression);
    
    // Limit to max items
    history = history.slice(0, MAX_HISTORY_ITEMS);
    
    // Save to localStorage
    localStorage.setItem('amr-history', JSON.stringify(history));
    
    // Update display
    displayHistory(history);
}

/**
 * Display history items in the sidebar
 * @param {Array} history - Array of history items
 */
function displayHistory(history) {
    const container = document.getElementById('historyList');
    if (!container) return;
    
    if (history.length === 0) {
        container.innerHTML = '<p class="history-empty">No recent expressions</p>';
        return;
    }
    
    container.innerHTML = history.map((expr, idx) => `
        <button 
            class="example-btn" 
            onclick="insertHistoryItem(${idx})"
            title="${escapeHtml(expr)}"
        >
            <span class="example-btn__preview">${truncate(expr, 25)}</span>
        </button>
    `).join('');
}

/**
 * Insert a history item into the input
 * @param {number} index - Index of the history item
 */
function insertHistoryItem(index) {
    const history = getHistory();
    if (history[index]) {
        const textarea = document.getElementById('math_input');
        textarea.value = history[index];
        textarea.focus();
    }
}

/**
 * Clear all history
 */
function clearHistory() {
    localStorage.removeItem('amr-history');
    displayHistory([]);
    announceToScreenReader('History cleared');
}

// =============================================================================
// FORM HANDLING
// =============================================================================

/**
 * Setup form submission handler
 */
function setupFormHandler() {
    const form = document.getElementById('convertForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            const textarea = document.getElementById('math_input');
            if (textarea && textarea.value.trim()) {
                saveToHistory(textarea.value.trim());
            }
        });
    }
}

/**
 * Clear the input textarea
 */
function clearInput() {
    const textarea = document.getElementById('math_input');
    if (textarea) {
        textarea.value = '';
        textarea.focus();
    }
}

// =============================================================================
// SETTINGS HANDLERS
// =============================================================================

/**
 * Setup event handlers for settings radio buttons
 */
function setupSettingsHandlers() {
    // Braille notation
    document.querySelectorAll('input[name="braille"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            setBrailleNotation(e.target.value);
        });
    });
    
    // Speech style
    document.querySelectorAll('input[name="speech"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            setSpeechStyle(e.target.value);
        });
    });
    
    // Navigation mode
    document.querySelectorAll('input[name="navmode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            setNavMode(e.target.value);
        });
    });
}

/**
 * Set braille notation preference
 * @param {string} notation - 'nemeth' or 'ueb'
 */
function setBrailleNotation(notation) {
    localStorage.setItem('amr-braille-notation', notation);
    announceToScreenReader(`Braille notation set to ${notation}`);
    // TODO: Send to backend when implementing preferences API
}

/**
 * Set speech style preference
 * @param {string} style - 'verbose', 'concise', or 'superbrief'
 */
function setSpeechStyle(style) {
    localStorage.setItem('amr-speech-style', style);
    announceToScreenReader(`Speech style set to ${style}`);
    // TODO: Send to backend when implementing preferences API
}

/**
 * Set navigation mode
 * @param {string} mode - 'browse', 'explore', or 'verbose'
 */
function setNavMode(mode) {
    localStorage.setItem('amr-nav-mode', mode);
    announceToScreenReader(`Navigation mode set to ${mode}`);
    // TODO: Send to backend when implementing preferences API
}

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

/**
 * Setup global keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl + Enter: Submit form
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            const form = document.getElementById('convertForm');
            if (form) form.submit();
        }
        
        // Ctrl + L: Clear input
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            clearInput();
        }
        
        // Ctrl + B: Toggle sidebar
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            toggleSidebar();
        }
        
        // Ctrl + Shift + T: Toggle theme
        if (e.ctrlKey && e.shiftKey && e.key === 'T') {
            e.preventDefault();
            toggleTheme();
        }
        
        // Alt + 1-4: Switch tabs
        if (e.altKey && e.key >= '1' && e.key <= '4') {
            e.preventDefault();
            const tabs = ['formula', 'speech', 'braille', 'accessible'];
            switchTab(tabs[parseInt(e.key) - 1]);
        }
    });
}

// =============================================================================
// ZOOM FUNCTIONS
// =============================================================================

let currentZoom = 100;

/**
 * Zoom in the page content
 */
function zoomIn() {
    currentZoom = Math.min(currentZoom + 10, 150);
    document.body.style.fontSize = `${currentZoom}%`;
    localStorage.setItem('amr-zoom', currentZoom);
    announceToScreenReader(`Zoom ${currentZoom}%`);
}

/**
 * Zoom out the page content
 */
function zoomOut() {
    currentZoom = Math.max(currentZoom - 10, 80);
    document.body.style.fontSize = `${currentZoom}%`;
    localStorage.setItem('amr-zoom', currentZoom);
    announceToScreenReader(`Zoom ${currentZoom}%`);
}

/**
 * Reset zoom to 100%
 */
function resetZoom() {
    currentZoom = 100;
    document.body.style.fontSize = '100%';
    localStorage.setItem('amr-zoom', currentZoom);
    announceToScreenReader('Zoom reset to 100%');
}

// =============================================================================
// DIALOG/MODAL FUNCTIONS
// =============================================================================

/**
 * Show keyboard shortcuts dialog
 */
function showShortcuts() {
    const dialog = document.getElementById('shortcutsDialog');
    if (dialog) dialog.showModal();
}

/**
 * Show about dialog
 */
function showAbout() {
    const dialog = document.getElementById('aboutDialog');
    if (dialog) dialog.showModal();
}

/**
 * Show user guide (placeholder)
 */
function showUserGuide() {
    alert('User Guide: Coming soon!');
}

/**
 * Close a modal dialog by ID
 * @param {string} dialogId - ID of the dialog to close
 */
function closeModal(dialogId) {
    const dialog = document.getElementById(dialogId);
    if (dialog) dialog.close();
}

// =============================================================================
// FILE OPERATIONS (Placeholders)
// =============================================================================

/**
 * Show file open dialog (placeholder)
 */
function showFileDialog() {
    alert('Open from File: Coming soon!');
}

/**
 * Save output to file (placeholder)
 */
function saveOutput() {
    const brailleText = document.querySelector('.braille-display')?.textContent;
    const speechText = document.querySelector('.transcript-box p')?.textContent;
    
    if (brailleText || speechText) {
        const content = `Speech: ${speechText || 'N/A'}\n\nBraille: ${brailleText || 'N/A'}`;
        downloadFile(content, 'math-output.txt', 'text/plain');
    } else {
        alert('No output to save. Convert an expression first.');
    }
}

/**
 * Export Braille as BRF file
 */
function exportBraille() {
    const brailleText = document.querySelector('.braille-display')?.textContent;
    
    if (brailleText) {
        downloadFile(brailleText, 'math-braille.brf', 'text/plain');
    } else {
        alert('No Braille output to export. Convert an expression first.');
    }
}

/**
 * Trigger file download
 * @param {string} content - File content
 * @param {string} filename - Name of the file
 * @param {string} mimeType - MIME type
 */
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// =============================================================================
// CLIPBOARD FUNCTIONS
// =============================================================================

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        announceToScreenReader('Copied to clipboard');
    } catch (err) {
        console.error('Failed to copy:', err);
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        announceToScreenReader('Copied to clipboard');
    }
}

// =============================================================================
// ACCESSIBILITY HELPERS
// =============================================================================

/**
 * Announce a message to screen readers via ARIA live region
 * @param {string} message - Message to announce
 */
function announceToScreenReader(message) {
    // Create or find the live region
    let liveRegion = document.getElementById('aria-live-region');
    
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'aria-live-region';
        liveRegion.setAttribute('role', 'status');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'visually-hidden';
        document.body.appendChild(liveRegion);
    }
    
    // Update the content to trigger announcement
    liveRegion.textContent = '';
    setTimeout(() => {
        liveRegion.textContent = message;
    }, 100);
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Escape HTML special characters
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Truncate string to specified length
 * @param {string} str - String to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated string
 */
function truncate(str, maxLength) {
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

// =============================================================================
// CLOSE DROPDOWN MENUS ON OUTSIDE CLICK
// =============================================================================

document.addEventListener('click', (e) => {
    // Close dropdowns when clicking outside
    if (!e.target.closest('.menu-item')) {
        document.querySelectorAll('.menu-item__trigger').forEach(trigger => {
            trigger.setAttribute('aria-expanded', 'false');
        });
    }
});
