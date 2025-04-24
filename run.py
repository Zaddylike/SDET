import os

# 定義 TestPilot 專案結構
structure = {
    "TestPilot": [
        "runner.py",
        "api_handler.py",
        "ws_handler.py",
        "ui_web_handler.py",
        "ui_app_handler.py",
        "stress_handler.py",
        "validator.py",
        "report_handler.py",
        "yaml_loader.py",
        "config.py",
        "__init__.py"
    ],
    "utils": ["tools.py", "__init__.py"],
    "examples": ["api_login.yaml"],
    "cli": ["main.py"],
    "report": ["sample_report.csv", "sample_report.json", "sample_report.html"],
    "tests": ["test_runner.py"],
    ".": ["README.md", "setup.py"]
}

# 建立資料夾與檔案
for folder, files in structure.items():
    os.makedirs(folder, exist_ok=True)
    for file in files:
        file_path = os.path.join(folder, file)
        with open(file_path, "w") as f:
            if file == "README.md":
                f.write("# TestPilot\n\nA unified testing library for API, WebSocket, UI, and performance testing.")
            elif file == "setup.py":
                f.write(
                    "from setuptools import setup, find_packages\n\n"
                    "setup(\n"
                    "    name='TestPilot',\n"
                    "    version='0.1.0',\n"
                    "    packages=find_packages(),\n"
                    "    install_requires=[],\n"
                    "    author='Watson',\n"
                    "    description='A unified testing library driven by YAML for APIs, WebSocket, UI, and performance.'\n"
                    ")"
                )
            elif file.endswith(".html"):
                f.write(
                    "<!DOCTYPE html>\n<html><head><title>Test Report</title></head>\n"
                    "<body><h1>Sample Test Report</h1><table border='1'>\n"
                    "<tr><th>Case</th><th>Status</th><th>Message</th></tr>\n"
                    "<tr><td>Login Test</td><td>PASS</td><td>Login success</td></tr>\n"
                    "</table></body></html>"
                )
            else:
                f.write("")  # 空白初始檔案

"TestPilot v1.0 架構已建立完成！"
