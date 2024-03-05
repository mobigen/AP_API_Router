FROM elasticsearch:7.17.14

RUN elasticsearch-plugin install analysis-nori

RUN touch /usr/share/elasticsearch/config/user_dic.txt
RUN touch /usr/share/elasticsearch/config/stopwords.txt
RUN touch /usr/share/elasticsearch/config/synonyms.txt