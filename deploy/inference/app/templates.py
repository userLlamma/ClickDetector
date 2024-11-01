DEMO_HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:image/x-icon;base64,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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBcA0BQXANAUFwnQFBeq0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBeq0BQXQdAUFwDQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAzhMXANAUF0HQFBeq0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBdB0BQXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUF9TQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBfU0BQXCQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUFwnQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUFwkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBc80BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUFzzQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXqtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXCtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBcKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXVdAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF1XQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXqtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXCtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBcKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXVdAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF1XQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXqtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF6rQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBcA0BQXCtAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUFwrQFBcAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBcA0BQXVdAUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQXVdAUFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUF6rQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBeqAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXCtAUF/nQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX+dAUFwoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADQFBdV0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBdVAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXANAUFwrQFBf50BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf50BQXCtAUFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANAUF1XQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF1UAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXANAUFwrQFBf50BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQX/9AUF/nQFBcK0BQXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAqBQWANAUF1XQFBf/0BQX/9AUF//QFBf/0BQX/9AUF//QFBf/0BQXVagUFgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0BQXANAUFwrQFBdV0BQXqtAUF6rQFBdV0BQXCtAUFwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACqFBYA0BQXANAUF1XQFBdV0BQXANAUF1WoFBYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//AP///gB///gAH//wAA//4AAH/8AAA/+AAAH/AAAA/wAAAP4AAAB+AAAAfAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA8AAAAPAAAADwAAAA+AAAAfgAAAH8AAAD/AAAA/4AAAf/AAAP/4AAH//AAD//4AB///wD/8=">
    <title>Click Sound Detection Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 4px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Click Sound Detection Demo</h1>
        <div class="form-group">
            <label for="token">API Token:</label>
            <input type="text" id="token" placeholder="Enter your API token">
        </div>
        <div class="form-group">
            <label for="audio">Audio File (WAV):</label>
            <input type="file" id="audio" accept=".wav">
        </div>
        <button onclick="detectClick()">Detect Click</button>
        
        <div id="loading" class="loading">
            Processing... Please wait...
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        async function detectClick() {
            const token = document.getElementById('token').value;
            const audioFile = document.getElementById('audio').files[0];
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            
            if (!token || !audioFile) {
                showResult('Please provide both token and audio file', false);
                return;
            }
            
            const formData = new FormData();
            formData.append('file', audioFile);
            
            try {
                loadingDiv.style.display = 'block';
                resultDiv.style.display = 'none';
                
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'X-API-Token': token
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const result = data.result.prediction;
                    const message = `
                        Result: ${result.class_name}<br>
                        Confidence: ${(result.score * 100).toFixed(2)}%<br>
                        Probabilities:<br>
                        - No Click: ${(result.probabilities['non_click'] * 100).toFixed(2)}%<br>
                        - Click: ${(result.probabilities['click'] * 100).toFixed(2)}%
                    `;
                    showResult(message, true);
                } else {
                    showResult(data.detail || 'Detection failed', false);
                }
            } catch (error) {
                showResult('Error: ' + error.message, false);
            } finally {
                loadingDiv.style.display = 'none';
            }
        }
        
        function showResult(message, isSuccess) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = message;
            resultDiv.className = isSuccess ? 'success' : 'error';
            resultDiv.style.display = 'block';
        }
    </script>
</body>
</html>
"""