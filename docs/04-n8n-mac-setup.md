# n8n Self-hosted — Mac 상시구동 설치 가이드

> 결정: n8n을 Mac에서 Docker로 상시구동. Community Edition(무료), executions 무제한.

## ⚠️ 먼저 확인 — Mac 종류에 따라 안정성 다름
- **Mac mini/iMac(데스크탑, 항상 전원 연결)**: 적합. 그대로 진행.
- **MacBook(노트북)**: 뚜껑 닫으면 sleep으로 n8n 중단됨. 상시구동하려면 전원 연결 + "덮개 닫아도 안 재우기" 설정 또는 외장 디스플레이 연결 상태 유지 필요. 배터리 절전 모드에서도 끊길 수 있음.

## 설치 (Docker Desktop 방식)

### 1. Docker Desktop 설치
```bash
brew install --cask docker
```
설치 후 Docker.app 실행 → **Docker Desktop 환경설정 → General → "Start Docker Desktop when you log in" 체크** (재부팅 후에도 자동 실행되게)

### 2. n8n 작업 폴더 생성
```bash
mkdir -p ~/n8n && cd ~/n8n
```

### 3. docker-compose.yml 작성
```yaml
services:
  n8n:
    image: n8nio/n8n
    container_name: n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - GENERIC_TIMEZONE=Asia/Seoul
      - TZ=Asia/Seoul
    volumes:
      - ~/n8n/data:/home/node/.n8n
```
`restart: always`가 핵심 — Docker Desktop이 재시작되면 n8n 컨테이너도 자동 재시작됨.

### 4. 실행
```bash
docker compose up -d
```
`-d`는 백그라운드 실행(detached). 브라우저에서 `http://localhost:5678` 접속해 초기 계정(이메일/비번) 생성.

### 5. 상시구동 보장 (macOS 설정)
- **시스템 설정 → 잠자기(에너지) → "전원 어댑터 연결 시 디스플레이가 꺼져도 Mac을 깨어있게 유지"** 체크 (Mac mini/iMac)
- Docker Desktop을 로그인 시 자동 실행하도록 설정(위 2번)
- 정전/재부팅 후에도 `restart: always` 덕분에 Docker Desktop만 다시 켜지면 n8n은 자동 복구됨

## 확인
```bash
docker ps            # n8n 컨테이너 Up 상태 확인
docker compose logs -f n8n   # 로그 확인, Ctrl+C로 종료
```

## 참고 — 왜 공인 IP/포트포워딩이 지금은 필요 없나
현재 설계(PLAUD MCP 폴링 방식)는 n8n이 **Cron 트리거로 주기적으로 Plaud MCP에 요청을 보내는 구조**(outbound)라, 외부에서 n8n으로 들어오는 인바운드 웹훅이 필요 없다. `localhost:5678`만으로 충분. (나중에 Slack/카카오톡 등 외부 서비스가 n8n을 직접 호출해야 하는 기능을 추가하면 그때 포트포워딩/터널링이 필요해짐 — 지금은 불필요)

## 다음 액션
- [ ] 사용자: 위 단계대로 Docker + n8n 설치, `localhost:5678` 접속 확인
- [ ] n8n 안에서 MCP Client Tool 노드 추가 → `https://mcp.plaud.ai/mcp` 연결 테스트
