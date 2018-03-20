FROM node:9-alpine

RUN apk add --no-cache git \
    && git clone https://github.com/pentie/ptcoding.git /src/ptcoding \
    && cd /src/ptcoding/redtool \
    && npm install

ENV DEBUG=redtool:* NODE_ENV=production ADDRESS=0.0.0.0 PORT=3000
EXPOSE 3000
WORKDIR /src/ptcoding/redtool
CMD [ "node", "bin/www" ]


