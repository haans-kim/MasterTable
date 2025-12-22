# GitHub 업로드 가이드

## 📤 GitHub에 프로젝트 업로드하기

### 방법 1: GitHub 웹사이트 사용 (권장)

1. **GitHub 로그인**
   - https://github.com 접속
   - 로그인

2. **새 저장소 생성**
   - 우측 상단 "+" 버튼 클릭
   - "New repository" 선택

3. **저장소 설정**
   - Repository name: `2025_CJ_CULTURE_SURVEY`
   - Description: "CJ그룹 컬처서베이 주관식 문항 분석 시스템"
   - Public 또는 Private 선택
   - ✅ Add a README 체크 해제 (이미 있음)
   - "Create repository" 클릭

4. **로컬 저장소 연결 및 푸시**
   ```bash
   # 터미널/명령 프롬프트에서 실행
   cd C:\Project\CJ_Culture

   # 원격 저장소 추가 (YOUR_USERNAME을 실제 GitHub 아이디로 변경)
   git remote add origin https://github.com/YOUR_USERNAME/2025_CJ_CULTURE_SURVEY.git

   # 브랜치 이름 설정
   git branch -M main

   # GitHub에 푸시
   git push -u origin main
   ```

### 방법 2: GitHub Desktop 사용

1. **GitHub Desktop 설치**
   - https://desktop.github.com/ 에서 다운로드

2. **저장소 추가**
   - File → Add Local Repository
   - C:\Project\CJ_Culture 선택

3. **Publish repository**
   - "Publish repository" 버튼 클릭
   - Name: `2025_CJ_CULTURE_SURVEY`
   - Keep this code private 선택/해제
   - "Publish repository" 클릭

### 방법 3: GitHub CLI 사용

1. **GitHub CLI 설치**
   ```bash
   # Windows (winget)
   winget install --id GitHub.cli

   # 또는 https://cli.github.com/ 에서 다운로드
   ```

2. **인증**
   ```bash
   gh auth login
   ```

3. **저장소 생성 및 푸시**
   ```bash
   cd C:\Project\CJ_Culture
   gh repo create 2025_CJ_CULTURE_SURVEY --public --source=. --remote=origin --push
   ```

## ⚠️ 주의사항

### 민감한 데이터 확인
- `주관식 분석 raw data_250929.xlsx` 파일은 .gitignore에 포함되어 있어 업로드되지 않습니다
- 개인정보나 민감한 정보가 포함되어 있는지 확인하세요

### Private 저장소 권장
- 회사 내부 데이터이므로 Private 저장소로 설정을 권장합니다
- Private 저장소는 GitHub 계정당 무료로 제공됩니다

## 📁 현재 Git 상태

```
✅ Git 저장소 초기화 완료
✅ 모든 파일 스테이징 완료
✅ 첫 커밋 완료
⏳ GitHub 푸시 대기 중
```

## 🔗 완료 후 확인사항

1. GitHub 저장소 URL: `https://github.com/YOUR_USERNAME/2025_CJ_CULTURE_SURVEY`
2. README.md가 제대로 표시되는지 확인
3. 민감한 파일이 업로드되지 않았는지 확인

---
*작성일: 2025-09-29*