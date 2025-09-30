# Simulverse 개선 로드맵 🗺️

> **프로젝트**: Metaverse Content Management Framework
> **현재 버전**: v0.1.0
> **목표 버전**: v1.0.0-stable
> **총 예상 기간**: 4-6주

---

## 📋 전체 개요

### 목표
1. **보안 강화**: 인증/권한 취약점 제거
2. **성능 최적화**: 응답 시간 10배 개선 (500ms → 50ms)
3. **아키텍처 현대화**: 확장 가능한 구조 확립
4. **운영 자동화**: CI/CD 및 모니터링 구축

### 진행 상황
```
Priority 1 (즉시):    [ ] 0/5 tasks  (예상: 1.5일)
Priority 2 (단기):    [ ] 0/7 tasks  (예상: 1주)
Priority 3 (중기):    [ ] 0/8 tasks  (예상: 2.5주)
─────────────────────────────────────────────
전체 진행률:           0% (0/20 tasks)
```

---

## 🎯 Phase 1: 즉시 개선 (Week 1)

**목표**: 크리티컬 버그 및 보안 이슈 해결
**기간**: 1-2일
**담당**: Backend Team
**결과물**: v0.2.0-security-fixes

| Task | 파일 | 우선순위 | 상태 |
|------|------|----------|------|
| 1.1 권한 검증 로직 수정 | `routers/space.py:149` | 🔴 Critical | ⏳ Pending |
| 1.2 MongoDB 인덱스 추가 | `manage/create_indexes.py` | 🔴 Critical | ⏳ Pending |
| 1.3 예외 처리 세분화 | `main.py:50` | 🟡 High | ⏳ Pending |
| 1.4 ObjectId 검증 강화 | `routers/*.py` | 🟡 High | ⏳ Pending |
| 1.5 비밀번호 해싱 통일 | `models/`, `libs/` | 🟢 Medium | ⏳ Pending |

**성공 지표**:
- ✅ 권한 우회 취약점 0건
- ✅ 인덱스 적용 후 쿼리 속도 100배 향상
- ✅ 모든 HTTP 상태 코드 적절히 처리

**상세 문서**: [priority-1-immediate.md](.claude/todos/priority-1-immediate.md)

---

## 🚀 Phase 2: 성능 최적화 (Week 2-3)

**목표**: 응답 시간 단축 및 코드 품질 향상
**기간**: 1주
**담당**: Backend + QA Team
**결과물**: v0.3.0-performance

| Task | 주요 기술 | 예상 효과 | 상태 |
|------|-----------|-----------|------|
| 2.1 N+1 쿼리 해결 | Aggregation Pipeline | 응답 10배 빠름 | ⏳ Pending |
| 2.2 Form 클래스 리팩토링 | 상속 패턴 | 코드 40% 감소 | ⏳ Pending |
| 2.3 환경 변수 관리 | Pydantic Settings | 배포 편의성 | ⏳ Pending |
| 2.4 로깅 시스템 | Python logging | 디버깅 효율 | ⏳ Pending |
| 2.5 비동기 최적화 | asyncio.gather | 응답 3배 빠름 | ⏳ Pending |
| 2.6 테스트 환경 구축 | pytest-asyncio | 버그 조기 발견 | ⏳ Pending |
| 2.7 API 응답 표준화 | Pydantic Response | 일관성 확보 | ⏳ Pending |

**성공 지표**:
- ✅ API 평균 응답 시간 < 100ms
- ✅ 테스트 커버리지 60% 이상
- ✅ 코드 중복률 < 5%
- ✅ 로그 기반 에러 추적 100%

**상세 문서**: [priority-2-short-term.md](.claude/todos/priority-2-short-term.md)

---

## 🏗️ Phase 3: 아키텍처 재설계 (Week 3-6)

**목표**: 확장 가능한 시스템 구축
**기간**: 2.5주
**담당**: Full Team
**결과물**: v1.0.0-stable

