
"""
Stealth scripts to bypass bot detection.
Comprehensive list derived from puppeteer-stealth techniques.
"""

STEALTH_SCRIPTS = [
    # 1. Override navigator.webdriver
    """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """,
    # 2. Mock Chrome object
    """
    if (!window.chrome) {
        window.chrome = {};
    }
    if (!window.chrome.runtime) {
        window.chrome.runtime = {};
    }
    """,
    # 3. Pass Permissions Check
    """
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    """,
    # 4. Plugins and MimeTypes
    """
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            var plugins = [];
            // Add a fake plugin
            var p = {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            };
            plugins.push(p);
            return plugins;
        }
    });
    Object.defineProperty(navigator, 'mimeTypes', {
        get: () => {
             var mimeTypes = [];
             var m = {
                 type: "application/x-google-chrome-pdf",
                 suffixes: "pdf",
                 description: "Portable Document Format",
                 enabledPlugin: {name: "Chrome PDF Plugin"}
             };
             mimeTypes.push(m);
             return mimeTypes;
        }
    });
    """,
    # 5. WebGL Vendor/Renderer (Masking Headless)
    """
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445) {
            return 'Intel Inc.';
        }
        // UNMASKED_RENDERER_WEBGL
        if (parameter === 37446) {
            return 'Intel Iris OpenGL Engine';
        }
        return getParameter(parameter);
    };
    """
]
