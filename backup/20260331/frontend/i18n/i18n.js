/**
 * Claw Advisor - i18n Internationalization Module
 * Supports: Chinese (zh) / English (en)
 */

class I18n {
  constructor() {
    this.currentLang = localStorage.getItem('claw-language') || 'zh';
    this.translations = {};
    this.isLoaded = false;
  }

  /**
   * Initialize i18n module
   */
  async init() {
    await this.loadLanguage(this.currentLang);
    this.applyTranslations();
    this.updateLanguageSwitcher();
    // Dispatch i18n-ready so pages waiting on this event can proceed
    document.dispatchEvent(new CustomEvent('i18n-ready', {
      detail: { lang: this.currentLang, translations: this.translations }
    }));
  }

  /**
   * Load language file
   */
  async loadLanguage(lang) {
    try {
      const response = await fetch(`/i18n/${lang}.json`);
      if (!response.ok) throw new Error(`Failed to load ${lang}`);
      this.translations = await response.json();
      this.currentLang = lang;
      this.isLoaded = true;
      localStorage.setItem('claw-language', lang);
      document.documentElement.lang = lang;
      return true;
    } catch (error) {
      console.error('i18n load error:', error);
      return false;
    }
  }

  /**
   * Get translation by key (supports nested keys like "nav.dashboard")
   */
  t(key, replacements = {}) {
    if (!this.isLoaded) return key;
    
    const keys = key.split('.');
    let value = this.translations;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return key; // Return key if translation not found
      }
    }
    
    if (typeof value !== 'string') return key;
    
    // Replace placeholders like {{name}}
    return value.replace(/\{\{(\w+)\}\}/g, (match, name) => {
      return replacements[name] !== undefined ? replacements[name] : match;
    });
  }

  /**
   * Switch to another language
   */
  async switchLanguage(lang) {
    if (lang === this.currentLang) return;
    
    const success = await this.loadLanguage(lang);
    if (success) {
      this.applyTranslations();
      this.updateLanguageSwitcher();
      // Trigger custom event for other components (dispatch on document, not window)
      document.dispatchEvent(new CustomEvent('languageChanged', { 
        detail: { lang, translations: this.translations } 
      }));
      document.dispatchEvent(new CustomEvent('language-changed', { 
        detail: { lang, translations: this.translations } 
      }));
    }
  }

  /**
   * Apply translations to all elements with data-i18n attribute
   */
  applyTranslations() {
    // Translate elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = this.t(key);
      if (text !== key) {
        el.innerHTML = text;
      }
    });

    // Translate placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const text = this.t(key);
      if (text !== key) {
        el.placeholder = text;
      }
    });

    // Translate titles
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      const text = this.t(key);
      if (text !== key) {
        el.title = text;
      }
    });

    // Update page title if data-i18n-page-title exists
    const pageTitleEl = document.querySelector('[data-i18n-page-title]');
    if (pageTitleEl) {
      const key = pageTitleEl.getAttribute('data-i18n-page-title');
      document.title = this.t(key);
    }
  }

  /**
   * Update language switcher UI
   */
  updateLanguageSwitcher() {
    const switchers = document.querySelectorAll('.lang-switcher');
    switchers.forEach(switcher => {
      const zhBtn = switcher.querySelector('[data-lang="zh"]');
      const enBtn = switcher.querySelector('[data-lang="en"]');
      
      if (zhBtn) {
        zhBtn.classList.toggle('active', this.currentLang === 'zh');
      }
      if (enBtn) {
        enBtn.classList.toggle('active', this.currentLang === 'en');
      }
    });
  }

  /**
   * Get current language
   */
  getCurrentLang() {
    return this.currentLang;
  }

  /**
   * Format number based on locale
   */
  formatNumber(num, options = {}) {
    const locale = this.currentLang === 'zh' ? 'zh-CN' : 'en-US';
    return new Intl.NumberFormat(locale, options).format(num);
  }

  /**
   * Format currency based on locale
   */
  formatCurrency(amount, currency = 'USD') {
    const locale = this.currentLang === 'zh' ? 'zh-CN' : 'en-US';
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency
    }).format(amount);
  }

  /**
   * Format date based on locale
   */
  formatDate(date, options = {}) {
    const locale = this.currentLang === 'zh' ? 'zh-CN' : 'en-US';
    const defaultOptions = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options }).format(new Date(date));
  }
}

// Create global instance
const i18n = new I18n();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => i18n.init());
} else {
  i18n.init();
}

// Expose to global scope for inline scripts
window.i18n = i18n;
window.t = (key, replacements) => i18n.t(key, replacements);
