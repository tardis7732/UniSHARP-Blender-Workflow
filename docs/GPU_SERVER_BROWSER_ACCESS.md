# GPU 서버 브라우저 실행과 PIN 접속

GPU 서버에서는 Blender 파일 생성 UI를 브라우저로 쓸 수 있습니다. 서버에 GUI용 데스크톱 환경은 필요하지 않습니다. Blender는 background 모드로 `.blend` 파일을 생성합니다.

## 권장: VS Code Remote-SSH 포트포워딩

이 방법은 UI 포트를 인터넷에 직접 공개하지 않습니다. 이미지가 외부 relay를 거치지 않고 SSH 터널로만 이동하므로, 입력 이미지가 민감할 때 권장합니다.

VS Code의 원격 터미널에서 프로젝트 환경을 활성화한 뒤 실행합니다.

```bash
cd ~/UniSHARP-Blender-Workflow
conda activate unisharp
bash scripts/run_browser_ui.sh
```

터미널에 다음처럼 표시됩니다.

```text
[UniSHARP] Browser login  |  username: unisharp  |  PIN: 123456
```

1. VS Code 하단 패널의 **PORTS** 탭을 엽니다.
2. `7860` 포트를 찾아 **Open in Browser**를 누릅니다. 보이지 않으면 **Forward a Port**에서 `7860`을 추가합니다.
3. 브라우저 로그인 창에서 username은 `unisharp`, password에는 터미널의 6자리 PIN을 넣습니다.

프로세스를 다시 시작하면 새 PIN이 생성됩니다. 고정 PIN이 필요하면 터미널 히스토리에 남지 않도록 환경 변수로 설정합니다.

```bash
export UNISHARP_UI_PIN='원하는-긴-PIN'
bash scripts/run_browser_ui.sh
```

## 포트를 직접 열 수 있는 서버 환경

플랫폼의 포트 노출/방화벽 설정이 있고, 내부망 또는 VPN에서만 접근하도록 제한할 수 있을 때 사용합니다.

```bash
bash scripts/run_browser_ui.sh --host 0.0.0.0 --port 7860
```

브라우저에서 `http://<서버-주소>:7860`으로 접속하고, 출력된 username/PIN으로 로그인합니다. 인터넷에 직접 노출하는 경우에는 PIN만으로 충분한 보호가 아닐 수 있으므로 반드시 플랫폼 방화벽, VPN 또는 reverse proxy 인증을 함께 사용하세요.

## 임시 공유 URL

플랫폼 포트포워딩이 안 되면 Gradio의 임시 공유 URL을 만들 수 있습니다.

```bash
bash scripts/run_browser_ui.sh --share
```

터미널에 표시되는 `https://...gradio.live` 주소로 접속합니다. 이 URL도 username `unisharp`와 실행 때 출력된 PIN을 요구합니다. 공유 URL은 임시이며, 업로드한 이미지 데이터가 Gradio relay를 경유할 수 있으므로 민감한 파일에는 VS Code 포트포워딩 방식을 사용하세요.

## 서버 환경 최소 확인

```bash
nvidia-smi
blender --version
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Blender는 3.6 이상이면 됩니다. 설치 경로를 자동으로 찾지 못하면 `BLENDER_EXE` 환경 변수에 Blender 실행 파일의 절대 경로를 지정하세요.
