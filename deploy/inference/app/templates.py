DEMO_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" type="image/x-icon" href="data:image/x-icon;base64,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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBcA0BQXANAUFwnQFBeq0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBeq0BQXQdAUFwDQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzhMXANAUF0HQFBeq0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBdB0BQXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUF9TQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBfU0BQXCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUFwnQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUFwkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBc80BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUFzzQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXqtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXCtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBcKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXVdAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF1XQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXqtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXCtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBcKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXVdAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF1XQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXqtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBcA0BQXCtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUFwrQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBcA0BQXVdAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQXVdAUFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUF6rQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBeqAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXCtAUF/nQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX+dAUFwoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBdV0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBdVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXANAUFwrQFBf50BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf50BQXCtAUFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUF1XQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF1UAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXANAUFwrQFBf50BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF/nQFBcK0BQXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqBQWANAUF1XQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQXVagUFgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXANAUFwrQFBdV0BQXqtAUF6rQFBdV0BQXCtAUFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACqFBYA0BQXANAUF1XQFBdV0BQXANAUF1WoFBYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//AP///gB///gAH//wAA//4AAH/8AAA/+AAAH/AAAA/wAAAP4AAAB+AAAAfAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA+AAAAfgAAAH8AAAD/AAAA/4AAAf/AAAP/4AAH//AAD//4AB///wD/8=">
    <title>Click Sound Detection Demo</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 6px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, input[type="file"]:focus {
            border-color: #4CAF50;
            outline: none;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.1s;
            font-weight: 600;
        }
        button:hover {
            background-color: #45a049;
        }
        button:active {
            transform: scale(0.98);
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 6px;
            display: none;
        }
        .success {
            background-color: #dff0d8;
            border: 1px solid #d6e9c6;
            color: #3c763d;
        }
        .error {
            background-color: #f2dede;
            border: 1px solid #ebccd1;
            color: #a94442;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .loading::after {
            content: '';
            display: inline-block;
            width: 24px;
            height: 24px;
            border: 3px solid #4CAF50;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
        #uploadTiming {
            margin-top: 15px;
            font-size: 0.9em;
            color: #666;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
        }
        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
            .container {
                padding: 15px;
            }
            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Click Sound Detection Demo</h1>
        <div class="form-group">
            <label for="token">API Token:</label>
            <input type="password" id="token" placeholder="Enter your API token" autocomplete="off">
        </div>
        <div class="form-group">
            <label for="audio">Audio File (WAV):</label>
            <input type="file" id="audio" accept=".wav" onchange="validateFile(this)">
            <small style="color: #666;">Maximum file size: 10MB</small>
        </div>
        <button id="detectButton" onclick="detectClick()">Detect Click</button>
        
        <div id="loading" class="loading"></div>
        <div id="status" style="display: none; margin: 10px 0;"></div>
        <div id="result" style="display: none; margin: 10px 0;"></div>
        <div id="uploadTiming"></div>
    </div>

    <script>
        const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

        function validateFile(input) {
            const file = input.files[0];
            const detectButton = document.getElementById('detectButton');
            
            if (file) {
                if (file.size > MAX_FILE_SIZE) {
                    showStatus('File size exceeds 10MB limit', false);
                    input.value = '';
                    detectButton.disabled = true;
                    return false;
                }
                
                if (!file.type.includes('audio/wav')) {
                    showStatus('Please select a WAV file', false);
                    input.value = '';
                    detectButton.disabled = true;
                    return false;
                }
                
                detectButton.disabled = false;
                return true;
            }
            
            detectButton.disabled = true;
            return false;
        }

        async function detectClick() {
            const token = document.getElementById('token').value.trim();
            const audioFile = document.getElementById('audio').files[0];
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            const timingDiv = document.getElementById('uploadTiming');
            const statusDiv = document.getElementById('status');
            const detectButton = document.getElementById('detectButton');
            
            if (!token) {
                showStatus('Please enter your API token', false);
                return;
            }
            
            if (!audioFile || !validateFile(document.getElementById('audio'))) {
                return;
            }
            
            const clientStartTime = Date.now();
            const formData = new FormData();
            formData.append('file', audioFile);
            formData.append('client_start_time', clientStartTime.toString());
            
            try {
                loadingDiv.style.display = 'block';
                resultDiv.style.display = 'none';
                timingDiv.innerHTML = '';
                statusDiv.style.display = 'none';
                detectButton.disabled = true;
                
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'X-API-Token': token
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok && data.status === 'success') {
                    const prediction = data.result.prediction;
                    const metrics = data.metrics;
                    
                    const resultMessage = `
                        <strong>Result:</strong> ${prediction.class_name}<br><br>
                        <strong>Probabilities:</strong><br>
                        • No Click: ${(prediction.probabilities.non_click * 100).toFixed(2)}%<br>
                        • Click: ${(prediction.probabilities.click * 100).toFixed(2)}%
                    `;
                    showResult(resultMessage);
                    showStatus('Detection completed successfully', true);
                    
                    const uploadTime = (metrics.timing.server_receive_time - metrics.timing.client_start_time);
                    const processingTime = (metrics.timing.server_complete_time - metrics.timing.server_receive_time);
                    
                    const timingInfo = `
                        <strong>Performance Metrics:</strong><br>
                        • Upload time: ${uploadTime}ms<br>
                        • Processing time: ${processingTime}ms
                    `;
                    
                    timingDiv.innerHTML = timingInfo;
                } else {
                    showStatus(data.detail || 'Detection failed', false);
                }
            } catch (error) {
                console.error('Error details:', error);
                showStatus('Error: ' + error.message, false);
            } finally {
                loadingDiv.style.display = 'none';
                detectButton.disabled = false;
            }
        }

        function showResult(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.classList.add('success');
            resultDiv.innerHTML = message;
        }

        function showStatus(message, isSuccess) {
            const statusDiv = document.getElementById('status');
            statusDiv.style.display = 'block';
            statusDiv.style.padding = '10px';
            statusDiv.style.borderRadius = '6px';
            statusDiv.style.backgroundColor = isSuccess ? '#dff0d8' : '#f2dede';
            statusDiv.style.color = isSuccess ? '#3c763d' : '#a94442';
            statusDiv.innerHTML = message;
        }
    </script>
</body>
</html>
"""