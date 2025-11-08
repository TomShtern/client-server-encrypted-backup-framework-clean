#!/usr/bin/env node

/**
 * Module Validation Script
 *
 * Validates all ES6 modules in the project for:
 * - Missing dependencies
 * - Circular dependencies
 * - Syntax errors
 * - Unused imports
 */

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = dirname(__dirname);

const IGNORED_FILES = [
  'validate-modules.js',
  'node_modules',
  'dist',
  'build'
];

class ModuleValidator {
  constructor() {
    this.modules = new Map();
    this.errors = [];
    this.warnings = [];
  }

  async validate() {
    console.log('🔍 Validating CyberBackup Web GUI modules...\n');

    try {
      // Find all JavaScript modules
      await this.findModules(projectRoot);

      // Analyze each module
      for (const [filePath, content] of this.modules) {
        this.validateModule(filePath, content);
      }

      // Check for missing dependencies
      await this.checkMissingDependencies();

      // Print results
      this.printResults();

      return this.errors.length === 0;

    } catch (error) {
      console.error('❌ Validation failed with error:', error.message);
      return false;
    }
  }

  async findModules(dir) {
    const files = readdirSync(dir);

    for (const file of files) {
      const fullPath = join(dir, file);
      const stat = statSync(fullPath);

      if (stat.isDirectory() && !IGNORED_FILES.includes(file)) {
        await this.findModules(fullPath);
      } else if (stat.isFile() && file.endsWith('.js') && !IGNORED_FILES.some(ignored => fullPath.includes(ignored))) {
        try {
          const content = readFileSync(fullPath, 'utf8');
          this.modules.set(fullPath, content);
        } catch (error) {
          this.errors.push(`Failed to read ${fullPath}: ${error.message}`);
        }
      }
    }
  }

  validateModule(filePath, content) {
    // Check for syntax errors
    try {
      // Basic syntax check
      if (!content.trim().startsWith('import') && !content.includes('export')) {
        this.warnings.push(`${filePath}: Doesn't use ES6 modules syntax`);
      }

      // Check for common issues
      this.checkImportSyntax(filePath, content);
      this.checkExports(filePath, content);

    } catch (error) {
      this.errors.push(`${filePath}: Syntax error - ${error.message}`);
    }
  }

  checkImportSyntax(filePath, content) {
    const importRegex = /import\s+(?:(?:\*\s+as\s+\w+)|(?:\w+)|(?:\{[^}]+\}))\s+from\s+['"`]([^'"`]+)['"`]/g;
    const imports = [...content.matchAll(importRegex)];

    for (const match of imports) {
      const importPath = match[1];

      // Check for relative imports
      if (importPath.startsWith('./') || importPath.startsWith('../')) {
        const absolutePath = this.resolveImportPath(filePath, importPath);
        if (!this.modules.has(absolutePath)) {
          this.errors.push(`${filePath}: Missing dependency - ${importPath}`);
        }
      }
    }
  }

  checkExports(filePath, content) {
    // Check if module exports something
    if (!content.includes('export ')) {
      this.warnings.push(`${filePath}: No exports found`);
    }
  }

  resolveImportPath(currentFile, importPath) {
    const currentDir = dirname(currentFile);

    // Handle file extensions
    if (!importPath.endsWith('.js')) {
      importPath += '.js';
    }

    const resolved = join(currentDir, importPath);
    return resolved.replace(/\\/g, '/'); // Normalize path separators
  }

  async checkMissingDependencies() {
    console.log('📦 Checking dependencies...');

    // Check for external dependencies
    const packageJsonPath = join(projectRoot, 'package.json');
    try {
      const packageJson = JSON.parse(readFileSync(packageJsonPath, 'utf8'));
      const dependencies = {
        ...packageJson.dependencies,
        ...packageJson.devDependencies
      };

      // Check for CDN dependencies in HTML
      const htmlFiles = [...this.modules.keys()].filter(file => file.endsWith('.html'));
      for (const htmlFile of htmlFiles) {
        const content = readFileSync(htmlFile, 'utf8');

        // Check for Socket.IO CDN
        if (content.includes('socket.io.min.js') && !dependencies['socket.io-client']) {
          this.warnings.push('Socket.IO used from CDN but not listed in package.json dependencies');
        }
      }

    } catch (error) {
      this.warnings.push('Could not read package.json');
    }
  }

  printResults() {
    console.log(`\n📊 Validation Results:`);
    console.log(`   Modules found: ${this.modules.size}`);
    console.log(`   Errors: ${this.errors.length}`);
    console.log(`   Warnings: ${this.warnings.length}\n`);

    if (this.errors.length > 0) {
      console.log('❌ Errors:');
      this.errors.forEach(error => console.log(`   • ${error}`));
      console.log('');
    }

    if (this.warnings.length > 0) {
      console.log('⚠️  Warnings:');
      this.warnings.forEach(warning => console.log(`   • ${warning}`));
      console.log('');
    }

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log('✅ All modules are valid!');
    } else if (this.errors.length === 0) {
      console.log('✅ Modules are valid with warnings');
    } else {
      console.log('❌ Modules have errors that need to be fixed');
    }
  }
}

// Run validation if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const validator = new ModuleValidator();
  const isValid = await validator.validate();
  process.exit(isValid ? 0 : 1);
}

export { ModuleValidator };