| Task | 아키텍처 변경 | 비즈니스 가치 | 상태 |
|------|---------------|---------------|------|
| 3.1 의존성 주입 | FastAPI Depends | 테스트 용이성 | ⏳ Pending |
| 3.2 Service 계층 분리 | 3-Tier Architecture | 유지보수성 | ⏳ Pending |
| 3.3 API 버전 관리 | v1/v2 분리 | 하위 호환성 | ⏳ Pending |
| 3.4 캐싱 레이어 | Redis | 성능 20배 향상 | ⏳ Pending |
| 3.5 이벤트 시스템 | Event Bus | 확장성 | ⏳ Pending |
| 3.6 GraphQL API | Strawberry | 유연성 (선택) | ⏳ Optional |
| 3.7 관리자 대시보드 | FastAPI Admin | 운영 효율 | ⏳ Pending |
| 3.8 Docker/CI/CD | GitHub Actions | 자동화 | ⏳ Pending |

**성공 지표**:
- ✅ 캐시 히트율 80% 이상
- ✅ 동시 접속자 100명 처리
- ✅ 테스트 커버리지 80% 이상
- ✅ 자동 배포 파이프라인 구축
- ✅ API 응답 < 50ms (캐시 사용 시 < 5ms)

**상세 문서**: [priority-3-mid-term.md](.claude/todos/priority-3-mid-term.md)

---

## 📊 기술 스택 변화

### Before (현재)
```
FastAPI 0.104 (단순 구조)
├── MongoDB (Motor) - 인덱스 없음
├── JWT 인증 (bcrypt)
└── Jinja2 템플릿

문제점:
- 전역 싱글톤 DB 매니저
- 비즈니스 로직 혼재
- 테스트 불가
- 캐싱 없음
```

### After (목표)
```
FastAPI 0.104+ (계층화 구조)
├── MongoDB (Motor) + 인덱스
├── Redis (캐싱)
├── Service/Repository 계층
├── 의존성 주입
├── GraphQL (선택)
├── Docker + GitHub Actions
└── 관리자 대시보드

개선점:
- 테스트 커버리지 80%
- 응답 시간 10배 개선
- 자동 배포
- 확장 가능한 구조
```

---

## 📈 성능 목표

### 현재 성능
- 공간 조회: ~500ms
- 씬 렌더링: ~800ms (N+1 문제)
- 동시 접속: ~20명
- 테스트 커버리지: 0%

### 목표 성능 (Phase 3 완료 후)
- 공간 조회: **~5ms** (캐시), ~50ms (DB)
- 씬 렌더링: **~80ms** (Aggregation)
- 동시 접속: **~100명**
- 테스트 커버리지: **80%**

**개선율**: 10-20배 향상

---

## 🔄 마일스톤

### v0.2.0 - Security Fixes (Week 1)
```
[  ] 1.1 권한 검증 수정
[  ] 1.2 인덱스 추가
[  ] 1.3 예외 처리 개선
[  ] 1.4 ObjectId 검증
[  ] 1.5 해싱 통일
─────────────────────────
예상 완료: 2025-10-07
```

### v0.3.0 - Performance (Week 2-3)
```
[  ] 2.1 N+1 쿼리 해결
[  ] 2.2-2.5 코드 품질 개선
[  ] 2.6 테스트 환경
[  ] 2.7 API 표준화
─────────────────────────
예상 완료: 2025-10-14
```

### v1.0.0 - Stable (Week 4-6)
```
[  ] 3.1-3.2 아키텍처 재설계
[  ] 3.3-3.4 버전/캐싱
[  ] 3.5-3.7 확장 기능
[  ] 3.8 CI/CD
─────────────────────────
예상 완료: 2025-10-31
```

---

## 👥 팀 역할 분담

### Backend Lead
- Phase 1: 모든 작업 리드
- Phase 2: 2.1, 2.5 (성능 최적화)
- Phase 3: 3.1, 3.2, 3.4 (아키텍처 코어)

