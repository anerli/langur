import os
from pathlib import Path

VIEWER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Graph Viewer</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: Arial, sans-serif;
        }
        .logo {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 60px;
            height: 60px;
        }
        .controls {
            display: flex;
            gap: 20px;
            align-items: center;
            margin: 20px 0;
        }
        .arrow-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            font-size: 18px;
        }
        .arrow-btn:disabled {
            background: #cccccc;
            cursor: not-allowed;
        }
        .graph-container {
            width: 100%;
            height: 800px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <a href="https://github.com/anerli/langur" target="_blank">
        <svg class="logo" viewBox="0 0 492.47363 492.47366" version="1.1" xmlns="http://www.w3.org/2000/svg">
            <g transform="translate(-2621.908,-270.72006)">
                <rect style="display:inline;fill:#000000;fill-opacity:1;stroke-width:19.4652;stroke-opacity:0.996951" width="492.47357" height="492.47357" x="2621.908" y="270.72006" ry="68.615402" />
                <path style="color:#000000;display:inline;fill:#ffffff;fill-opacity:1;-inkscape-stroke:none" d="m 2868.1447,313.20605 c 0,0 -101.4418,62.24614 -149.0312,144.67336 -47.5894,82.4273 -50.7752,201.4016 -50.7752,201.4016 0,0 104.6277,56.7284 199.8064,56.7284 95.1788,0 199.8064,-56.7284 199.8064,-56.7284 0,0 -3.1853,-118.9744 -50.7746,-201.4016 -47.5894,-82.42729 -149.0318,-144.67336 -149.0318,-144.67336 z m 0,117.85636 c 62.4215,0 131.0396,37.2045 131.0396,37.2045 0,0 -2.089,78.0274 -33.2998,132.086 -31.2108,54.0586 -97.7398,94.8815 -97.7398,94.8815 0,0 -66.5292,-40.8229 -97.7397,-94.8815 -31.2108,-54.0586 -33.3003,-132.086 -33.3003,-132.086 0,0 68.6184,-37.2045 131.04,-37.2045 z" />
                <ellipse style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:0.297659;stroke-dasharray:none;stroke-opacity:1" cx="2802.6106" cy="516.95685" rx="22.949991" ry="42.48605" />
                <ellipse style="fill:#ffffff;fill-opacity:1;stroke:none;stroke-width:0.297659;stroke-dasharray:none;stroke-opacity:1" cx="-2933.6785" cy="516.95685" rx="22.949991" ry="42.48605" transform="scale(-1,1)" />
            </g>
        </svg>
    </a>

    <div class="controls">
        <button id="prevBtn" class="arrow-btn">Prev</button>
        <span id="currentGraph">Graph 1</span>
        <button id="nextBtn" class="arrow-btn">Next</button>
    </div>
    <div class="graph-container">
        <iframe id="graphFrame" src=""></iframe>
    </div>

    <script>
        const graphs = [{{graphs}}];
        
        let currentIndex = 0;
        const graphFrame = document.getElementById('graphFrame');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const currentGraphText = document.getElementById('currentGraph');

        function updateGraph() {
            graphFrame.src = graphs[currentIndex];
            currentGraphText.textContent = graphs[currentIndex];
            prevBtn.disabled = currentIndex === 0;
            nextBtn.disabled = currentIndex === graphs.length - 1;
        }

        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateGraph();
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentIndex < graphs.length - 1) {
                currentIndex++;
                updateGraph();
            }
        });

        // Initialize first graph
        updateGraph();
    </script>
</body>
</html>
'''


def generate_viewer(path):
    graphs_dir = Path(path) / 'graphs'
    
    graph_files = []
    if graphs_dir.exists() and graphs_dir.is_dir():
        graph_files = sorted([
            f"'./graphs/{f.name}'"
            for f in graphs_dir.iterdir()
            if f.suffix.lower() == '.html'
        ])
    
    graphs_array = ',\n'.join(graph_files)
    
    viewer_html = VIEWER_TEMPLATE.replace('{{graphs}}', graphs_array)
    
    output_path = Path(path) / 'viewer.html'
    with open(output_path, 'w') as f:
        f.write(viewer_html)
    
    return str(output_path)