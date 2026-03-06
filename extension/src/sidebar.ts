import * as vscode from 'vscode';

export class SecurePatchSidebarProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'securepatch.sidebar';
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        webviewView.webview.onDidReceiveMessage(data => {
            switch (data.type) {
                case 'onInfo': {
                    if (!data.value) { return; }
                    vscode.window.showInformationMessage(data.value);
                    break;
                }
                case 'onError': {
                    if (!data.value) { return; }
                    vscode.window.showErrorMessage(data.value);
                    break;
                }
            }
        });
    }

    public updateFunctionList(functions: any[]) {
        if (this._view) {
            this._view.webview.postMessage({ type: 'updateFunctions', value: functions });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>SecurePatch</title>
                <style>
                    body { font-family: sans-serif; padding: 10px; }
                    .function-item { 
                        border-bottom: 1px solid #ccc; 
                        padding: 5px 0; 
                        cursor: pointer;
                    }
                    .function-item:hover { background-color: #333; }
                    .severity { float: right; font-weight: bold; }
                    .low { color: blue; }
                    .medium { color: yellow; }
                    .high { color: orange; }
                    .critical { color: red; }
                </style>
            </head>
            <body>
                <h3>Detected Functions</h3>
                <div id="function-list">Scanning...</div>
                <script>
                    const vscode = acquireVsCodeApi();
                    window.addEventListener('message', event => {
                        const message = event.data;
                        switch (message.type) {
                            case 'updateFunctions':
                                const list = document.getElementById('function-list');
                                list.innerHTML = message.value.map(f => \`
                                    <div class="function-item" onclick="openFile('\${f.file_path}', \${f.start_line})">
                                        <span>\${f.name}</span>
                                        <span class="severity \${f.severity || 'low'}">\${f.severity || 'OK'}</span>
                                        <div style="font-size: 0.8em; color: #888;">\${f.file_path.split('/').pop()}</div>
                                    </div>
                                \`).join('');
                                break;
                        }
                    });
                    function openFile(path, line) {
                        // We'll handle this in extension.ts
                    }
                </script>
            </body>
            </html>`;
    }
}
