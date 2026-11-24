FROM node:20-alpine
WORKDIR /app
COPY server.js mensagens.js ./
ENV NODE_ENV=production
USER node
EXPOSE 3000
CMD ["node", "server.js"]
