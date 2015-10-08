FROM centos:latest
MAINTAINER Marcus R. Breese <marcus@breese.com>

RUN yum install -y python-virtualenv make gcc python-devel postgresql-devel postgresql-client && \
    yum clean all && \
    useradd -u 1000 -g 100 -m devop

USER 1000:100
EXPOSE 5000

WORKDIR /srv/genelist

ENV APP_ENV="dev"

CMD [ "/srv/genelist/genelist", "start" ]
