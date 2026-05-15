/**
 * API Wrapper for pywebview bridge
 */
export class Api {
    constructor() {
        this.ready = false;
        this._initPromise = new Promise((resolve) => {
            window.addEventListener('pywebviewready', () => {
                this.ready = true;
                resolve();
            });
        });
    }

    async ensureReady() {
        if (!this.ready) {
            await this._initPromise;
        }
    }

    async checkHealth() {
        await this.ensureReady();
        return await window.pywebview.api.check_health();
    }

    async getHistory() {
        await this.ensureReady();
        return await window.pywebview.api.get_history();
    }
    
    async getScan(id) {
        await this.ensureReady();
        return await window.pywebview.api.get_scan(id);
    }

    async startScan(config) {
        await this.ensureReady();
        return await window.pywebview.api.start_scan(config);
    }

    async stopScan() {
        await this.ensureReady();
        return await window.pywebview.api.stop_scan();
    }
}

export const api = new Api();
