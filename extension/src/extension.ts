import * as vscode from 'vscode';
import { SecurePatchClient } from './client';
import { SecurePatchSidebarProvider } from './sidebar';

export function activate(context: vscode.ExtensionContext) {
    console.log('SecurePatch extension is now active');
    const client = new SecurePatchClient();
    const sidebarProvider = new SecurePatchSidebarProvider(context.extensionUri);

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            SecurePatchSidebarProvider.viewType,
            sidebarProvider
        )
    );

    let scanCommand = vscode.commands.registerCommand('securepatch.scan', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open.');
            return;
        }

        const workspacePath = workspaceFolders[0].uri.fsPath;
        vscode.window.showInformationMessage(`Scanning workspace: ${workspacePath}...`);

        const functions = await client.extractFunctions(workspacePath);
        vscode.window.showInformationMessage(`Found ${functions.length} functions.`);
        sidebarProvider.updateFunctionList(functions);
    });

    let healthCheckCommand = vscode.commands.registerCommand('securepatch.healthCheck', async () => {
        const isHealthy = await client.checkHealth();
        if (isHealthy) {
            vscode.window.showInformationMessage('SecurePatch Backend is online!');
        } else {
            vscode.window.showErrorMessage('SecurePatch Backend is offline. Please check your settings.');
        }
    });

    context.subscriptions.push(scanCommand, healthCheckCommand);
}

export function deactivate() { }
