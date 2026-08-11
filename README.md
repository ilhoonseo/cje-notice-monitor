# 🎓 청주교육대학교 교육전문대학원 공지 모니터링 시스템

> **Cheongju National University of Education Graduate School Announcement Monitoring & Notification System**
>
> 본 저장소는 청주교육대학교 교육전문대학원 공지사항 상태 페이지와 수동 수집 스크립트를 제공합니다. 새 공지 확인과 Gmail 알림은 저장소 밖의 Codex 예약 작업이 담당합니다.

---

## 🌟 주요 기능

1. **지능형 웹 스크래퍼 (Python)**:
   - 대학원 공지사항 목록 API(`brdList.do`)를 수동 요청하여 상태 페이지 데이터 갱신.
   - 중복 방지 로직 및 로컬 스토리지(`data/notices.json`) 연동을 통한 데이터 정합성 유지.
   - 한글 인코딩 자동 복원 및 SSL 인증 오류 회피 처리를 적용한 강력한 내구성.

2. **Gmail 새 공지 알림 (Codex 예약 작업)**:
   - Codex가 3시간마다 게시판을 직접 확인하고 새 공지가 있을 때만 Gmail로 알림 발송.
   - 제목, 작성자, 날짜, 본문 요약과 게시판 원본 링크를 제공.
   - 연결된 Gmail을 사용하므로 Gmail 앱 비밀번호나 GitHub Secret이 필요 없음.

3. **프리미엄 상태 페이지 대시보드 (Vercel)**:
   - **Rich Aesthetics**: 다크 슬레이트 블루 기반의 HSL 컬러 팔레트, 세련된 글래스모피즘(Glassmorphism) 효과, 호버 인터랙션, 맥박이 뛰는 듯한(Pulsating) 실시간 라이브 인디케이터가 적용된 하이엔드 SaaS 스타일 상태 페이지.
   - **실시간 데이터 동기화**: 브라우저 캐시를 무력화하는 `vercel.json` 캐시 컨트롤 및 자바스크립트 캐시 버스터 기법을 활용한 100% 최신 상태 제공.
   - **공지사항 상세 조회 팝업**: 외부 링크 이동 없이 대시보드 내에서 직접 공지사항 내용의 전체 HTML을 깔끔한 모달 창으로 조회하는 프리미엄 확장 편의 기능.

---

## 🛠 기술 스택

- **Back-end & Scraper**: Python 3.x, `requests`
- **Front-end Dashboard**: Plain HTML5, Modern Vanilla CSS, Plain JavaScript, FontAwesome Icons, Google Fonts (Inter, Noto Sans KR)
- **Deployment & Hosting**: Vercel (Static Web Server)
- **Scheduled Monitoring**: Codex Scheduled Tasks (3-Hour Interval)
- **Manual Maintenance**: GitHub Actions (`workflow_dispatch` only)

---

## 📂 디렉토리 구조

```text
├── .github/
│   └── workflows/
│       └── scrape.yml      # 필요할 때만 실행하는 수동 데이터 갱신
├── data/
│   ├── notices.json        # 최근 수집된 공지사항 원본 데이터 백업 (DB 역할)
│   └── status.json         # 모니터링 시스템의 활성 상태 및 에러 기록 파일
├── app.js                  # 대시보드 인터랙션 및 Fetch API 비동기 제어 스크립트
├── index.html              # 상태 대시보드 기본 마크업 레이아웃
├── requirements.txt        # Python 의존성 라이브러리 목록
├── scraper.py              # 모니터링 및 알림 핵심 수집 스크립트
├── style.css               # 프리미엄 다크 슬레이트 디자인 스타일시트
├── vercel.json             # Vercel 배포 헤더 및 라우팅 설정 파일
└── README.md               # 시스템 구축 가이드 및 매뉴얼
```

---

## 🚀 로컬 실행 및 개발 방법

### 1. 가상환경 구성 및 의존성 패키지 설치
프로젝트 루트 디렉토리에서 터미널을 실행한 뒤 다음 명령어를 순서대로 실행합니다.

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 가상환경 활성화 (macOS / Linux)
source venv/bin/activate

# 필수 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 구성
GitHub 스크래퍼에는 알림용 환경 변수가 필요하지 않습니다. Gmail 알림은 저장소와 독립된 Codex 예약 작업이 담당합니다.

### 3. 수집 스크립트 1회 강제 실행
로컬 가상환경 내에서 최초로 수집을 수행하여 로컬 데이터베이스 파일(`notices.json`, `status.json`)을 구축합니다.

```bash
python scraper.py
```
> **Note**: 이 스크립트는 상태 페이지 데이터를 갱신할 뿐 이메일이나 텔레그램 알림을 보내지 않습니다.

### 4. 대시보드 웹서버 실행
상태 대시보드는 정적 웹 어플리케이션으로, 단순 파일 열기 방식이 아닌 로컬 웹 서버 환경에서 로드되어야 `/data/*.json` 리소스를 정상적으로 로드(Fetch)할 수 있습니다.

```bash
# Python 내장 웹서버를 이용해 실행하는 경우
python -m http.server 3000
```
브라우저에서 `http://localhost:3000`에 접속하여 화려하고 세련된 프리미엄 대시보드를 감상하세요!

---

## 🤖 GitHub Actions 수동 데이터 갱신

GitHub의 예약 실행은 중단되어 있습니다. 상태 페이지 데이터를 수동으로 갱신할 때만 Actions 화면에서 워크플로를 실행합니다.

### 1. Actions 권한(Workflow permissions) 수정
GitHub Actions 스크립트가 수집한 데이터를 자동으로 커밋하고 원격지에 밀어 넣을 수 있도록 권한을 변경합니다.
- **경로**: `Settings` -> `Actions` -> `General`
- **Workflow permissions** 섹션으로 이동하여 **Read and write permissions** 옵션을 체크하여 활성화한 후 **Save** 버튼을 클릭합니다.

GitHub Actions는 자동으로 실행되지 않으며 Gmail 알림에도 관여하지 않습니다.

### 2. Codex 예약 Gmail 알림

ChatGPT/Codex의 **예약** 화면에 3시간 주기의 독립 작업을 설정합니다. 예약 작업은 대학원 게시판을 직접 확인하고, 연결된 Gmail의 기존 발송 기록을 기준으로 아직 알리지 않은 공지만 본인에게 보냅니다. GitHub Actions와 Google Apps Script는 이 과정에 사용되지 않습니다.

---

## ⚡ Vercel 웹 배포 설정 (1분 소요)

Vercel에 본 프로젝트를 완전 무료로 1분 만에 게시할 수 있습니다.

1. [Vercel 공식 홈페이지](https://vercel.com/)에 로그인합니다 (GitHub 계정 연동 권장).
2. Dashboard에서 **Add New...** -> **Project**를 클릭합니다.
3. 생성된 이 GitHub 리포지토리를 찾아 **Import** 버튼을 누릅니다.
4. **Configure Project** 세션에서 다른 설정은 전혀 건드릴 필요 없이 곧바로 **Deploy** 버튼을 누릅니다.
5. 배포가 완료되면 제공되는 고유 서브도메인 주소(예: `http://cje-notice-monitor.vercel.app`)를 통해 전 세계 어디서나 대시보드 화면을 실시간 관제할 수 있습니다.

---

## 🔒 보안 사항

- Gmail 자격증명과 수신 주소는 저장소에 저장하지 않습니다. 메일은 Codex에 연결된 Gmail 권한으로만 발송합니다.
- 과거 커밋에 노출된 텔레그램 봇 토큰은 텔레그램에서 폐기해야 합니다.
