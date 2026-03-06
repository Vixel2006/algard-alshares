import axios from 'axios';
import * as vscode from 'vscode';

export class SecurePatchClient {
    private baseUrl: string;

    constructor() {
        const config = vscode.workspace.getConfiguration('securepatch');
        this.baseUrl = config.get<string>('backendUrl') || 'http://localhost:8000';
    }

    async checkHealth(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.baseUrl}/health`);
            return response.data.status === 'ok';
        } catch (error) {
            console.error('Backend health check failed:', error);
            return false;
        }
    }

    async extractFunctions(workspacePath: string): Promise<any[]> {
        try {
            const response = await axios.post(`${this.baseUrl}/extract`, null, {
                params: { workspace_path: workspacePath }
            });
            return response.data.functions;
        } catch (error) {
            console.error('Failed to extract functions:', error);
            return [];
        }
    }
}