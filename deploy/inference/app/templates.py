DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Click Sound Detection Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.6;
            background-color: #f5f5f5;
        }

        .nav {
            background: #333;
            padding: 1rem;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }

        .nav-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            cursor: pointer;
        }

        .nav a:hover {
            background: #555;
            border-radius: 4px;
        }

        .main-content {
            max-width: 800px;
            margin: 80px auto 0;
            padding: 20px;
        }

        .section {
            background: white;
            margin-bottom: 30px;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Demo 部分样式 */
        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }

        input[type="text"], 
        input[type="file"],
        input[type="password"],
        input[type="email"],
        textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 6px;
            transition: border-color 0.3s;
        }

        input:focus, 
        textarea:focus {
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

        /* 模态框样式 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            z-index: 1001;
        }

        .modal-content {
            background-color: white;
            max-width: 500px;
            margin: 100px auto;
            padding: 20px;
            border-radius: 8px;
            position: relative;
        }

        .close {
            position: absolute;
            right: 20px;
            top: 10px;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        }

        .required {
            color: red;
        }

        @media (max-width: 768px) {
            .nav-content {
                flex-direction: column;
                text-align: center;
            }

            .nav a {
                display: block;
                margin: 5px 0;
            }

            .main-content {
                padding: 10px;
            }

            .section {
                padding: 15px;
            }

            button {
                width: 100%;
            }

            .modal-content {
                margin: 60px 20px;
            }
        }

        .section h2 {
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
            color: #333;
        }

        .section h3 {
            font-size: 1.25rem;
            margin: 1.5rem 0 1rem;
            color: #444;
        }

        .section p {
            margin-bottom: 1rem;
        }

        .section ul, 
        .section ol {
            margin-bottom: 1rem;
            padding-left: 1.5rem;
        }

        .section li {
            margin-bottom: 0.5rem;
        }

        .section strong {
            color: #333;
        }

        .section em {
            color: #666;
        }

        @media (max-width: 768px) {
            .section h2 {
                font-size: 1.5rem;
            }
            
            .section h3 {
                font-size: 1.1rem;
            }
            
            .section {
                margin-bottom: 20px;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-content">
            <div>
                <a href="#demo">Demo</a>
                <a href="#about">About</a>
                <a onclick="openContactModal()">Contact</a>
            </div>
        </div>
    </nav>

    <div class="main-content">
        <!-- Demo Section -->
        <section id="demo" class="section">
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
        </section>

        <!-- About Section -->
        <section id="about" class="section">
            <h2>About the Demo</h2>
            <p>This demo showcases our AI-powered click sound detection system, designed to identify and analyze click sounds in audio recordings. Our machine learning model has been trained to recognize specific click patterns and characteristics.</p>
            
            <h3>Technical Requirements</h3>
            <ul>
                <li><strong>File Format:</strong> WAV format only</li>
                <li><strong>Audio Channel:</strong> Mono (single channel)</li>
                <li><strong>Duration:</strong> Maximum 3 seconds recommended</li>
                <li><strong>Sampling Rate:</strong> Up to 48kHz</li>
                <li><strong>File Size:</strong> Maximum 10MB</li>
            </ul>

            <h3>Current Limitations</h3>
            <ul>
                <li>The model is trained on a specific subset of click sounds and may not recognize all types of clicks</li>
                <li>Performance may vary depending on background noise and audio quality</li>
                <li>Best results are achieved with clear, isolated click sounds</li>
            </ul>

            <h3>How to Use</h3>
            <ol>
                <li>Enter your API token</li>
                <li>Upload a WAV file meeting the above specifications</li>
                <li>Click "Detect Click" to analyze</li>
                <li>View results showing click probability and detection metrics</li>
            </ol>

            <p><em>Note: This is a demonstration version. For commercial use or access to the full model capabilities, please contact us.</em></p>
        </section>
    </div>

    <!-- 联系表单模态框 -->
    <div id="contactModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeContactModal()">&times;</span>
            <h2>Contact Us</h2>
            <form id="contactForm" onsubmit="return handleSubmit(event)">
                <div class="form-group">
                    <label>Name <span class="required">*</span></label>
                    <input type="text" name="name" required>
                </div>
                
                <div class="form-group">
                    <label>Email <span class="required">*</span></label>
                    <input type="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label>Message <span class="required">*</span></label>
                    <textarea name="message" required rows="4"></textarea>
                </div>
                
                <button type="submit">Send Message</button>
            </form>
        </div>
    </div>

    <script>
        // Demo 功能相关代码
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
            
            try {
                loadingDiv.style.display = 'block';
                resultDiv.style.display = 'none';
                timingDiv.innerHTML = '';
                statusDiv.style.display = 'none';
                detectButton.disabled = true;
                
                const timeResponse = await fetch('/time');
                const timeData = await timeResponse.json();
                const serverTime = timeData.server_time;
                const clientTime = Date.now();
                const timeDifference = serverTime - clientTime;
                
                const calibratedStartTime = Date.now() + timeDifference;
                
                const formData = new FormData();
                formData.append('file', audioFile);
                formData.append('client_start_time', calibratedStartTime.toString());
                
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
                    
                    const uploadTime = metrics.timing.server_receive_time - metrics.timing.client_start_time;
                    const processingTime = metrics.timing.server_complete_time - metrics.timing.server_receive_time;
                    
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

        // 模态框控制
        function openContactModal() {
            document.getElementById('contactModal').style.display = 'block';
        }

        function closeContactModal() {
            document.getElementById('contactModal').style.display = 'none';
        }

        // 点击模态框外部关闭
        window.onclick = function(event) {
            if (event.target == document.getElementById('contactModal')) {
                closeContactModal();
            }
        }

        // 表单提交处理
        async function handleSubmit(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                message: formData.get('message')
            };

            try {
                const response = await fetch('/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert('Thank you for your message. We will contact you soon.');
                    event.target.reset();
                    closeContactModal();
                } else {
                    throw new Error('Failed to submit form');
                }
            } catch (error) {
                alert('Error submitting form: ' + error.message);
            }
            return false;
        }
    </script>
</body>
</html>
"""