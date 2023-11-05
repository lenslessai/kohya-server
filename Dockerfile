from ashleykza/kohya:1.6.0

ENV REG_IMG_MAN_DIR /job/input/man/reg/1_man
ENV REG_IMG_WOMAN_DIR /job/input/woman/reg/1_woman

ENV MAN_REG_URL https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/man_4321_imgs_1024x1024px.zip
ENV WOMAN_REG_URL https://huggingface.co/MonsterMMORPG/SECourses/resolve/main/woman_3791_imgs_1024x1024px.zip

RUN mkdir -p $REG_IMG_MAN_DIR
RUN mkdir -p $REG_IMG_WOMAN_DIR

# Install curl and unzip
#RUN apt-get update && apt-get install -y curl unzip

RUN curl -L $MAN_REG_URL -o $REG_IMG_MAN_DIR/man_4321_imgs_1024x1024px.zip && \
    unzip -j -d $REG_IMG_MAN_DIR $REG_IMG_MAN_DIR/man_4321_imgs_1024x1024px.zip && \
    rm $REG_IMG_MAN_DIR/man_4321_imgs_1024x1024px.zip

RUN curl -L $WOMAN_REG_URL -o $REG_IMG_WOMAN_DIR/woman_3791_imgs_1024x1024px.zip && \
    unzip -j -d $REG_IMG_WOMAN_DIR $REG_IMG_WOMAN_DIR/woman_3791_imgs_1024x1024px.zip && \
    rm $REG_IMG_WOMAN_DIR/woman_3791_imgs_1024x1024px.zip

RUN pip install runpod boto3
RUN apt-get update && apt-get install -y python3-opencv
COPY . .
RUN chmod 777 /starter.sh
CMD [ "/starter.sh" ]