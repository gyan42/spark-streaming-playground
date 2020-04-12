FROM python:3.7

COPY docker/api/requirements.txt /
#RUN apt-get update -y && \
#    apt-get install -y python-pip python-dev
RUN pip install -r /requirements.txt

RUN mkdir /spacy_ner_flask
# We copy just the requirements.txt first to leverage Docker cache
#ADD ./requirements.txt /spacy_ner_flask/requirements.txt
RUN mkdir /spacy_ner_flask/ssp
RUN mkdir /spacy_ner_flask/config
WORKDIR /spacy_ner_flask
ADD src/ssp/ /spacy_ner_flask/ssp/
ADD config/config.ini /spacy_ner_flask/config/

COPY models/en_core_web_sm-2.2.5.tar.gz /spacy_ner_flask/
RUN pip install /spacy_ner_flask/en_core_web_sm-2.2.5.tar.gz
#RUN python -m spacy download en_core_web_sm
ENV PYTHONPATH "${PYTHONPATH}:/spacy_ner_flask"
EXPOSE 5000
CMD ["python", "ssp/flask/api/app.py"]