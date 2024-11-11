FROM pandoc/latex:3.2.0

RUN apk update && \
    apk add openssh-client git && \
    apk add --no-cache bash make gcc g++ python3-dev py3-pip linux-headers && \
    apk add --no-cache graphviz openjdk11 ttf-droid ca-certificates lsb-release xdg-utils wget && \
    pip install psutil --break-system-packages && \
    pip install pandoc-secnos --break-system-packages
 
# Eisvogel latex-template
RUN tlmgr install adjustbox babel-german background bidi collectbox csquotes everypage filehook footmisc footnotebackref \
framed fvextra letltxmacro ly1 mdframed mweights needspace pagecolor sourcecodepro sourcesanspro titling ucharcat ulem \
unicode-math  upquote  xecjk xurl zref koma-script lineno xstring
 
# Getting Eisvogel
ARG EISVOGEL_VERSION=latest
RUN mkdir -p /opt/pandoc/templates && \
    wget -O - https://github.com/Wandmalfarbe/pandoc-latex-template/releases/${EISVOGEL_VERSION}/download/Eisvogel.tar.gz | \
    tar zxvf - -C /opt/pandoc/templates
 
# Install pandoc-crossref
RUN wget https://github.com/lierdakil/pandoc-crossref/releases/download/v0.3.17.1a/pandoc-crossref-Linux.tar.xz &&\
    tar -xf pandoc-crossref-Linux.tar.xz &&\
    mv pandoc-crossref /usr/bin/

# Setting up Plant UML
ARG plantuml_version="1.2024.7"
RUN wget https://github.com/plantuml/plantuml/releases/download/v${plantuml_version}/plantuml-${plantuml_version}.jar -O /opt/plantuml.jar
RUN pip3 install pandoc-plantuml-filter --upgrade pip --break-system-packages 
ENV PLANTUML_BIN="java -jar /opt/plantuml.jar"
 
# Get requirements for mermaid and colored emojis
RUN apk add --no-cache \
      chromium \
      nss \
      freetype \
      harfbuzz \
      ca-certificates \
      ttf-freefont \
      nodejs \
      yarn
 
# Tell Puppeteer to skip installing Chrome. We'll be using the installed package.
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser \
    PATH="/data/node_modules/.bin:${PATH}"
 
# Copy files over from source pc
COPY / /data/

# Get LUA-Filter for vertical tables
RUN curl -O \
    -L https://raw.githubusercontent.com/chrisaga/lua-filters/refs/heads/tables-vrules/tables-vrules/tables-rules.lua
 
WORKDIR /data
RUN yarn add puppeteer@13.5.0 mermaid-filter mermaid.cli --prefix=/app && yarn install --prefix/app
ENV PATH="/app/node_modules/.bin:$PATH"
RUN rm -rf /tmp/*
RUN echo '{"args": ["--no-sandbox", "--disable-setuid-sandbox"]}' > .puppeteer.json
ENTRYPOINT ["/bin/sh", "-c", "python d2ds.py"]