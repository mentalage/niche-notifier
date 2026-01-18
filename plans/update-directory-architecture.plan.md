# Update Directory Architecture

- 현재 루트에 `api`, `src`, `web`이 있는데, `api`와 `web`은 `apps/` 폴더 하위로 옮긴다.
- `src`는 github actions를 위해 그대로 둔다.

## 주의사항

- 프로젝트 구조가 변경되면서, 참조되는 `import`문이 변경되므로, 이를 잘 확인해야 한다.
