# UniSHARP 로컬 Blender · Unreal 워크플로우

이 문서는 이 저장소에 추가한 **단일 이미지 → 3D Gaussian → Blender/Unreal** 로컬 도구의 구성과 사용법을 정리합니다.

## 결과 파일

GUI에서 이미지를 처리하면 지정한 출력 폴더에 다음 파일을 만듭니다.

| 파일 | 용도 |
| --- | --- |
| `<이름>_unisharp.blend` | Blender 장면입니다. Gaussian 포인트, 카메라, 축 컨트롤 및 선택한 배경/레퍼런스 큐브가 포함됩니다. |
| `<이름>_unreal_gaussian_splat.ply` | Unreal용 Gaussian Splat PLY입니다. GUI에서 **Unreal용 Gaussian Splat PLY 저장**을 켠 경우에만 생성됩니다. |

Unreal에는 반드시 `*_unreal_gaussian_splat.ply`를 사용하세요. Blender 점 표시용으로 변환한 색상 포인트 PLY는 중간 산출물이며 현재 GUI의 최종 출력으로 저장하지 않습니다.

## 포함된 도구와 라이브러리

### 핵심 추론/렌더링

| 항목 | 버전 또는 역할 |
| --- | --- |
| [UniSHARP](https://github.com/Insta360-Research-Team/UniSHARP) | 단일 이미지에서 카메라 레이를 추정하고 3D Gaussian을 예측하는 기본 모델입니다. |
| [UniK3D](https://github.com/lpiccinelli-eth/UniK3D) | 다양한 카메라 형식의 ray/feature 예측에 사용되는 포함 의존성입니다. |
| PyTorch / TorchVision / TorchAudio | `2.8.0` / `0.23.0` / `2.8.0`. NVIDIA GPU 추론에 사용합니다. 휴대용 패키지는 CUDA 12.8 PyTorch wheel을 설치합니다. |
| `gsplat` | `1.5.3`. Gaussian splatting 렌더링과 관련 연산에 사용합니다. |
| `triton`, `ninja` | GPU 커널 및 컴파일 보조 의존성입니다. |
| 3DGEER | 어안(fisheye) 렌더링 경로에서만 필요한 외부 CUDA rasterizer입니다. 원근/파노라마만 처리한다면 필수는 아닙니다. |

### 이미지·데이터 처리

`numpy`, `scipy`, `Pillow`, `pillow-heif`, `imageio`, `imageio-ffmpeg`, `opencv-python`, `matplotlib`, `h5py`, `plyfile`, `trimesh`, `pandas`, `tables`, `PyYAML`, `requests`, `tqdm`, `rich`, `click`, `safetensors`, `einops`, `protobuf`, `timm`, `huggingface-hub`, `lpips`, `tabulate`, `termcolor`을 사용합니다. 정확한 최소 버전은 [`requirements.txt`](../requirements.txt)를 기준으로 합니다.

### 로컬 UI·미리보기·DCC

| 항목 | 역할 |
| --- | --- |
| [Gradio](https://www.gradio.app/) `6.22.0` | `scripts/blender_gui.py`의 로컬 웹 GUI입니다. |
| [Viser](https://viser.studio/) `1.0.30` | GUI 안에서 Unreal PLY를 WebGL로 미리보기 위한 로컬 뷰어입니다. 이 뷰어는 파일을 업로드하지 않습니다. |
| [Blender 3.6 이상](https://www.blender.org/download/) | `.blend` 파일 생성에 사용합니다. 이 워크플로우는 Blender의 기본 PLY import가 있는 3.6 이상을 지원합니다. Windows 휴대용 실행기는 설치 여부를 확인하고, 없으면 5.2 LTS를 기본 설치 선택지로 제안합니다. |

GUI 전용 추가 의존성은 [`requirements-portable.txt`](../requirements-portable.txt)에 있으며, 기본 연구 환경은 [`requirements.txt`](../requirements.txt)에 있습니다.

## Windows 휴대용 실행

배포 폴더의 `Run-UniSHARP.cmd`를 더블클릭하면 됩니다.

1. Blender 3.6 이상이 없으면 공식 Blender 설치 파일을 다운로드해 설치를 안내합니다. 자동 설치의 기본 선택지는 Blender 5.2 LTS입니다.
2. UniSHARP 체크포인트가 없으면 공식 Hugging Face 배포처에서 약 4.7GB를 자동으로 다운로드합니다.
3. NVIDIA 드라이버/GPU를 확인합니다. CUDA 환경이 없으면 CUDA 12.8 네트워크 설치 파일을 다운로드하고 설치를 시작할지 묻습니다.
4. 프로젝트 전용 Miniforge/Python 환경과 필요한 Python 패키지를 준비한 뒤 GUI를 엽니다.

CUDA Toolkit은 PyTorch CUDA wheel 자체에 포함되는 런타임과는 별개입니다. GPU 드라이버가 최신이고 PyTorch가 정상 인식한다면 Toolkit을 별도로 설치하지 않아도 추론되는 구성도 있습니다. 설치 프로그램의 안내에 따라 드라이버/Toolkit을 준비한 뒤 재시작이 필요할 수 있습니다.

## Unreal Engine에서 Gaussian Splat PLY 열기

언리얼 기본 PLY 임포터만으로는 이 Gaussian 속성을 렌더링할 수 없습니다. 다음 렌더러 플러그인을 사용합니다.

- 플러그인: [MLSLabs Gaussian Splatting Renderer for Unreal Engine](https://github.com/mlslabs/MLSLabsGaussianSplattingRenderer-UE)
- 현재 설치 대상: Unreal Engine **5.5.4** 프로젝트 (`5.5.x` 지원 범위)
- 권장 환경: Windows 10/11, DirectX 12, NVIDIA Turing(Shader Model 7.5) 이상 GPU. 최소 RTX 2060, 원활한 사용은 RTX 4070 Ti 이상이 플러그인 저장소에 안내되어 있습니다.

### 프로젝트별 설치

1. MLSLabs 플러그인 저장소를 내려받습니다.
2. 저장소 안의 `Plugins\MLSLabsRenderer` 폴더를 Unreal 프로젝트의 아래 위치로 복사합니다.

   ```text
   <Unreal 프로젝트>\Plugins\MLSLabsRenderer
   ```

   예: `C:\Users\AIRev\Documents\Unreal Projects\test\Plugins\MLSLabsRenderer`

3. 프로젝트를 열고 **Edit → Plugins**에서 MLSLabs Renderer를 활성화한 뒤 에디터를 재시작합니다.
4. 콘텐츠 브라우저에서 `*_unreal_gaussian_splat.ply`를 플러그인의 Gaussian Splat import 기능으로 불러옵니다.

처음 열 때 `project could not be compiled`가 나오면 플러그인 버전과 UE 5.5.4가 맞는지 먼저 확인하고, C++ 프로젝트 빌드 도구(Visual Studio 2022의 **Desktop development with C++** 및 Windows SDK)를 설치한 후 프로젝트 파일을 다시 생성/빌드하세요.

패키징된 게임에서도 이 플러그인을 포함해야 한다면 플러그인 문서의 안내대로 엔진의 `Engine\Plugins\Marketplace` 경로에도 배치하는 방식을 검토하세요. 일반적인 편집 작업은 프로젝트의 `Plugins` 폴더 설치만으로 충분합니다.

## 참고

- UniSHARP 모델 체크포인트는 `checkpoints/pretained_model.pt`가 기본값이며, 파일이 없으면 GUI 또는 휴대용 실행기가 [공식 Hugging Face 배포처](https://huggingface.co/Insta360-Research/Unisharp)에서 자동으로 받습니다.
- Blender 파일의 거리 단위는 미터로 설정하지만, 단일 이미지 복원 결과의 절대 스케일은 추정값입니다.
- 원근 카메라를 사용한 장면에서 필요하면 GUI의 세로 맞춤/스케일 옵션을 조절해 원본 이미지와 viewport overlay를 맞출 수 있습니다.
