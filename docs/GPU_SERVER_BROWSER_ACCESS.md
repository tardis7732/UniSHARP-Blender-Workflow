# GPU 서버 브라우저 실행과 PIN 접속

GPU 서버에서는 Blender 파일 생성 UI를 브라우저로 쓸 수 있습니다. 서버에 GUI용 데스크톱 환경은 필요하지 않습니다. Blender는 background 모드로 `.blend` 파일을 생성합니다.

## `~/air`에 최소 코드만 clone

체크포인트, 생성 결과물, Windows 휴대용 실행 파일 및 데모 에셋은 Git 저장소에 포함하지 않습니다. 아래 sparse clone은 서버 추론에 필요한 Python 소스와 Linux 브라우저 실행 스크립트만 받습니다.

```bash
mkdir -p ~/air
cd ~/air
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/tardis7732/UniSHARP-Blender-Workflow.git unisharp-blender
cd unisharp-blender
git sparse-checkout set --no-cone \
  /.gitignore /LICENSE /README.md /THIRD_PARTY_NOTICES.md \
  /requirements.txt /requirements-portable.txt \
  /unisharp/** /scripts/** /docs/** \
  /UniK3D/.gitignore /UniK3D/LICENSE /UniK3D/pyproject.toml /UniK3D/requirements.txt /UniK3D/unik3d/**
```

Blender 실행 파일은 Git으로 받지 않습니다. 서버에 Blender 3.6 이상을 설치하거나, 이미 설치된 Blender의 경로를 `BLENDER_EXE`로 지정하면 됩니다. 체크포인트는 첫 실행 때 별도로 자동 다운로드됩니다.

## 권장: VS Code Remote-SSH 포트포워딩

이 방법은 UI 포트를 인터넷에 직접 공개하지 않습니다. 이미지가 외부 relay를 거치지 않고 SSH 터널로만 이동하므로, 입력 이미지가 민감할 때 권장합니다.

VS Code의 원격 터미널에서 프로젝트 환경을 활성화한 뒤 실행합니다.

```bash
cd ~/air/unisharp-blender
conda activate unisharp
bash scripts/run_browser_ui.sh
```

터미널에 다음처럼 표시됩니다.

```text
[UniSHARP] Browser PIN: 123456  |  Leave the username field blank and enter this PIN as the password.
```

1. VS Code 하단 패널의 **PORTS** 탭을 엽니다.
2. `7860` 포트를 찾아 **Open in Browser**를 누릅니다. 보이지 않으면 **Forward a Port**에서 `7860`을 추가합니다.
3. 브라우저 로그인 창에서 **Username은 비워 두고**, Password에 터미널의 6자리 PIN을 넣습니다.

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

브라우저에서 `http://<서버-주소>:7860`으로 접속하고, Username은 비운 채 출력된 PIN을 Password에 넣어 로그인합니다. 인터넷에 직접 노출하는 경우에는 PIN만으로 충분한 보호가 아닐 수 있으므로 반드시 플랫폼 방화벽, VPN 또는 reverse proxy 인증을 함께 사용하세요.

## 임시 공유 URL

플랫폼 포트포워딩이 안 되면 Gradio의 임시 공유 URL을 만들 수 있습니다.

```bash
bash scripts/run_browser_ui.sh --share
```

터미널에 표시되는 `https://...gradio.live` 주소로 접속합니다. 브라우저의 Username 칸은 비워 두고, Password에 실행 때 출력된 PIN을 넣으세요. 공유 URL은 임시이며, 업로드한 이미지 데이터가 Gradio relay를 경유할 수 있으므로 민감한 파일에는 VS Code 포트포워딩 방식을 사용하세요.

Gradio 임시 공유 URL은 실행할 때마다 새로 만들어지므로 URL 자체를 고정할 수 없습니다. 고정 주소가 필요하면 GPU 서버 플랫폼에서 7860 포트의 고정 ingress/domain을 만들고 `--host 0.0.0.0`으로 실행해야 합니다.

## 서버 환경 최소 확인

```bash
nvidia-smi
blender --version
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Blender는 3.6 이상이면 됩니다. 설치 경로를 자동으로 찾지 못하면 `BLENDER_EXE` 환경 변수에 Blender 실행 파일의 절대 경로를 지정하세요.
