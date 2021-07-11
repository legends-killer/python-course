# encoding:utf-8

import codecs
import re

# the method of cutting text to sentence
re_han = re.compile(u"([\u4E00-\u9FD5a-zA-Z0-9+#&\._%]+)")


def get_sentence():
    # 打开对应文件
    file_corpus = codecs.open('./data/file_corpus.txt', 'r', encoding='utf-8')
    file_sentence = codecs.open(
        './data/file_sentence.txt', 'w', encoding='utf-8')

    st = dict()
    for _, line in enumerate(file_corpus):
        line = line.strip()
        blocks = re_han.split(line)
        for blk in blocks:
            if re_han.match(blk) and len(blk) > 10:
                st[blk] = st.get(blk, 0)+1

    st = sorted(st.items(), key=lambda x: x[1], reverse=True)
    # 句子总数
    for s in st:
        file_sentence.write(s[0]+'\n')

    file_corpus.close()
    file_sentence.close()


get_sentence()
