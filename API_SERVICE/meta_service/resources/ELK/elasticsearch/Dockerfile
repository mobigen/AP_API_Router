FROM docker.elastic.co/elasticsearch/elasticsearch:7.15.0


RUN elasticsearch-plugin install analysis-nori

RUN touch /usr/share/elasticsearch/config/user_dic.txt
RUN touch /usr/share/elasticsearch/config/stopwords.txt
RUN touch /usr/share/elasticsearch/config/synonyms.txt