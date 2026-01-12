# Web Browser Engineering - Chapter 6 Enhancements

## 추가된 기능

### 1. CSS width/height 속성 지원
- **파일**: `layout.py`, `parser.py`
- **기능**: 블록 레이아웃에서 CSS `width`와 `height` 속성을 지원
- **예시**: `<div style="width: 200px; height: 100px;">`
- **구현**:
  - HTML 속성 파서 개선 (따옴표 처리)
  - `parse_pixel_value()` 함수 추가
  - `BlockLayout.layout()` 메서드에서 CSS 크기 속성 적용

### 2. CSS !important 구문 지원
- **파일**: `css.py`
- **기능**: CSS `!important` 선언을 인식하고 우선순위 1000 보너스 부여
- **예시**: `<div style="color: red !important;">`
- **구현**:
  - CSS 파서에서 `!important` 감지
  - 우선순위 기반 스타일 적용 시스템
  - 인라인 스타일 vs 외부 스타일 우선순위 관리

## 우선순위 시스템
```
상속 속성:              0
태그 셀렉터:            1
태그 셀렉터 + !important: 1001
인라인 스타일:         1000
인라인 + !important:   2000
```

## 테스트
- `test.html`: width/height 속성 테스트
- `test_important.html`: !important 구문 테스트