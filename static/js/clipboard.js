/**
 * =============================================================================
 * ACCESSIBLE MATH READER - CLIPBOARD MODULE
 * =============================================================================
 * 
 * @file clipboard.js
 * @description Browser-level clipboard integration with multi-format support
 *              for mathematical expressions.
 * 
 * @features
 * - Copy formula in multiple formats (LaTeX, MathML, plain text, accessible)
 * - Format selection dialog for user choice
 * - ARIA announcements for screen readers
 * - Fallback for browsers without Clipboard API
 * - Copy confirmation toast notifications
 * 
 * @author Accessible Math Reader Contributors
 * @version 0.2.0
 * @license MIT
 * =============================================================================
 */

// =============================================================================
// CLIPBOARD FORMAT DEFINITIONS
// =============================================================================

/**
 * @constant {Object} CLIPBOARD_FORMATS
 * @description Supported clipboard export formats with metadata
 */
const CLIPBOARD_FORMATS = {
    latex: {
        name: 'LaTeX',
        description: 'Original LaTeX source code',
        mimeType: 'text/plain',
        icon: '📝',
        accessibleName: 'LaTeX source code'
    },
    mathml: {
        name: 'MathML',
        description: 'Semantic MathML markup',
        mimeType: 'application/mathml+xml',
        icon: '🔣',
        accessibleName: 'MathML markup'
    },
    plainText: {
        name: 'Plain Text',
        description: 'Simple text representation',
        mimeType: 'text/plain',
        icon: '📄',
        accessibleName: 'Plain text representation'
    },
    accessible: {
        name: 'Accessible Text',
        description: 'Screen-reader optimized description',
        mimeType: 'text/plain',
        icon: '♿',
        accessibleName: 'Accessible text for screen readers'
    },
    braille: {
        name: 'Braille',
        description: 'Unicode Braille characters',
        mimeType: 'text/plain',
        icon: '⠿',
        accessibleName: 'Braille representation'
    }
};

// =============================================================================
// CLIPBOARD MANAGER CLASS
// =============================================================================

/**
 * @class ClipboardManager
 * @description Manages clipboard operations with format selection and 
 *              accessibility support.
 * 
 * @example
 * const clipboard = new ClipboardManager();
 * 
 * // Copy with specific format
 * clipboard.copy('\\frac{a}{b}', 'latex');
 * 
 * // Show format selection dialog
 * clipboard.showFormatDialog({
 *     latex: '\\frac{a}{b}',
 *     accessible: 'a divided by b',
 *     braille: '⠹⠁⠌⠃⠼'
 * });
 */
class ClipboardManager {
    /**
     * @constructor
     * @description Initialize the clipboard manager with default settings.
     */
    constructor() {
        /** @type {Object} Currently available content for each format */
        this.content = {};

        /** @type {HTMLElement|null} Reference to the format dialog */
        this.dialog = null;

        /** @type {HTMLElement|null} Reference to the toast container */
        this.toastContainer = null;

        // Initialize DOM elements
        this._initializeUI();
    }

    // =========================================================================
    // PUBLIC METHODS
    // =========================================================================

