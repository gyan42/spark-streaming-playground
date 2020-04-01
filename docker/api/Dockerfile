FROM python:3.7

COPY docker/api/requirements.txt /
#RUN apt-get update -y && \
#    apt-get install -y python-pip python-dev
RUN pip install -r /requirements.txt

RUN mkdir /spacy_ner_flask
# We copy just the requirements.txt first to leverage Docker cache
#ADD ./requirements.txt /spacy_ner_flask/requirements.txt
RUN mkdir /spacy_ner_flask/ssp
RUN mkdir /spacy_ner_flask/ssp/app
RUN mkdir /spacy_ner_flask/ssp/utils
WORKDIR /spacy_ner_flask
ADD src/ssp/utils /spacy_ner_flask/ssp/utils/
ADD src/ssp/flask/api /spacy_ner_flask/ssp/api/
ADD config/config.ini /spacy_ner_flask/

COPY models/en_core_web_sm-2.2.5.tar.gz /spacy_ner_flask/
RUN pip install /spacy_ner_flask/en_core_web_sm-2.2.5.tar.gz
#RUN python -m spacy download en_core_web_sm
ENV PYTHONPATH "${PYTHONPATH}:/spacy_ner_flask"
EXPOSE 5000
CMD ["python", "ssp/api/main.py"]