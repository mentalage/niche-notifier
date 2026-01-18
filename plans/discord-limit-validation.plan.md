# Discord limit validation plan

- Dicord의 메시지 길이 제한을 확인
- Discord의 Embed 메시지 길이 제한 및 개수 제한을 확인
- 현재의 메시징 구조를 보고, 최소 제한에 따라 limit을 설정(각 주제별 limit 10개)
- 또한 embed 10개 제한을 방지해, 10개 이상이 넘어가게 된다면 여러번 webhook을 호출할 수 있게 구현

## 변경 사항

- 각 주제별 limit이 아닌, 각 rss link별 10개의 기사로 제한
- rss link를 관리하기 위한 database 설정(이후 웹 UI를 통해 관리 가능)

## 2차 변경 사항

- 현재 database에 정상적으로 feed가 저장되고 있는지 확인해보고, 아니라면 수정해줘

## 3차 변경

- 현재 메시지를 보면 embed 나열로만 구성되어 있어서 보기 어려운 것 같아.
- 각 category가 시작될 때, category 이름을 제목으로 하는 embed를 추가하고, 그 아래에 10개의 기사가 나열된 embed를 추가하는 구조로 변경
