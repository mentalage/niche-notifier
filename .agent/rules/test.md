---
trigger: always_on
---

모든 작업이 끝나고, 파일이 수정되면 반드시 `tests/` 하위 목록에 test 파일을 추가한 뒤 pytest를 진행한다.

test가 통과하지 못하면, 다시 해당 부분을 참조하여 수정