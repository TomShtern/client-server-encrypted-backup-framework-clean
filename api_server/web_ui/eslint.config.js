/**
 * ESLint flat config for the web UI (classic browser scripts + node helpers).
 * Non-JS assets are ignored to prevent the VS Code ESLint plugin from
 * complaining about missing configs when editing HTML/CSS/markdown.
 */

const browserGlobals = {
  // Standard browser globals used across the UI
  window: "readonly",
  document: "readonly",
  navigator: "readonly",
  console: "readonly",
  localStorage: "readonly",
  sessionStorage: "readonly",
  URL: "readonly",
  URLSearchParams: "readonly",
  fetch: "readonly",
  Request: "readonly",
  Response: "readonly",
  Headers: "readonly",
  FormData: "readonly",
  Blob: "readonly",
  File: "readonly",
  WebSocket: "readonly",
  Event: "readonly",
  MutationObserver: "readonly",
  Notification: "readonly",
  performance: "readonly",
  getComputedStyle: "readonly",
  setTimeout: "readonly",
  clearTimeout: "readonly",
  setInterval: "readonly",
  clearInterval: "readonly",
  requestAnimationFrame: "readonly",
  cancelAnimationFrame: "readonly",
  queueMicrotask: "readonly",

  // Project-level globals shared across classic scripts
  dom: "writable",
  domUtils: "readonly",
  formatters: "readonly",
  StateStore: "readonly",
  ToastManager: "readonly",
  ScreenReaderAnnouncer: "readonly",
  ApiClient: "readonly",
  ConnectionMonitor: "readonly",
  SocketClient: "readonly",
  AdvancedSettings: "readonly",
  FileManager: "readonly",
  ThemeManager: "readonly",
  LogStore: "readonly",
  ErrorBoundary: "readonly",
  API_CONFIG: "readonly",
  TimerManager: "readonly",
  CONSTANTS: "readonly",
  FILE_VALIDATION: "readonly",
  ProfessionalGUIEnhancements: "readonly",
};

const nodeGlobals = {
  module: "readonly",
  __dirname: "readonly",
  require: "readonly",
  process: "readonly",
};

export default [
  {
    ignores: [
      "node_modules/**",
      "dist/**",
      "build/**",
      "coverage/**",
      "**/*.css",
      "**/*.html",
      "**/*.md",
      "assets/**",
      "logs/**",
      "eslint.config.js",
    ],
  },
  {
    files: ["js/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: browserGlobals,
    },
    rules: {
      "no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "no-undef": "warn",
      "no-console": "off",
      "prefer-const": "warn",
    },
  },
  {
    files: ["scripts/**/*.js"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "script",
      globals: nodeGlobals,
    },
    rules: {
      "no-console": "off",
    },
  },
];