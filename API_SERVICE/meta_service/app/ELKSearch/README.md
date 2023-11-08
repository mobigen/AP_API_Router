# ELKSearch

- mapping
  - index 생성에 사용되는 mapping 파일을 저장하는 폴더 
- Utils
  - base.py: document와 index에서 공통적으로 사용되는 util 모듈
- test
  - ELKSearch 모듈을 테스트하기 위한 코드를 저장해 두는 폴더
- ELKSearch
  - config: els 연결에 사용할 설정을 저장해두는 코드
  - model: 검색이나 els 설정에 사용될 데이터 모델을 작성해둔 파일
  - index: elasticsearch의 index를 관리하기 위한 모듈
  - document: index의 데이터를 관리하기 위한 모듈