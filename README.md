# UniSHARP Blender Workflow

단일 이미지를 UniSHARP 3D Gaussian으로 변환하고, Blender 장면과 Unreal Engine용 Gaussian Splat PLY를 만드는 Windows 로컬 워크플로우입니다.

> 이 저장소는 [Insta360 Research Team의 UniSHARP](https://github.com/Insta360-Research-Team/UniSHARP)를 기반으로 한 비공식 로컬 워크플로우입니다. 원 논문·모델·연구 코드의 상세 내용은 [원본 저장소](https://github.com/Insta360-Research-Team/UniSHARP)를 참고하세요. Insta360 Research Team 또는 UniK3D 저자와 제휴·보증 관계가 아닙니다.

## 빠른 시작 (Windows)

1. NVIDIA GPU가 있는 Windows PC에서 배포 폴더의 `Run-UniSHARP.cmd`를 실행합니다.
2. Blender 5.2 LTS가 없으면 안내에 따라 설치합니다.
3. 로컬 GUI에서 이미지를 고르고 출력 폴더와 옵션을 정한 뒤 **Blender 파일 생성**을 누릅니다.

생성 결과는 다음과 같습니다.

- `<이름>_unisharp.blend` — Gaussian 포인트와 카메라가 들어 있는 Blender 장면
- `<이름>_unreal_gaussian_splat.ply` — Unreal 플러그인으로 불러올 Gaussian Splat PLY

모델 체크포인트와 개인 입력/생성 결과물은 이 저장소에 포함하지 않습니다.

## 문서

- [Blender · Unreal 사용 가이드](docs/LOCAL_BLENDER_UNREAL_GUIDE.md) — 사용 라이브러리, 휴대용 실행, PLY 결과물, Unreal 플러그인 설치 방법
- [서드파티 고지 및 라이선스](THIRD_PARTY_NOTICES.md) — UniSHARP, UniK3D 및 외부 도구의 출처와 적용 라이선스
- [원본 UniSHARP 저장소](https://github.com/Insta360-Research-Team/UniSHARP) — 연구 코드의 전체 설치·학습·검증 안내

## 라이선스

이 저장소에는 별도 라이선스를 가진 구성요소가 함께 들어 있습니다. 사용·수정·재배포 전에 반드시 모든 적용 라이선스를 확인하세요.

- UniSHARP 기반 소스: 저장소 루트의 [LICENSE](LICENSE)에 있는 **CC BY-NC 4.0** — 저작자 표시와 비상업 조건이 적용됩니다.
- 포함된 `UniK3D/` 소스: [`UniK3D/LICENSE`](UniK3D/LICENSE)에 있는 **CC BY-NC-SA 4.0** — 저작자 표시·비상업·동일조건변경허락 조건이 적용됩니다.
- Blender, PyTorch, Gradio, Viser, MLSLabs Unreal 플러그인 등은 각 프로젝트의 자체 라이선스를 따릅니다.

특히 상업적 사용이나 배포 전에는 원 저작권자 및 각 외부 구성요소의 라이선스 조건을 별도로 검토해야 합니다.
