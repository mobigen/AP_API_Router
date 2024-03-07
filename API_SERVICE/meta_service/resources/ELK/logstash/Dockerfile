FROM docker.elastic.co/logstash/logstash:7.15.0

RUN /usr/share/logstash/bin/logstash-plugin install logstash-integration-jdbc
RUN /usr/share/logstash/bin/logstash-plugin install logstash-filter-aggregate
RUN /usr/share/logstash/bin/logstash-plugin install logstash-filter-mutate

COPY postgresql-42.7.0.jar /usr/share/logstash/logstash-core/lib/jars/postgresql.jar
COPY biz_meta.conf /usr/share/logstash/pipeline/biz_meta.conf
COPY v_biz_meta_oversea_els.conf /usr/share/logstash/pipeline/v_biz_meta_oversea_els.conf