    /**
     * @method copy
     * @description Copy text to clipboard in the specified format.
     * 
     * @param {string} text - The text content to copy
     * @param {string} format - Format key from CLIPBOARD_FORMATS
     * @returns {Promise<boolean>} True if copy succeeded
     * 
     * @example
     * await clipboard.copy('x^2 + y^2 = z^2', 'latex');
     */
    async copy(text, format = 'plainText') {
        if (!text || typeof text !== 'string') {
            console.warn('[ClipboardManager] Invalid text provided');
            return false;
        }

        const formatInfo = CLIPBOARD_FORMATS[format] || CLIPBOARD_FORMATS.plainText;

        try {
            // Use modern Clipboard API if available
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
            } else {
                // Fallback for older browsers
                this._copyFallback(text);
            }

            // Show success feedback
            this._showToast(`Copied as ${formatInfo.name}`, 'success');
            this._announceToScreenReader(`${formatInfo.accessibleName} copied to clipboard`);

            return true;
        } catch (error) {
            console.error('[ClipboardManager] Copy failed:', error);
            this._showToast('Copy failed. Please try again.', 'error');
            this._announceToScreenReader('Failed to copy to clipboard');
            return false;
        }
    }

    /**
     * @method copyWithRichFormat
     * @description Copy content with multiple MIME types for rich paste support.
     *              Note: Rich clipboard requires secure context (HTTPS).
     * 
     * @param {Object} contentByFormat - Object mapping format keys to content
     * @returns {Promise<boolean>} True if copy succeeded
     * 
     * @example
     * await clipboard.copyWithRichFormat({
     *     latex: '\\frac{1}{2}',
     *     plainText: '1/2',
     *     accessible: 'one half'
     * });
     */
    async copyWithRichFormat(contentByFormat) {
        // For now, use plain text as the primary format
        // Rich clipboard (ClipboardItem) has limited browser support
        const primaryContent =
            contentByFormat.latex ||
            contentByFormat.plainText ||
            Object.values(contentByFormat)[0];

        return this.copy(primaryContent, 'latex');
    }

    /**
     * @method showFormatDialog
     * @description Display a dialog allowing the user to choose the copy format.
     * 
     * @param {Object} contentByFormat - Object mapping format keys to content
     * @param {Object} [options] - Dialog options
     * @param {string} [options.title='Copy Formula'] - Dialog title
     * 
     * @example
     * clipboard.showFormatDialog({
     *     latex: '\\frac{a}{b}',
     *     accessible: 'a divided by b',
     *     braille: '⠹⠁⠌⠃⠼'
     * });
     */
    showFormatDialog(contentByFormat, options = {}) {
        this.content = contentByFormat;

        const title = options.title || 'Copy Formula';
        const availableFormats = Object.keys(contentByFormat).filter(
            key => contentByFormat[key] && CLIPBOARD_FORMATS[key]
        );

        if (availableFormats.length === 0) {
            console.warn('[ClipboardManager] No valid formats provided');
            return;
        }

        // If only one format available, copy directly
        if (availableFormats.length === 1) {
            this.copy(contentByFormat[availableFormats[0]], availableFormats[0]);
            return;
        }

        // Create and show dialog
        this._createFormatDialog(title, availableFormats);
    }

    /**
     * @method setContent
     * @description Set content for a specific format without copying.
     * 
     * @param {string} format - Format key
     * @param {string} content - Content for that format
     */
    setContent(format, content) {
        this.content[format] = content;
    }

    /**
     * @method getAvailableFormats
     * @description Get list of formats with content available.
     * 
     * @returns {string[]} Array of format keys with content
     */
    getAvailableFormats() {
        return Object.keys(this.content).filter(key => this.content[key]);
    }

    // =========================================================================
    // PRIVATE METHODS - UI
    // =========================================================================

    /**
     * @private
     * @method _initializeUI
     * @description Initialize UI elements (toast container, dialog).
     */
    _initializeUI() {
        // Create toast container if not exists
        if (!document.getElementById('clipboard-toast-container')) {
            this.toastContainer = document.createElement('div');
            this.toastContainer.id = 'clipboard-toast-container';
            this.toastContainer.className = 'clipboard-toast-container';
            this.toastContainer.setAttribute('aria-live', 'polite');
            this.toastContainer.setAttribute('aria-atomic', 'true');
            document.body.appendChild(this.toastContainer);
        } else {
            this.toastContainer = document.getElementById('clipboard-toast-container');
        }
    }

    /**
     * @private
     * @method _createFormatDialog
     * @description Create and display the format selection dialog.
     * 
     * @param {string} title - Dialog title
     * @param {string[]} formats - Available format keys
     */
    _createFormatDialog(title, formats) {
        // Remove existing dialog if present
        const existingDialog = document.getElementById('clipboard-format-dialog');
        if (existingDialog) {
            existingDialog.remove();
        }

        // Create dialog element
        const dialog = document.createElement('dialog');
        dialog.id = 'clipboard-format-dialog';
        dialog.className = 'clipboard-dialog modal';
        dialog.setAttribute('aria-labelledby', 'clipboard-dialog-title');
        dialog.setAttribute('aria-describedby', 'clipboard-dialog-desc');

        // Build dialog content
        dialog.innerHTML = `
            <div class="modal__content clipboard-dialog__content">
                <h2 id="clipboard-dialog-title" class="clipboard-dialog__title">${this._escapeHtml(title)}</h2>
                <p id="clipboard-dialog-desc" class="clipboard-dialog__description">
                    Choose the format to copy the formula:
                </p>
                
                <div class="clipboard-format-list" role="listbox" aria-label="Copy formats">
                    ${formats.map((format, index) => this._createFormatButton(format, index === 0)).join('')}
                </div>
                
                <div class="clipboard-dialog__actions">
                    <button 
                        type="button" 
                        class="btn btn--secondary" 
                        id="clipboard-dialog-cancel"
                        aria-label="Cancel and close dialog"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(dialog);
        this.dialog = dialog;

        // Add event listeners
        this._attachDialogListeners(dialog, formats);

        // Show dialog
        dialog.showModal();

        // Focus first format button
        const firstButton = dialog.querySelector('.clipboard-format-btn');
        if (firstButton) {
            firstButton.focus();
        }
    }

    /**
     * @private
     * @method _createFormatButton
     * @description Generate HTML for a format selection button.
     * 
     * @param {string} format - Format key
     * @param {boolean} isFirst - Whether this is the first (default) option
     * @returns {string} HTML string
     */
    _createFormatButton(format, isFirst = false) {
        const info = CLIPBOARD_FORMATS[format];
        if (!info) return '';

        const content = this.content[format];
        const preview = this._truncate(content, 50);

        return `
            <button 
                type="button"
                class="clipboard-format-btn ${isFirst ? 'clipboard-format-btn--default' : ''}"
                data-format="${format}"
                role="option"
                aria-selected="${isFirst}"
                aria-label="Copy as ${info.accessibleName}"
            >
                <span class="clipboard-format-btn__icon" aria-hidden="true">${info.icon}</span>
                <span class="clipboard-format-btn__info">
                    <span class="clipboard-format-btn__name">${info.name}</span>
                    <span class="clipboard-format-btn__desc">${info.description}</span>
                </span>
                <span class="clipboard-format-btn__preview" title="${this._escapeHtml(content)}">
                    ${this._escapeHtml(preview)}
                </span>
            </button>
        `;
    }

    /**
     * @private
     * @method _attachDialogListeners
     * @description Attach event listeners to the dialog.
     * 
     * @param {HTMLDialogElement} dialog - The dialog element
     * @param {string[]} formats - Available format keys
     */
    _attachDialogListeners(dialog, formats) {
        // Format button clicks
        formats.forEach(format => {
            const btn = dialog.querySelector(`[data-format="${format}"]`);
            if (btn) {
                btn.addEventListener('click', () => {
                    this.copy(this.content[format], format);
                    dialog.close();
                });
            }
        });

        // Cancel button
        const cancelBtn = dialog.querySelector('#clipboard-dialog-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                dialog.close();
            });
        }

        // Escape key to close
        dialog.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dialog.close();
            }
        });

        // Clean up on close
        dialog.addEventListener('close', () => {
            dialog.remove();
            this.dialog = null;
        });

        // Keyboard navigation within format list
        const formatBtns = dialog.querySelectorAll('.clipboard-format-btn');
        formatBtns.forEach((btn, index) => {
            btn.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                    e.preventDefault();
                    const next = formatBtns[(index + 1) % formatBtns.length];
                    next.focus();
                } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prev = formatBtns[(index - 1 + formatBtns.length) % formatBtns.length];
                    prev.focus();
                }
            });
        });
    }

    /**
     * @private
     * @method _showToast
     * @description Display a toast notification.
     * 
     * @param {string} message - Message to display
     * @param {string} type - Toast type ('success', 'error', 'info')
     */
    _showToast(message, type = 'info') {
        if (!this.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `clipboard-toast clipboard-toast--${type}`;
        toast.setAttribute('role', 'status');

        const icon = type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ';

        toast.innerHTML = `
            <span class="clipboard-toast__icon" aria-hidden="true">${icon}</span>
            <span class="clipboard-toast__message">${this._escapeHtml(message)}</span>
        `;

        this.toastContainer.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.classList.add('clipboard-toast--visible');
        });

        // Remove after delay
        setTimeout(() => {
            toast.classList.remove('clipboard-toast--visible');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // =========================================================================
    // PRIVATE METHODS - UTILITIES
    // =========================================================================

    /**
     * @private
     * @method _copyFallback
     * @description Fallback copy method for browsers without Clipboard API.
     * 
     * @param {string} text - Text to copy
     */
    _copyFallback(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.cssText = 'position:fixed;left:-9999px;top:-9999px;';
        textarea.setAttribute('readonly', '');
        textarea.setAttribute('aria-hidden', 'true');

        document.body.appendChild(textarea);
        textarea.select();
        textarea.setSelectionRange(0, textarea.value.length);

        try {
            document.execCommand('copy');
        } finally {
            document.body.removeChild(textarea);
        }
    }

    /**
     * @private
     * @method _announceToScreenReader
     * @description Announce a message to screen readers via ARIA live region.
     * 
     * @param {string} message - Message to announce
     */
    _announceToScreenReader(message) {
        // Use existing announceToScreenReader function if available
        if (typeof announceToScreenReader === 'function') {
            announceToScreenReader(message);
            return;
        }

        // Fallback: create temporary live region
        const region = document.createElement('div');
        region.setAttribute('role', 'status');
        region.setAttribute('aria-live', 'assertive');
        region.setAttribute('aria-atomic', 'true');
        region.className = 'visually-hidden';
        region.textContent = message;

        document.body.appendChild(region);

        setTimeout(() => region.remove(), 1000);
    }

    /**
     * @private
     * @method _escapeHtml
     * @description Escape HTML special characters.
     * 
     * @param {string} str - String to escape
     * @returns {string} Escaped string
     */
    _escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * @private
     * @method _truncate
     * @description Truncate string to specified length.
     * 
     * @param {string} str - String to truncate
     * @param {number} maxLength - Maximum length
     * @returns {string} Truncated string
     */
    _truncate(str, maxLength) {
        if (!str) return '';
        if (str.length <= maxLength) return str;
        return str.substring(0, maxLength) + '...';
    }
}

// =============================================================================
// GLOBAL INSTANCE AND CONVENIENCE FUNCTIONS
// =============================================================================

/**
 * @global clipboardManager
 * @description Global ClipboardManager instance
 */
const clipboardManager = new ClipboardManager();

/**
 * @function copyFormula
 * @description Convenience function to copy formula with format selection.
 * 
 * @param {Object} content - Object with format keys and content values
 * 
 * @example
 * copyFormula({
 *     latex: '\\frac{1}{2}',
 *     accessible: 'one half',
 *     braille: '⠹⠂⠌⠆⠼'
 * });
 */
function copyFormula(content) {
    clipboardManager.showFormatDialog(content, {
        title: 'Copy Formula'
    });
}

/**
 * @function copyFormulaAs
 * @description Copy formula in a specific format without dialog.
 * 
 * @param {string} text - Text to copy
 * @param {string} format - Format key
 * @returns {Promise<boolean>} Copy success status
 * 
 * @example
 * await copyFormulaAs('\\frac{a}{b}', 'latex');
 */
async function copyFormulaAs(text, format) {
    return clipboardManager.copy(text, format);
}

/**
 * @function copyLatex
 * @description Quick copy as LaTeX format.
 * 
 * @param {string} latex - LaTeX string to copy
 * @returns {Promise<boolean>} Copy success status
 */
async function copyLatex(latex) {
    return clipboardManager.copy(latex, 'latex');
}

/**
 * @function copyAccessible
 * @description Quick copy as accessible text format.
 * 
 * @param {string} text - Accessible text to copy
 * @returns {Promise<boolean>} Copy success status
 */
async function copyAccessible(text) {
    return clipboardManager.copy(text, 'accessible');
}

/**
 * @function copyBraille
 * @description Quick copy as Braille format.
 * 
 * @param {string} braille - Braille string to copy
 * @returns {Promise<boolean>} Copy success status
 */
async function copyBraille(braille) {
    return clipboardManager.copy(braille, 'braille');
}

// =============================================================================
// CSS STYLES (Injected into document)
// =============================================================================

/**
 * @description Inject clipboard module styles into the document.
 *              Styles follow the existing app design system.
 */
(function injectClipboardStyles() {
    const styleId = 'clipboard-module-styles';

    // Don't inject twice
    if (document.getElementById(styleId)) return;

    const styles = document.createElement('style');
    styles.id = styleId;
    styles.textContent = `
        /* =====================================================================
           CLIPBOARD MODULE STYLES
           ===================================================================== */
        
        /* Toast Container */
        .clipboard-toast-container {
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            pointer-events: none;
        }
        
        /* Toast Notification */
        .clipboard-toast {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.875rem 1.25rem;
            background: var(--bg-elevated, #1e1e2e);
            color: var(--text-primary, #cdd6f4);
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            font-size: 0.9375rem;
            opacity: 0;
            transform: translateX(100%);
            transition: opacity 0.3s ease, transform 0.3s ease;
            pointer-events: auto;
        }
        
        .clipboard-toast--visible {
            opacity: 1;
            transform: translateX(0);
        }
        
        .clipboard-toast--success {
            border-left: 4px solid #a6e3a1;
        }
        
        .clipboard-toast--error {
            border-left: 4px solid #f38ba8;
        }
        
        .clipboard-toast--info {
            border-left: 4px solid #89b4fa;
        }
        
        .clipboard-toast__icon {
            font-size: 1.25rem;
        }
        
        .clipboard-toast--success .clipboard-toast__icon {
            color: #a6e3a1;
        }
        
        .clipboard-toast--error .clipboard-toast__icon {
            color: #f38ba8;
        }
        
        /* Format Selection Dialog */
        .clipboard-dialog {
            max-width: 500px;
            width: 90vw;
        }
        
        .clipboard-dialog__content {
            padding: 1.5rem;
        }
        
        .clipboard-dialog__title {
            margin: 0 0 0.5rem;
            font-size: 1.25rem;
            font-weight: 600;
        }
        
        .clipboard-dialog__description {
            margin: 0 0 1.25rem;
            color: var(--text-secondary, #a6adc8);
            font-size: 0.9375rem;
        }
        
        /* Format List */
        .clipboard-format-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-bottom: 1.25rem;
        }
        
        /* Format Button */
        .clipboard-format-btn {
            display: flex;
            align-items: center;
            gap: 1rem;
            width: 100%;
            padding: 0.875rem 1rem;
            background: var(--bg-secondary, #313244);
            border: 2px solid transparent;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
            transition: all 0.15s ease;
            color: var(--text-primary, #cdd6f4);
        }
        
        .clipboard-format-btn:hover,
        .clipboard-format-btn:focus {
            background: var(--bg-hover, #45475a);
            border-color: var(--accent-primary, #89b4fa);
            outline: none;
        }
        
        .clipboard-format-btn--default {
            border-color: var(--accent-secondary, #74c7ec);
        }
        
        .clipboard-format-btn__icon {
            font-size: 1.5rem;
            flex-shrink: 0;
            width: 2rem;
            text-align: center;
        }
        
        .clipboard-format-btn__info {
            flex: 1;
            min-width: 0;
        }
        
        .clipboard-format-btn__name {
            display: block;
            font-weight: 600;
            font-size: 0.9375rem;
        }
        
        .clipboard-format-btn__desc {
            display: block;
            font-size: 0.8125rem;
            color: var(--text-secondary, #a6adc8);
        }
        
        .clipboard-format-btn__preview {
            flex-shrink: 0;
            max-width: 120px;
            font-family: var(--font-mono, 'JetBrains Mono', monospace);
            font-size: 0.75rem;
            color: var(--text-muted, #6c7086);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        
        /* Dialog Actions */
        .clipboard-dialog__actions {
            display: flex;
            justify-content: flex-end;
            padding-top: 0.5rem;
            border-top: 1px solid var(--border-color, #45475a);
        }
        
        /* Light Theme Overrides */
        [data-theme="light"] .clipboard-toast {
            background: #eff1f5;
            color: #4c4f69;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        [data-theme="light"] .clipboard-format-btn {
            background: #e6e9ef;
            color: #4c4f69;
        }
        
        [data-theme="light"] .clipboard-format-btn:hover,
        [data-theme="light"] .clipboard-format-btn:focus {
            background: #dce0e8;
        }
    `;

    document.head.appendChild(styles);
})();

// =============================================================================
// EXPORTS (for module systems)
// =============================================================================

// Support both browser globals and module exports
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ClipboardManager,
        CLIPBOARD_FORMATS,
        clipboardManager,
        copyFormula,
        copyFormulaAs,
        copyLatex,
        copyAccessible,
        copyBraille
    };
}
