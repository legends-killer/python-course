#encoding:utf-8

import codecs
import similarity
import json
import time


def test(data):
    #示例句子
    test_data1=[]
    for line in open("./data/file_corpus.txt","r",encoding='utf-8'): #设置文件对象并读取每一行文件
        test_data1.append(line)    
    
    train_data1 = data
    #四种模型
    model_list=['cosine','idf','bm25','jaccard']
    #打开句子集
    file_sentence=codecs.open('./data/file_sentence.txt','r',encoding='utf-8')

    train_data=file_sentence.readlines()
    #计算每种模型的相似度
    for model in model_list:
        t1 = time.time()
        dataset=dict()
        result=dict()
        for s1 in test_data1:
            dataset[s1]=dict()
            for s2 in train_data1:
                s2=s2.strip()
                if s1!=s2:
                    sim=similarity.ssim(s1,s2,model=model)
                    dataset[s1][s2]=dataset[s1].get(s2,0)+sim
        for r in dataset:
            top=sorted(dataset[r].items(),key=lambda x:x[1],reverse=True)
            result[r]=top[0]
        #将结果写入测试结果文件
        with codecs.open('./data/test_result1.txt','a',encoding='utf-8') as f:
            f.write('--------------The result of %s method------------------\n '%model)
            f.write('\tThe computing cost %.3f seconds\n'% (time.time() - t1))
            f.write(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=False))
            f.write('\n\n')

    file_sentence.close()


with open('./data/userExp.txt','r',encoding='utf-8') as f:
    userExp = []
    for line in f:
        userExp.append(line)
    test(userExp)




#