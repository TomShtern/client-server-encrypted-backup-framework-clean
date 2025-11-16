import { formatBytes } from '../utils/formatters.js';

const RECENT_STORAGE_KEY = 'cyberbackup-recent-files';
const MAX_RECENT = 5;

export class FileManager {
  constructor({ dropZone, fileInput, selectButton, clearButton, recentButton, nameLabel, infoLabel, announcer, onRecent }) {
    this.dropZone = dropZone;
    this.fileInput = fileInput;
    this.selectButton = selectButton;
    this.clearButton = clearButton;
    this.recentButton = recentButton;
    this.nameLabel = nameLabel;
    this.infoLabel = infoLabel;
    this.announcer = announcer;
    this.onRecent = onRecent;

    this.currentFile = null;
    this.currentFileMeta = null;
    this.recent = this.#loadRecent();

    this.#attachEvents();
    this.#updateUI();
  }

  get file() {
    return this.currentFile;
  }

  clear() {
    this.currentFile = null;
    this.currentFileMeta = null;
    if (this.fileInput) {
      this.fileInput.value = '';
    }
    this.#updateUI();
  }

  #attachEvents() {
    if (this.selectButton) {
      this.selectButton.addEventListener('click', () => this.fileInput?.click());
    }
    if (this.fileInput) {
      this.fileInput.addEventListener('change', (event) => {
        const input = event.target;
        const file = input.files?.[0];
        if (file) {
          this.#handleFile(file);
        }
      });
    }
    if (this.clearButton) {
      this.clearButton.addEventListener('click', () => {
        this.clear();
        this.announcer?.announce('File cleared');
      });
    }
    if (this.recentButton) {
      this.recentButton.addEventListener('click', () => this.#showRecent());
    }
    if (this.dropZone) {
      const onDragOver = (event) => {
        event.preventDefault();
        this.dropZone?.classList.add('drag-over');
      };
      const onDragLeave = () => this.dropZone?.classList.remove('drag-over');
      const onDrop = (event) => {
        event.preventDefault();
        this.dropZone?.classList.remove('drag-over');
        if (event.dataTransfer?.files?.[0]) {
          this.#handleFile(event.dataTransfer.files[0]);
        }
      };
      this.dropZone.addEventListener('dragover', onDragOver);
      this.dropZone.addEventListener('dragleave', onDragLeave);
      this.dropZone.addEventListener('drop', onDrop);
    }
  }

  #handleFile(file) {
    this.currentFile = file;
    this.currentFileMeta = {
      name: file.name,
      size: file.size,
      type: file.type || 'application/octet-stream',
      lastModified: file.lastModified,
    };
    this.#updateUI();
    this.#saveRecent(this.currentFileMeta);
    this.announcer?.announce(`Selected ${file.name}, size ${formatBytes(file.size)}`);
  }

  #updateUI() {
    if (!this.nameLabel || !this.infoLabel) {
      return;
    }
    const namePlaceholder = this.nameLabel.dataset.placeholder || 'Drag & drop a file here or choose above';
    const infoPlaceholder = this.infoLabel.dataset.placeholder || 'Size — • Type —';
    if (!this.currentFileMeta) {
      this.nameLabel.textContent = namePlaceholder;
      this.nameLabel.classList.add('placeholder');
      this.infoLabel.textContent = infoPlaceholder;
      this.infoLabel.classList.add('placeholder');
      if (this.clearButton) {
        this.clearButton.disabled = true;
      }
      // Remove file-selected class when no file
      this.dropZone?.classList.remove('file-selected', 'file-invalid');
      return;
    }
    const { name, size, type } = this.currentFileMeta;

    // Add file-selected class with animation
    this.dropZone?.classList.add('file-selected');
    this.dropZone?.classList.remove('file-invalid');

    this.nameLabel.textContent = name;
    this.nameLabel.classList.remove('placeholder');
    this.infoLabel.textContent = `${formatBytes(size)} • ${type}`;
    this.infoLabel.classList.remove('placeholder');

    // Add animation to file icon
    const fileIcon = this.dropZone?.querySelector('.file-icon');
    if (fileIcon) {
      fileIcon.classList.add('file-selected');
    }

    if (this.clearButton) {
      this.clearButton.disabled = false;
    }
  }

  #showRecent() {
    if (!this.recent.length) {
      this.announcer?.announce('No recent files yet');
      return;
    }
    const newest = this.recent[0];
    const formattedSize = formatBytes(newest.size);
    const message = `Recent: ${newest.name} (${formattedSize})`;
    this.announcer?.announce(message);
    if (typeof this.onRecent === 'function') {
      this.onRecent({ ...newest, formattedSize });
    }
  }

  #saveRecent(meta) {
    if (!meta?.name) return;
    this.recent = [meta, ...this.recent.filter((entry) => entry.name !== meta.name)].slice(0, MAX_RECENT);
    try {
      localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(this.recent));
    } catch (error) {
      console.warn('Failed to persist recent files', error);
    }
  }

  #loadRecent() {
    try {
      const stored = localStorage.getItem(RECENT_STORAGE_KEY);
      if (!stored) return [];
      const parsed = JSON.parse(stored);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }
}
