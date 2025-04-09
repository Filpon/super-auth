FROM node:22.11.0
WORKDIR /usr/src/app
COPY package.json ./
RUN yarn install
COPY ./src /usr/src/app/src
COPY ./public /usr/src/app/public
RUN yarn build
EXPOSE 3000

CMD ["yarn", "start", "--port", "3000"]
