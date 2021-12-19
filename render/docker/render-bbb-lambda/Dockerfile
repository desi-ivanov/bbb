FROM render-bbb


ARG FUNCTION_DIR="/function"

RUN mkdir -p ${FUNCTION_DIR}

RUN cp -r app/* "$FUNCTION_DIR"

RUN pip3 install \
        --target ${FUNCTION_DIR} \
        awslambdaric

WORKDIR ${FUNCTION_DIR}

ENV DEBIAN_FRONTEND=noninteractive

COPY ./entry_script.sh /entry_script.sh

ADD aws-lambda-rie /usr/local/bin/aws-lambda-rie

ENTRYPOINT [ "/entry_script.sh" ]

CMD ["app.handler"]