# UniSHARP Blender Workflow

단일 이미지를 UniSHARP 3D Gaussian으로 변환하고 Blender 장면과 Unreal용 Gaussian Splat PLY를 만드는 로컬/서버용 도구입니다.

> [Insta360 Research Team의 UniSHARP](https://github.com/Insta360-Research-Team/UniSHARP)를 기반으로 한 비공식 워크플로우입니다. 연구 코드·논문·모델의 원본 정보는 [UniSHARP 원본 저장소](https://github.com/Insta360-Research-Team/UniSHARP)를 참고하세요.

## 실행

프로젝트 Python 환경에서 아래 한 줄로 브라우저 UI를 엽니다.

```bash
python scripts/blender_gui.py
```

서버 브라우저 접속용 PIN UI는 다음과 같이 실행합니다.

```bash
export UNISHARP_UI_PIN='123457'
bash scripts/run_browser_ui.sh --share
```

`BLENDER_EXE`가 설정돼 있으면 그 실행 파일을 쓰고, 그렇지 않으면 PATH의 `blender` 명령을 사용합니다. 체크포인트가 없을 때는 공식 Hugging Face 배포처에서 자동으로 받습니다.

## 생성 파일

- `<이름>_unisharp.blend` — Gaussian 포인트와 카메라가 포함된 Blender 장면
- `<이름>_unreal_gaussian_splat.ply` — Unreal Gaussian Splat 플러그인용 PLY

## 문서

- [GPU 서버 브라우저/PIN 접속](docs/GPU_SERVER_BROWSER_ACCESS.md)
- [서드파티 고지 및 라이선스](THIRD_PARTY_NOTICES.md)

## 라이선스

- UniSHARP 기반 소스: [CC BY-NC 4.0](LICENSE)
- 포함된 `UniK3D/` 소스: [CC BY-NC-SA 4.0](UniK3D/LICENSE)

상업적 사용 또는 재배포 전에는 원 저작권자와 각 외부 구성요소의 라이선스를 확인하세요.