### Backend Developer
- Phase 2: 2.2, 2.3, 2.4 (리팩토링)
- Phase 3: 3.3, 3.5, 3.7 (확장 기능)

### QA/DevOps
- Phase 2: 2.6 (테스트)
- Phase 3: 3.8 (CI/CD)

### 선택 (풀스택)
- Phase 3: 3.6 (GraphQL)
- Phase 3: 3.7 (관리자 UI)

---

## ⚠️ 리스크 관리

| 리스크 | 확률 | 영향도 | 대응 방안 |
|--------|------|--------|-----------|
| MongoDB 인덱스 적용 실패 | Low | High | 스테이징 환경 테스트 |
| 캐싱 시 데이터 정합성 문제 | Medium | High | TTL 짧게 설정, 무효화 로직 강화 |
| 의존성 주입 리팩토링 범위 과다 | High | Medium | 단계적 적용, 레거시 코드 병행 |
| CI/CD 파이프라인 구축 지연 | Medium | Low | Phase 3 후반으로 연기 |
| 테스트 작성 시간 부족 | High | High | 핵심 로직 우선 테스트 (60% 목표) |

---

## 📝 주간 체크인 템플릿

```markdown
## Week X 진행 상황 (YYYY-MM-DD)

### 완료된 작업
- [ ] Task X.X: 설명
  - 결과: ...
  - 소요 시간: X시간

### 진행 중 작업
- [ ] Task X.X: 설명
  - 진행률: X%
  - 블로커: ...

### 다음 주 계획
- [ ] Task X.X
- [ ] Task X.X

### 이슈 및 결정사항
- ...

### 메트릭
- 테스트 커버리지: X%
- API 응답 시간: Xms
- 완료 작업: X/20
```

---

## 🎓 학습 리소스

### Priority 1 관련
- [MongoDB 인덱스 최적화](https://docs.mongodb.com/manual/indexes/)
- [FastAPI 예외 처리](https://fastapi.tiangolo.com/tutorial/handling-errors/)

### Priority 2 관련
- [MongoDB Aggregation](https://docs.mongodb.com/manual/aggregation/)
- [Python asyncio 패턴](https://docs.python.org/3/library/asyncio.html)
- [pytest-asyncio 가이드](https://pytest-asyncio.readthedocs.io/)

### Priority 3 관련
- [FastAPI 의존성 주입](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Redis 캐싱 전략](https://redis.io/docs/manual/patterns/)
- [GitHub Actions CI/CD](https://docs.github.com/en/actions)

---

## 📞 연락처 및 문서

- **프로젝트 리포지토리**: `/home/cbchoi/project/simulverse`
- **이슈 트래킹**: GitHub Issues
- **문서**: [README.md](../../README.md)
- **상세 태스크**:
  - [Priority 1](./priority-1-immediate.md)
  - [Priority 2](./priority-2-short-term.md)
  - [Priority 3](./priority-3-mid-term.md)

---

## ✅ 최종 체크리스트

### Phase 1 완료 조건
- [ ] 모든 보안 이슈 해결
- [ ] 인덱스 적용 및 성능 측정
- [ ] 수동 테스트 통과
- [ ] 코드 리뷰 완료
- [ ] v0.2.0 태그 생성

### Phase 2 완료 조건
- [ ] N+1 쿼리 0건
- [ ] 테스트 커버리지 60%+
- [ ] 로그 시스템 운영
- [ ] API 응답 표준화
- [ ] v0.3.0 태그 생성

### Phase 3 완료 조건
- [ ] 의존성 주입 100% 적용
- [ ] Service/Repository 계층 완성
- [ ] 캐시 히트율 80%+
- [ ] CI/CD 파이프라인 작동
- [ ] 테스트 커버리지 80%+
- [ ] Docker 배포 가능
- [ ] v1.0.0 태그 생성
- [ ] 프로덕션 배포

---

**마지막 업데이트**: 2025-09-30
**다음 리뷰**: 2025-10-07 (Week 1 완료 후)
**프로젝트 오너**: @cbchoi
