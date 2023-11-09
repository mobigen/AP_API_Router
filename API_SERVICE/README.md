## [katech-dev]
- emailAthnCnfm.py
- emailAthnPass.py
- emailAthnSend.py
- emailDataShare.py

## [katech]
dir : ~/common_service/route/v1/email.py

## [개발 및 상용서버 환경설정]
<pre>
service_name = common_service | login_service | meta_service | ...

API_SERVICE/{service_name}/.env

DB_URL=postgresql://{id}:{pwd}@{ip}:{port}/{dbname}
SCHEMA=schema1, schema2, ...
</pre>