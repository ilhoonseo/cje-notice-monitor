# 🎓 청주교육대학교 교육전문대학원 공지 모니터링 시스템

> **Cheongju National University of Education Graduate School Announcement Monitoring & Notification System**
>
> 본 프로젝트는 청주교육대학교 교육전문대학원 공지사항 게시판을 주기적으로 모니터링하여 새 공지사항을 감지하면 즉시 이메일로 알림을 보내고, 시스템 가동 상태와 최근 수집된 공지사항 목록을 한눈에 확인할 수 있는 프리미엄 Vercel 상태 페이지 대시보드를 제공합니다.

---

## 🌟 주요 기능

1. **지능형 웹 스크래퍼 (Python)**:
   - 대학원 공지사항 목록 API(`brdList.do`)를 3시간 주기로 자동 요청하여 실시간 공지사항 감지.
   - 중복 방지 로직 및 로컬 스토리지(`data/notices.json`) 연동을 통한 데이터 정합성 유지.
   - 한글 인코딩 자동 복원 및 SSL 인증 오류 회피 처리를 적용한 강력한 내구성.

2. **텔레그램 실시간 즉시 알림 (Telegram Bot API)**:
   - 새로운 공지사항 발견 시 등록된 텔레그램 채팅방으로 즉시 알림 메시지 발송.
   - 가독성 높은 HTML 마크다운 템플릿 메시지로 공지사항 제목, 작성자, 날짜 및 본문 핵심 요약과 게시판 원본 바로가기 링크 제공.
   - 보안을 준수하여 텔레그램 API 정보는 환경 변수(`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`)로 안전하게 관리.

3. **프리미엄 상태 페이지 대시보드 (Vercel)**:
   - **Rich Aesthetics**: 다크 슬레이트 블루 기반의 HSL 컬러 팔레트, 세련된 글래스모피즘(Glassmorphism) 효과, 호버 인터랙션, 맥박이 뛰는 듯한(Pulsating) 실시간 라이브 인디케이터가 적용된 하이엔드 SaaS 스타일 상태 페이지.
   - **실시간 데이터 동기화**: 브라우저 캐시를 무력화하는 `vercel.json` 캐시 컨트롤 및 자바스크립트 캐시 버스터 기법을 활용한 100% 최신 상태 제공.
   - **공지사항 상세 조회 팝업**: 외부 링크 이동 없이 대시보드 내에서 직접 공지사항 내용의 전체 HTML을 깔끔한 모달 창으로 조회하는 프리미엄 확장 편의 기능.

---

## 🛠 기술 스택

- **Back-end & Scraper**: Python 3.x, `requests`, `beautifulsoup4`
- **Front-end Dashboard**: Plain HTML5, Modern Vanilla CSS, Plain JavaScript, FontAwesome Icons, Google Fonts (Inter, Noto Sans KR)
- **Deployment & Hosting**: Vercel (Static Web Server)
- **Automation Cron Job**: GitHub Actions (3-Hour Interval Schedule)

---

## 📂 디렉토리 구조

```text
├── .github/
│   └── workflows/
│       └── scrape.yml      # GitHub Actions 자동 스케줄러 (3시간 주기)
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
텔레그램 발송 기능을 위해 로컬 터미널이나 시스템 환경 변수에 텔레그램 봇 토큰과 대화방 ID(Chat ID)를 제공해야 합니다.

**💡 텔레그램 봇 토큰 & Chat ID 발급 및 확인 방법**:
1. 텔레그램에서 [@BotFather](https://t.me/BotFather)를 검색하여 대화를 시작하고 `/newbot` 명령어를 통해 새 봇을 만듭니다.
2. 봇 생성이 완료되면 제공되는 **봇 API 토큰(HTTP API Token)**을 복사합니다.
3. 생성한 봇 링크를 통해 대방방으로 들어가서 **대화(시작/메시지 발송)**를 시작합니다.
4. 아래 API 주소를 브라우저에 입력하여 최근 업데이트에서 사용자의 **Chat ID**를 확인합니다:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   조회된 JSON 결과 내 `message.chat.id` 항목의 숫자가 사용자의 **Chat ID**입니다.

**로컬 터미널 세션 환경 변수 설정 (PowerShell)**:
```powershell
$env:TELEGRAM_BOT_TOKEN="발급받은_텔레그램_봇_토큰"
$env:TELEGRAM_CHAT_ID="사용자의_텔레그램_CHAT_ID"
```

### 3. 수집 스크립트 1회 강제 실행
로컬 가상환경 내에서 최초로 수집을 수행하여 로컬 데이터베이스 파일(`notices.json`, `status.json`)을 구축합니다.

```bash
python scraper.py
```
> **Note**: 최초 1회 실행 시에는 기존의 모든 공지가 이메일 알림으로 스팸 발송되지 않도록 감지 데이터베이스 초기화(Setup) 기능만 조용히 수행하도록 구현되어 있습니다. 2회차 실행부터 신규 글 감지 시 이메일이 발송됩니다.

### 4. 대시보드 웹서버 실행
상태 대시보드는 정적 웹 어플리케이션으로, 단순 파일 열기 방식이 아닌 로컬 웹 서버 환경에서 로드되어야 `/data/*.json` 리소스를 정상적으로 로드(Fetch)할 수 있습니다.

```bash
# Python 내장 웹서버를 이용해 실행하는 경우
python -m http.server 3000
```
브라우저에서 `http://localhost:3000`에 접속하여 화려하고 세련된 프리미엄 대시보드를 감상하세요!

---

## 🤖 GitHub Actions 자동화 및 배포 설정

3시간마다 주기적으로 공지사항을 감시하고 Vercel 페이지를 갱신하기 위해 GitHub 리포지토리 설정이 필수적입니다.

### 1. 리포지토리 보안 비밀(Secrets) 추가
GitHub 프로젝트 리포지토리로 접속 후 다음 경로에 텔레그램 API 정보를 등록합니다:
- **경로**: `Settings` -> `Secrets and variables` -> `Actions` -> `Repository secrets`
- **추가할 Secrets**:
  - `TELEGRAM_BOT_TOKEN`: 생성한 텔레그램 봇의 HTTP API 토큰 (예: `8848929626:AAH...`)
  - `TELEGRAM_CHAT_ID`: 알림을 수신할 대화방의 Chat ID (예: `8346985929`)

### 2. Actions 권한(Workflow permissions) 수정
GitHub Actions 스크립트가 수집한 데이터를 자동으로 커밋하고 원격지에 밀어 넣을 수 있도록 권한을 변경합니다.
- **경로**: `Settings` -> `Actions` -> `General`
- **Workflow permissions** 섹션으로 이동하여 **Read and write permissions** 옵션을 체크하여 활성화한 후 **Save** 버튼을 클릭합니다.

이제 매 3시간마다 백그라운드에서 스크래퍼가 자동 실행되어 새로운 공지사항 발생 시 이메일을 발송하고, 감지 데이터를 저장소에 커밋하여 Vercel 배포 페이지를 실시간으로 갱신하게 됩니다!

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

- 텔레그램 봇 토큰 및 Chat ID(`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`)는 가급적 리포지토리 소스 코드에 하드코딩하지 않고, 원격 환경(GitHub Actions Secrets 등)에 설정하여 사용하기를 권장합니다.
- GitHub Actions 환경 변수(Secrets)를 이용하여 소중한 API 토큰 정보가 외부에 누출되지 않도록 안전하게 보호하세요.
